"""Serial communication for the RTN measurement instrument.

Commands are based on the currently provided COMMAND_DECODE.c.
The supplied firmware does not yet implement transient acquisition or data streaming.
"""

import queue
import threading
import time

import serial


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
        """Read line-based UART messages without blocking the GUI thread."""
        while not stop_event.is_set():
            try:
                raw = connection.readline()
            except (serial.SerialException, OSError) as exc:
                if not stop_event.is_set():
                    message = f"Serieller Empfang fehlgeschlagen: {exc}"
                    print(message)
                    self.log_queue.put(("ERROR", message))
                break

            if not raw:
                continue  # read timeout: check stop_event again

            message = raw.decode("ascii", errors="replace").rstrip("\r\n")
            if message:
                print(f"RX <-- {message}")
                self.log_queue.put(("RX", message))

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

    def send_measurement_parameters(
        self, sample_rate, measure_time, points, gate_voltage, drain_voltage
    ):
        """Send the parameters which the current firmware can actually decode.

        In the provided files, Source 1 is provisionally mapped to Gate and
        Source 2 to Drain. Confirm this mapping with the firmware developer.
        Sample rate, measure time and point count are retained for the GUI but
        are NOT sent because COMMAND_DECODE.c has no commands for them yet.
        """
        if not self.connected:
            print("Kein Gerät verbunden!")
            return False

        self.last_parameters = {
            "sample_rate_hz": sample_rate,
            "measure_time_s": measure_time,
            "points": points,
            "gate_voltage_v": gate_voltage,
            "drain_voltage_v": drain_voltage,
       
        }

        commands = [
            f"SOURce1_VOLTage= {gate_voltage:.9g}",
            f"SOURce2_VOLTage= {drain_voltage:.9g}",
            f"SENSE_SAMPLE_RATE= {sample_rate:.9g}",
            f"SENSE_MEASURE_TIME= {measure_time:.9g}",
            f"SENSE_POINTS= {points:.9g}",
            "SENSE_MODE_TRANSIENT= TRUE",
        ]

        for command in commands:
            if not self.send(command):
                return False

        print(
            "NICHT übertragen: Sample Rate, Measure Time und Messpunktanzahl. "
            "Die vorliegenden Firmware-Dateien unterstützen diese Parameter noch nicht."
        )
        return True

    def start_transient(self):
        """Set the transient/measurement flags known to the current decoder.

        This sends control flags only. In the supplied measure.c, transient()
        is currently an empty stub, so this cannot start actual data acquisition yet.
        """
        if not self.connected:
            print("Kein Gerät verbunden!")
            return False

        # Set the measurement flag before enabling transient mode, because
        # main.c calls transient() once sense_mode_transient becomes true.
        if not self.send("SENSE_MODE_MEASUREMENT= START"):
            return False
        if not self.send("SENSE_MODE_TRANSIENT= TRUE"):
            return False

        print(
            "Start-Flags gesendet. Hinweis: transient() ist in der bereitgestellten "
            "Firmware noch leer; es werden daher noch keine Messdaten erfasst."
        )
        return True

    def stop_transient(self):
        """Clear the transient and measurement flags supported by the decoder."""
        if not self.connected:
            print("Kein Gerät verbunden!")
            return False

        ok_transient = self.send("SENSE_MODE_TRANSIENT= FALSE")
        ok_measurement = self.send("SENSE_MODE_MEASUREMENT= STOP")
        return ok_transient and ok_measurement
