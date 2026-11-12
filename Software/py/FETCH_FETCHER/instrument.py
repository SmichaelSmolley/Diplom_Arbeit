"""Serial communication for the RTN measurement instrument.

Commands are based on the currently provided COMMAND_DECODE.c.
The supplied firmware does not yet implement transient acquisition or data streaming.
"""

import queue
import threading
import time

import serial

from messdaten import BlockParser


class Instrument:
    BAUDRATE = 115200  # main.c sets uart1_set_baud(115200)
    COMMAND_DELAY_S = 0.04

    def __init__(self):
        self.connected = False
        self.connection = None
        self.last_parameters = None
        # GUI liest diese Queue regelmäßig aus. Der Empfangsthread greift
        # dadurch nicht direkt auf Tkinter-Widgets zu.
        self.log_queue = queue.Queue()
        self._reader_stop = threading.Event()
        self._reader_thread = None
        # Senden: Lock, damit Sequenz-Thread und ABORT nicht gleichzeitig schreiben
        self._write_lock = threading.Lock()
        self._sending = False
        self._cancel = threading.Event()

    def connect(self, port):
        """Open the instrument's COM port using the baud rate from main.c."""
        port = port.strip()
        if not port:
            print("Bitte einen COM-Port angeben, z. B. COM3.")
            return False

        self.disconnect()

        try:
            self.connection = serial.Serial(
                port=port,
                baudrate=self.BAUDRATE,
                timeout=1,
                write_timeout=1,
            )
            self.connected = True
            self._reader_stop = threading.Event()
            self._reader_thread = threading.Thread(
                target=self._receive_loop,
                args=(self.connection, self._reader_stop),
                name="RTN-serial-reader",
                daemon=True,
            )
            self._reader_thread.start()
            message = f"Serielle Verbindung zu {port} hergestellt ({self.BAUDRATE} Baud)."
            print(message)
            self.log_queue.put(("SYSTEM", message))
            self.log_queue.put((
                "SYSTEM",
                "Empfang aktiv. Eingehende UART-Zeilen erscheinen hier; eine Antwort auf jeden Befehl sendet die Firmware derzeit nicht.",
            ))
            return True
        except (serial.SerialException, ValueError) as exc:
            self.connection = None
            self.connected = False
            print(f"Verbindung zu {port} fehlgeschlagen: {exc}")
            return False

    def disconnect(self):
        """Stop the reader thread and close the serial connection."""
        self.connected = False
        stop_event = self._reader_stop
        stop_event.set()

        connection = self.connection
        self.connection = None
        if connection is not None:
            try:
                if connection.is_open:
                    connection.close()
            except (serial.SerialException, OSError) as exc:
                message = f"Fehler beim Schließen der Verbindung: {exc}"
                print(message)
                self.log_queue.put(("SYSTEM", message))

        reader = self._reader_thread
        if reader is not None and reader.is_alive() and reader is not threading.current_thread():
            reader.join(timeout=0.5)
        self._reader_thread = None

    def _receive_loop(self, connection, stop_event):
        """UART lesen, ohne die GUI zu blockieren.

        Textzeilen -> ("RX", text). Datenblöcke (#HDR … binär … #END, siehe
        Datenformat_Rueckgabe.md) -> ("BLOCK", (header, rohwerte)).
        """
        parser = BlockParser()
        while not stop_event.is_set():
            try:
                data = connection.read(connection.in_waiting or 1)
            except (serial.SerialException, OSError) as exc:
                if not stop_event.is_set():
                    message = f"Serieller Empfang fehlgeschlagen: {exc}"
                    print(message)
                    self.log_queue.put(("ERROR", message))
                break

            if not data:
                continue  # read timeout: check stop_event again

            for event in parser.feed(data):
                kind = event[0]
                if kind == "LINE":
                    print(f"RX <-- {event[1]}")
                    self.log_queue.put(("RX", event[1]))
                elif kind == "BLOCK":
                    hdr, raw = event[1], event[2]
                    self.log_queue.put(("RX", f"Datenblock {hdr['TYPE']} N={hdr['N']} "
                                              f"CYCLE={hdr['CYCLE']} (Prüfsumme OK)"))
                    self.log_queue.put(("BLOCK", (hdr, raw)))
                elif kind == "DONE":
                    self.log_queue.put(("RX", "#DONE"))
                else:
                    self.log_queue.put(("ERROR", event[1]))

    def send(self, command):
        """Send one newline-terminated command accepted by COMMAND_DECODE.c.

        The provided firmware uses line-based receive functions, and emits CRLF
        for its startup banner. The UART driver itself was not provided, so the
        exact command terminator should be confirmed with the firmware developer.
        """
        if not self.connected or self.connection is None:
            print("Kein Gerät verbunden!")
            return False

        command = command.strip()
        if "\r" in command or "\n" in command:
            print("Befehl darf keine Zeilenumbrüche enthalten.")
            return False

        try:
            payload = (command + "\r\n").encode("ascii")
            with self._write_lock:
                self.connection.write(payload)
                self.connection.flush()
            print(f"TX --> {command}")
            self.log_queue.put(("TX", command))
            # Give the firmware main loop time to consume one command before
            # sending the next; there is currently no ACK command in the decoder.
            time.sleep(self.COMMAND_DELAY_S)
            return True
        except (serial.SerialException, UnicodeEncodeError) as exc:
            print(f"Senden fehlgeschlagen: {exc}")
            return False

    # ------------------------------------------------------------------
    # Befehlsfolgen senden (laut Befehlsreferenz_Python_PC.md)
    # ------------------------------------------------------------------
    @property
    def busy(self):
        return self._sending

    def send_sequence(self, commands, tag=""):
        """Sendet die Befehle nacheinander in einem Hintergrund-Thread.

        Zwischen den Befehlen wartet send() COMMAND_DELAY_S, damit die
        Firmware jede Zeile abholen kann (Befehlsreferenz Kap. 2.1).
        Am Ende kommt ("DONE", (tag, ok, anzahl_gesendet)) in die log_queue.
        Gibt False zurück, wenn gerade schon gesendet wird.
        """
        if self._sending or not self.connected:
            return False
        self._sending = True
        self._cancel.clear()

        def worker():
            sent = 0
            ok = True
            for command in commands:
                if self._cancel.is_set():
                    ok = False
                    break
                if not self.send(command):
                    ok = False
                    break
                sent += 1
            self._sending = False
            self.log_queue.put(("DONE", (tag, ok, sent, len(commands))))

        threading.Thread(target=worker, name="FETCH-sender", daemon=True).start()
        return True

    def abort(self):
        """ABORT sofort senden (wird in der Firmware direkt im UART-Interrupt
        erkannt) und eine eventuell laufende Befehlsfolge abbrechen."""
        self._cancel.set()
        return self.send("ABORT")
