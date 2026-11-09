import queue
from datetime import datetime

import customtkinter as ctk
from serial.tools import list_ports

from instrument import Instrument


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.instrument = Instrument()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("RTN Measurement")
        self.geometry("1020x720")
        self.minsize(900, 620)

        self.grid_columnconfigure(0, weight=1, minsize=290)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar: connection
        self.sidebar = ctk.CTkFrame(self)
        self.sidebar.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")

        ctk.CTkLabel(
            self.sidebar,
            text="RTN Measurement Software",
            font=("Arial", 22, "bold"),
            wraplength=250,
        ).pack(padx=12, pady=(22, 18))

        self.connection_status = ctk.CTkLabel(
            self.sidebar, text="Status: Nicht verbunden", wraplength=250
        )
        self.connection_status.pack(padx=12, pady=8)

        # COM-Port-Auswahl mit Aktualisieren-Button
        port_row = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        port_row.pack(fill="x", padx=18, pady=8)
        port_row.grid_columnconfigure(0, weight=1)

        self._port_lookup = {}
        self.port_dropdown = ctk.CTkComboBox(
            port_row,
            values=["Keine COM-Ports gefunden"],
            state="readonly",
        )
        self.port_dropdown.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        ctk.CTkButton(
            port_row,
            text="Aktualisieren",
            command=self.aktualisiere_com_ports,
            width=100,
        ).grid(row=0, column=1, sticky="ew")

        # Beim Start nach verfügbaren seriellen Schnittstellen suchen.
        self.aktualisiere_com_ports()

        ctk.CTkButton(
            self.sidebar, text="Verbinden", command=self.verbinden
        ).pack(fill="x", padx=18, pady=(8, 6))

        ctk.CTkButton(
            self.sidebar, text="Trennen", command=self.trennen, fg_color="gray"
        ).pack(fill="x", padx=18, pady=6)

        ctk.CTkLabel(
            self.sidebar,
            text=(
                "Serielle Einstellungen\n"
                "115200 Baud, 8 Datenbits, keine Parität, 1 Stopbit"
            ),
            text_color="gray",
            justify="left",
        ).pack(padx=18, pady=12, anchor="w")

        # Main area
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=3)
        self.main_frame.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            self.main_frame,
            text="Transientenanalyse",
            font=("Arial", 22, "bold"),
        ).grid(row=0, column=0, padx=15, pady=(15, 8))

        params = ctk.CTkFrame(self.main_frame)
        params.grid(row=1, column=0, padx=15, pady=8, sticky="ew")
        for col in range(4):
            params.grid_columnconfigure(col, weight=1)

        # Inputs
        self.sample_rate_entry = self._add_entry(
            params, "Sample Rate (Hz)", 0, 0, "1000"
        )
        self.measure_time_entry = self._add_entry(
            params, "Measure Time (s)", 0, 2, "10"
        )
        self.points_entry = self._add_entry(
            params, "Messpunktanzahl", 1, 0, "10000"
        )
        # Provisional mapping: source 1 = Gate and source 2 = Drain. Confirm with firmware developer.
        self.gate_voltage_entry = self._add_entry(
            params, "Gate-Spannung / Source 1 (V)", 1, 2, "0"
        )
        self.drain_voltage_entry = self._add_entry(
            params, "Drain-Spannung / Source 2 (V)", 2, 0, "0.1"
        )

        # Keep the three time/sampling controls mutually consistent.
        self.sample_rate_entry.bind("<KeyRelease>", self.update_points)
        self.measure_time_entry.bind("<KeyRelease>", self.update_points)
        self.points_entry.bind("<KeyRelease>", self.update_measure_time)

        controls = ctk.CTkFrame(params, fg_color="transparent")
        controls.grid(row=3, column=0, columnspan=4, padx=8, pady=(12, 8), sticky="ew")
        for col in range(3):
            controls.grid_columnconfigure(col, weight=1)

        ctk.CTkButton(
            controls, text="Parameter senden", command=self.parameter_senden
        ).grid(row=0, column=0, padx=5, pady=4, sticky="ew")
        ctk.CTkButton(
            controls, text="Messung starten", command=self.messung_starten
        ).grid(row=0, column=1, padx=5, pady=4, sticky="ew")
        ctk.CTkButton(
            controls, text="Messung stoppen", command=self.messung_stoppen,
            fg_color="#8a4545", hover_color="#713838"
        ).grid(row=0, column=2, padx=5, pady=4, sticky="ew")

        self.action_status = ctk.CTkLabel(
            params,
            text="Bereit. Firmware unterstützt aktuell noch keine vollständige Transientenmessung.",
            wraplength=650,
            justify="left",
        )
        self.action_status.grid(row=4, column=0, columnspan=4, padx=10, pady=(4, 12), sticky="w")

        # Data display placeholder: current provided firmware sends no measurement samples.
        self.plot_frame = ctk.CTkFrame(self.main_frame)
        self.plot_frame.grid(row=2, column=0, padx=15, pady=(8, 15), sticky="nsew")
        self.plot_frame.grid_columnconfigure(0, weight=1)
        self.plot_frame.grid_rowconfigure(0, weight=1)
        ctk.CTkLabel(
            self.plot_frame,
            text=(
                "Messdiagramm\n\n"
                "Die Firmware muss die Transientenmessung implementieren und\n"
                "Messdaten über UART zurücksenden, bevor hier Messkurven erscheinen."
            ),
            justify="center",
            text_color="gray",
        ).grid(row=0, column=0, padx=20, pady=20)

        # Live-Protokoll: empfangene UART-Zeilen und gesendete Befehle.
        self.communication_frame = ctk.CTkFrame(self.main_frame)
        self.communication_frame.grid(
            row=3, column=0, padx=15, pady=(0, 15), sticky="nsew"
        )
        self.communication_frame.grid_columnconfigure(0, weight=1)
        self.communication_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self.communication_frame,
            text="Serielle Kommunikation (TX = gesendet, RX = vom Gerät empfangen)",
            font=("Arial", 14, "bold"),
        ).grid(row=0, column=0, padx=10, pady=(8, 4), sticky="w")

        self.communication_log = ctk.CTkTextbox(
            self.communication_frame,
            height=125,
            wrap="word",
        )
        self.communication_log.grid(
            row=1, column=0, padx=10, pady=(0, 10), sticky="nsew"
        )
        self.communication_log.insert(
            "end",
            "Hier erscheinen UART-Nachrichten, sobald das Gerät sie sendet.\n"
            "Die vorliegende Firmware bestätigt nicht jeden Befehl automatisch.\n",
        )
        self.communication_log.configure(state="disabled")

        self.protocol("WM_DELETE_WINDOW", self.beenden)
        self.after(100, self.process_communication_log)

    @staticmethod
    def _add_entry(parent, label_text, row, col, default_value):
        ctk.CTkLabel(parent, text=label_text).grid(
            row=row, column=col, padx=(10, 6), pady=8, sticky="w"
        )
        entry = ctk.CTkEntry(parent)
        entry.grid(row=row, column=col + 1, padx=(4, 10), pady=8, sticky="ew")
        entry.insert(0, default_value)
        return entry

    @staticmethod
    def _read_float(entry):
        return float(entry.get().strip().replace(",", "."))

    def update_points(self, _event=None):
        try:
            rate = self._read_float(self.sample_rate_entry)
            measure_time = self._read_float(self.measure_time_entry)
            if not (1 <= rate <= 100000) or measure_time <= 0:
                return
            points = max(1, round(rate * measure_time))
            self.points_entry.delete(0, "end")
            self.points_entry.insert(0, str(points))
        except (ValueError, TypeError):
            # Ignore incomplete input while the user is editing a field.
            return

    def update_measure_time(self, _event=None):
        try:
            rate = self._read_float(self.sample_rate_entry)
            points = int(self.points_entry.get().strip())
            if not (1 <= rate <= 100000) or points <= 0:
                return
            measure_time = points / rate
            self.measure_time_entry.delete(0, "end")
            self.measure_time_entry.insert(0, f"{measure_time:.9g}")
        except (ValueError, TypeError):
            return

    def read_parameters(self):
        sample_rate = self._read_float(self.sample_rate_entry)
        measure_time = self._read_float(self.measure_time_entry)
        points_text = self.points_entry.get().strip()
        points = int(points_text)
        gate_voltage = self._read_float(self.gate_voltage_entry)
        drain_voltage = self._read_float(self.drain_voltage_entry)

        if not 1 <= sample_rate <= 100000:
            raise ValueError("Sample Rate muss zwischen 1 Hz und 100000 Hz liegen.")
        if measure_time <= 0:
            raise ValueError("Measure Time muss größer als 0 sein.")
        if points <= 0:
            raise ValueError("Die Messpunktanzahl muss größer als 0 sein.")
        return sample_rate, measure_time, points, gate_voltage, drain_voltage

    def aktualisiere_com_ports(self):
        """Refresh the drop-down with currently available serial ports."""
        selected_before = self.port_dropdown.get().strip()
        ports = list(list_ports.comports())

        labels = []
        self._port_lookup = {}
        for port_info in ports:
            device = port_info.device
            description = (port_info.description or "").strip()
            label = f"{device} — {description}" if description and description.lower() != "n/a" else device
            labels.append(label)
            self._port_lookup[label] = device

        if labels:
            self.port_dropdown.configure(values=labels)
            if selected_before in self._port_lookup:
                self.port_dropdown.set(selected_before)
            else:
                self.port_dropdown.set(labels[0])
            if not self.instrument.connected:
                self.connection_status.configure(
                    text=f"Status: Nicht verbunden ({len(labels)} COM-Port(s) gefunden)"
                )
            if hasattr(self, "action_status"):
                self.action_status.configure(text=f"Gefundene COM-Ports: {len(labels)}")
            print("Gefundene COM-Ports:", ", ".join(self._port_lookup.values()))
        else:
            message = "Keine COM-Ports gefunden"
            self._port_lookup = {}
            self.port_dropdown.configure(values=[message])
            self.port_dropdown.set(message)
            if not self.instrument.connected:
                self.connection_status.configure(text="Status: Kein COM-Port gefunden")
            if hasattr(self, "action_status"):
                self.action_status.configure(
                    text="Kein COM-Port gefunden. Gerät anschließen und Aktualisieren drücken."
                )
            print(message)

    def verbinden(self):
        selected_label = self.port_dropdown.get().strip()
        port = self._port_lookup.get(selected_label)
        if not port:
            self.connection_status.configure(text="Status: Bitte einen verfügbaren COM-Port auswählen")
            self.action_status.configure(
                text="Keine gültige COM-Schnittstelle ausgewählt. Aktualisiere die Liste nach dem Anschließen."
            )
            return

        if self.instrument.connect(port):
            self.connection_status.configure(text=f"Status: Verbunden ({port})")
            self.action_status.configure(
                text="COM geöffnet. Die Firmware bestätigt angenommene Befehle derzeit nicht."
            )
        else:
            self.connection_status.configure(text="Status: Verbindung fehlgeschlagen")
            self.action_status.configure(text="COM-Port prüfen und sicherstellen, dass kein anderes Programm ihn verwendet.")

    def trennen(self):
        self.instrument.disconnect()
        self.connection_status.configure(text="Status: Nicht verbunden")
        self.action_status.configure(text="Serielle Verbindung geschlossen.")

    def parameter_senden(self):
        if not self.instrument.connected:
            self.action_status.configure(text="Bitte zuerst den COM-Port verbinden.")
            return False
        try:
            sample_rate, measure_time, points, gate_voltage, drain_voltage = self.read_parameters()
        except (ValueError, TypeError) as exc:
            self.action_status.configure(text=f"Ungültige Eingabe: {exc}")
            return False

        ok = self.instrument.send_measurement_parameters(
            sample_rate, measure_time, points, gate_voltage, drain_voltage
        )
        if ok:
            self.action_status.configure(
                text=(
                    "Spannungswerte wurden über UART geschrieben (Source 1 = Gate und "
                    "Source 2 = Drain sind noch zu bestätigen). Sample Rate, Measure Time "
                    "und Messpunktanzahl werden von der vorliegenden Firmware noch nicht verarbeitet."
                )
            )
            return True
        self.action_status.configure(text="Fehler beim Senden. Details stehen im Terminal.")
        return False

    def messung_starten(self):
        if not self.instrument.connected:
            self.action_status.configure(text="Bitte zuerst den COM-Port verbinden.")
            return

        # First transmit the voltage values currently supported by COMMAND_DECODE.c.
        if not self.parameter_senden():
            return

        ok = self.instrument.start_transient()
        if ok:
            self.action_status.configure(
                text=(
                    "Start-Flags gesendet, aber noch keine echte Messung: Die mitgelieferte "
                    "measure.c enthält eine leere transient()-Funktion und sendet keine Messdaten zurück."
                )
            )

    def messung_stoppen(self):
        if not self.instrument.connected:
            self.action_status.configure(text="Bitte zuerst den COM-Port verbinden.")
            return
        if self.instrument.stop_transient():
            self.action_status.configure(text="Stop-Flags gesendet. Eine Bestätigung der Firmware gibt es derzeit nicht.")
        else:
            self.action_status.configure(text="Fehler beim Senden der Stop-Flags.")

    def process_communication_log(self):
        """Move queued serial log messages into the GUI on Tk's main thread."""
        try:
            while True:
                kind, message = self.instrument.log_queue.get_nowait()
                timestamp = datetime.now().strftime("%H:%M:%S")
                labels = {
                    "TX": "TX →",
                    "RX": "RX ←",
                    "SYSTEM": "INFO",
                    "ERROR": "FEHLER",
                }
                label = labels.get(kind, kind)

                self.communication_log.configure(state="normal")
                self.communication_log.insert(
                    "end", f"[{timestamp}] {label}: {message}\n"
                )
                self.communication_log.see("end")
                self.communication_log.configure(state="disabled")

                if kind == "ERROR":
                    self.connection_status.configure(text="Status: Empfangsfehler")
                    self.action_status.configure(text=message)
        except queue.Empty:
            pass

        # Polling keeps all Tkinter widget updates on the GUI thread.
        self.after(100, self.process_communication_log)

    def beenden(self):
        self.instrument.disconnect()
        self.destroy()
