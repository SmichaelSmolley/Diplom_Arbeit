import queue
import sys
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, ttk

import customtkinter as ctk
from serial.tools import list_ports

from instrument import Instrument
import scpi_commands
import dateinamen
import messinfo
import messdaten
import vorverarbeitung
import math

# ----------------------------------------------------------------------
# Pfade, die auch in der .exe (PyInstaller) funktionieren:
#   RESOURCE_DIR = mitgelieferte Dateien (Farbschemata)
#                  in der .exe: entpackter Temp-Ordner sys._MEIPASS
#   APP_DIR      = Ordner, in dem gui.py bzw. die .exe liegt
#                  -> dort landet der Ordner "messungen"
# ----------------------------------------------------------------------
if getattr(sys, "frozen", False):
    RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    APP_DIR = Path(sys.executable).resolve().parent
else:
    RESOURCE_DIR = Path(__file__).resolve().parent
    APP_DIR = RESOURCE_DIR
MEASUREMENT_DIR = APP_DIR / "messungen"


class App(ctk.CTk):
    TAB_NAMES = ("ID-VG", "Transient", "Stress", "MSM", "Temperatur")
    MODE_NAMES = ("Messung durchführen", "Messung auswerten", "Serielle Konsole")
    SIDEBAR_WIDTH = 330
    EVAL_SIDEBAR_WIDTH = 560     # breiter, damit lange Dateinamen ganz sichtbar sind
    MUTED = "gray"
    SECONDARY = "gray"
    FONT = "Arial"

    def __init__(self, retro=False):
        # Design muss VOR dem Erzeugen des Fensters gesetzt werden.
        # Ein Farbschema (qt_theme.json): Hell = Stil einer Qt-Messsoftware,
        # Dunkel = ursprüngliches CustomTkinter-Design ("blue").
        # Umgeschaltet wird zur Laufzeit mit dem Button oben rechts.
        # retro=True (main_retro.py / --retro): startet hell.
        self.retro = retro
        # Farben als (hell, dunkel) – passen sich beim Umschalten automatisch an
        App.MUTED = ("#6A6A6A", "gray60")          # Hinweistexte
        App.SECONDARY = ("#F6F6F6", "gray")      # Neben-Buttons
        App.FONT = "Segoe UI"
        App.SELECT = ("#CDE3F5", "#1F6AA5")         # markierte Datei / Vorschlag
        App.HEADER = ("#ECECEC", "gray25")         # Abschnitts-Köpfe
        # Stopp-Button: normaler Button mit roter Schrift
        App.DANGER = {"fg_color": ("#F6F6F6", "#8a4545"),
                      "hover_color": ("#FBE9E9", "#713838"),
                      "text_color": ("#B00020", "#DCE4EE")}
        ctk.set_default_color_theme(str(RESOURCE_DIR / "qt_theme.json"))
        ctk.set_appearance_mode("light" if retro else self._load_theme_mode())

        super().__init__()

        self.instrument = Instrument()

        self.title("RTN Measurement")
        self.geometry("1150x800")
        self.minsize(950, 650)

        # Spalte 0 = Sidebar mit fester Breite (Messen und Auswerten gleich),
        # Spalte 1 = Hauptbereich, nimmt den restlichen Platz.
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        # Zeile 0 = Umschalter Messen/Auswerten, Zeile 1 = Inhalt
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # Obere Leiste: Modus-Umschalter
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="ew")
        top_bar.grid_columnconfigure(0, weight=1)

        self.mode_bar = ctk.CTkSegmentedButton(
            top_bar,
            values=list(self.MODE_NAMES),
            command=self._show_mode,
            height=42,
            font=(App.FONT, 16, "bold"),
            dynamic_resizing=False,
        )
        self.mode_bar.grid(row=0, column=0, sticky="ew")

        # Umschalter Hell / Dunkel
        self.theme_button = ctk.CTkButton(
            top_bar, text="", width=130, height=42, font=(App.FONT, 15, "bold"),
            command=self._toggle_theme,
        )
        self.theme_button.grid(row=0, column=1, padx=(10, 0))
        self._update_theme_button()


        # ==============================================================
        # Linke Seite: oben Verbindung, unten Kommunikations-Log
        # ==============================================================
        self.sidebar = ctk.CTkFrame(self, fg_color="transparent", width=self.SIDEBAR_WIDTH)
        self.sidebar.grid_propagate(False)  # Breite fest, nicht vom Inhalt abhängig
        self.sidebar.grid(row=1, column=0, padx=(10, 5), pady=10, sticky="nsew")
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(1, weight=1)

        connection_box = ctk.CTkFrame(self.sidebar)
        connection_box.grid(row=0, column=0, pady=(0, 5), sticky="nsew")

        ctk.CTkLabel(
            connection_box,
            text="RTN Measurement Software",
            font=(App.FONT, 22, "bold"),
            wraplength=260,
        ).pack(padx=12, pady=(18, 12))

        self.connection_status = ctk.CTkLabel(
            connection_box, text="Status: Nicht verbunden", wraplength=260
        )
        self.connection_status.pack(padx=12, pady=6)

        # COM-Port-Auswahl mit Aktualisieren-Button
        port_row = ctk.CTkFrame(connection_box, fg_color="transparent")
        port_row.pack(fill="x", padx=18, pady=6)
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
            connection_box, text="Verbinden", command=self.verbinden
        ).pack(fill="x", padx=18, pady=(8, 6))

        ctk.CTkButton(
            connection_box, text="Trennen", command=self.trennen, fg_color=App.SECONDARY
        ).pack(fill="x", padx=18, pady=6)

        ctk.CTkLabel(
            connection_box,
            text="115200 Baud, 8N1",
            text_color=App.MUTED,
        ).pack(padx=18, pady=(6, 2), anchor="w")

        self.action_status = ctk.CTkLabel(
            connection_box, text="", wraplength=280, justify="left", text_color=App.MUTED
        )
        self.action_status.pack(padx=18, pady=(0, 12), anchor="w")

        # Live-Protokoll: empfangene UART-Zeilen und gesendete Befehle.
        self.communication_frame = ctk.CTkFrame(self.sidebar)
        self.communication_frame.grid(row=1, column=0, pady=(5, 0), sticky="nsew")
        self.communication_frame.grid_columnconfigure(0, weight=1)
        self.communication_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self.communication_frame,
            text="Serielle Kommunikation",
            font=(App.FONT, 14, "bold"),
        ).grid(row=0, column=0, padx=10, pady=(8, 4), sticky="w")

        self.communication_log = ctk.CTkTextbox(
            self.communication_frame,
            wrap="word",
        )
        self.communication_log.grid(
            row=1, column=0, padx=10, pady=(0, 10), sticky="nsew"
        )
        self.communication_log.insert(
            "end",
            "TX = gesendet, RX = vom Gerät empfangen.\n"
            "Die Firmware bestätigt Befehle derzeit nicht.\n",
        )
        self.communication_log.configure(state="disabled")

        # ==============================================================
        # Rechte Seite: Reiterleiste oben über die volle Breite,
        # darunter der Inhalt des gewählten Reiters.
        # ==============================================================
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=1, padx=(5, 10), pady=10, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.tab_bar = ctk.CTkSegmentedButton(
            self.main_frame,
            values=list(self.TAB_NAMES),
            command=self._show_tab,
            height=38,
            font=(App.FONT, 15, "bold"),
            dynamic_resizing=False,
        )
        self.tab_bar.grid(row=0, column=0, padx=0, pady=0, sticky="ew")

        self.tab_frames = {}
        for name in self.TAB_NAMES:
            frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
            frame.grid_columnconfigure(0, weight=1)
            # Zeile 0 = Parameter, Zeile 1 = Datei, Zeile 2 = Diagramm
            frame.grid_rowconfigure(2, weight=1)
            self.tab_frames[name] = frame

        self.tab_status = {}
        self._build_idvg_tab(self.tab_frames["ID-VG"])
        self._build_stress_tab(self.tab_frames["Stress"])
        self._build_msm_tab(self.tab_frames["MSM"])
        self._build_temp_tab(self.tab_frames["Temperatur"])
        self._build_transient_tab(self.tab_frames["Transient"])

        # Bei jeder Messart: Speicherdatei (.h5) wählen.
        self.save_path_entries = {}
        self.device_entries = {}
        for name in self.TAB_NAMES:
            self._add_file_row(self.tab_frames[name], name)

        self.tab_bar.set("Transient")
        self._show_tab("Transient")

        # Ansicht "Messung auswerten" (vorerst nur Oberfläche)
        self._build_evaluation_view()

        # Ansicht "Serielle Konsole": Befehle selbst eingeben, mit Autofill
        self._build_console_view()

        self.mode_bar.set(self.MODE_NAMES[0])
        self._show_mode(self.MODE_NAMES[0])

        self.protocol("WM_DELETE_WINDOW", self.beenden)
        self.after(100, self.process_communication_log)

    # ------------------------------------------------------------------
    # Hell / Dunkel umschalten (Auswahl wird gemerkt)
    # ------------------------------------------------------------------
    SETTINGS_FILE = APP_DIR / "fetch_einstellungen.json"

    @classmethod
    def _load_theme_mode(cls):
        try:
            import json
            mode = json.loads(cls.SETTINGS_FILE.read_text(encoding="utf-8")).get("theme", "dark")
            return mode if mode in ("light", "dark") else "dark"
        except (OSError, ValueError):
            return "dark"

    def _save_theme_mode(self, mode):
        try:
            import json
            self.SETTINGS_FILE.write_text(json.dumps({"theme": mode}), encoding="utf-8")
        except OSError:
            pass                      # nicht schlimm, dann gilt beim nächsten Start "dunkel"

    def _toggle_theme(self):
        mode = "light" if ctk.get_appearance_mode() == "Dark" else "dark"
        ctk.set_appearance_mode(mode)
        self._style_tree()
        self._stripe_tree()
        self._update_theme_button()
        self._save_theme_mode(mode)
        if self._last_view is not None:
            self._redraw_plot()          # Diagrammfarben an Hell/Dunkel anpassen

    def _update_theme_button(self):
        dark = ctk.get_appearance_mode() == "Dark"
        self.theme_button.configure(text="☀  Hell" if dark else "☾  Dunkel")

    # ------------------------------------------------------------------
    # Umschaltung Messung durchführen / Messung auswerten
    # ------------------------------------------------------------------
    def _show_mode(self, mode):
        """Messen: Sidebar + Reiter. Auswerten: eigene Sidebar + Diagramm.
        Konsole: Sidebar (Verbindung) + Konsole."""
        views = {
            self.MODE_NAMES[0]: (self.sidebar, self.main_frame),
            self.MODE_NAMES[1]: (self.eval_side, self.eval_plot),
            self.MODE_NAMES[2]: (self.sidebar, self.console_frame),
        }
        visible = views[mode]
        for widgets in views.values():
            for widget in widgets:
                if widget not in visible:
                    widget.grid_remove()
        for widget in visible:
            widget.grid()
        if mode == self.MODE_NAMES[2]:
            self.console_entry.focus_set()
        else:
            self._hide_suggestions()

    def _show_eval_tab(self, name):
        self.eval_tab_frames[name].tkraise()

    def _build_evaluation_view(self):
        """Ansicht zum Auswerten gespeicherter .h5-Messungen.

        Sidebar und Diagramm liegen in denselben Grid-Spalten wie beim Messen,
        dadurch ist die Sidebar in beiden Ansichten gleich breit.
        """
        # ---- Links: Reiter "Dateien" | "Einstellungen" ----
        side = ctk.CTkFrame(self, width=self.EVAL_SIDEBAR_WIDTH)
        side.grid(row=1, column=0, padx=(10, 5), pady=10, sticky="nsew")
        side.grid_propagate(False)
        side.grid_columnconfigure(0, weight=1)
        side.grid_rowconfigure(1, weight=1)  # Inhalt des gewählten Reiters
        self.eval_side = side

        self.EVAL_TABS = ("Dateien", "Einstellungen", "ΔVth")
        self.eval_tab_bar = ctk.CTkSegmentedButton(
            side,
            values=list(self.EVAL_TABS),
            command=self._show_eval_tab,
            height=34,
            font=(App.FONT, 14, "bold"),
            dynamic_resizing=False,
        )
        self.eval_tab_bar.grid(row=0, column=0, padx=0, pady=0, sticky="ew")

        self.eval_tab_frames = {}
        for name in self.EVAL_TABS:
            frame = ctk.CTkFrame(side, fg_color="transparent")
            frame.grid(row=1, column=0, sticky="nsew")
            frame.grid_columnconfigure(0, weight=1)
            self.eval_tab_frames[name] = frame

        # ======== Reiter "Dateien": Ordner + Baumansicht (wie Qt-Dateibrowser) ========
        files_tab = self.eval_tab_frames["Dateien"]
        files_tab.grid_rowconfigure(2, weight=1)

        folder_row = ctk.CTkFrame(files_tab, fg_color="transparent")
        folder_row.grid(row=0, column=0, padx=8, pady=(10, 4), sticky="ew")
        folder_row.grid_columnconfigure(0, weight=1)
        self.eval_folder_entry = ctk.CTkEntry(folder_row)
        self.eval_folder_entry.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        self.eval_folder_entry.insert(0, str(MEASUREMENT_DIR))
        self.eval_folder_entry.bind("<Return>", lambda _e: self._refresh_file_list())
        ctk.CTkButton(
            folder_row, text="Ordner…", width=75, command=self._choose_eval_folder
        ).grid(row=0, column=1)

        tools_row = ctk.CTkFrame(files_tab, fg_color="transparent")
        tools_row.grid(row=1, column=0, padx=8, pady=4, sticky="ew")
        tools_row.grid_columnconfigure(0, weight=1)
        self.eval_filter = ctk.CTkEntry(tools_row, placeholder_text="filter")
        self.eval_filter.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        self.eval_filter.bind("<KeyRelease>", self._on_filter_key)
        ctk.CTkButton(tools_row, text="Refresh", width=70,
                      command=self._refresh_file_list).grid(row=0, column=1, padx=(0, 5))
        ctk.CTkButton(tools_row, text="Collapse All", width=90,
                      command=self._collapse_tree).grid(row=0, column=2)

        tree_frame = ctk.CTkFrame(files_tab)
        tree_frame.grid(row=2, column=0, padx=8, pady=(4, 8), sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        self.eval_tree = ttk.Treeview(tree_frame, columns=("date",), style="Fetch.Treeview",
                                      selectmode="extended")   # Strg/Shift: mehrere
        self.eval_tree.heading("#0", text="Directory / File", anchor="w")
        self.eval_tree.heading("date", text="Date", anchor="w")
        self.eval_tree.column("#0", width=400, minwidth=200, stretch=True)
        self.eval_tree.column("date", width=118, minwidth=90, stretch=False)
        self.eval_tree.grid(row=0, column=0, sticky="nsew", padx=(1, 0), pady=1)
        tree_scroll = ctk.CTkScrollbar(tree_frame, command=self.eval_tree.yview)
        tree_scroll.grid(row=0, column=1, sticky="ns")
        tree_xscroll = ctk.CTkScrollbar(tree_frame, orientation="horizontal",
                                        command=self.eval_tree.xview)
        tree_xscroll.grid(row=1, column=0, sticky="ew")
        self.eval_tree.configure(yscrollcommand=tree_scroll.set, xscrollcommand=tree_xscroll.set)
        self.eval_tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.eval_tree.bind("<Double-1>", self._on_tree_double)
        self._tree_paths = {}
        self._filter_job = None
        self.selected_eval_file = None
        self.selected_eval_files = []
        self._style_tree()

        # ======== Reiter "Einstellungen" (nur Oberfläche) ========
        settings_tab = self.eval_tab_frames["Einstellungen"]
        settings_tab.grid_rowconfigure(0, weight=1)
        settings = ctk.CTkScrollableFrame(settings_tab, fg_color="transparent")
        settings.grid(row=0, column=0, padx=8, pady=(8, 4), sticky="nsew")
        settings.grid_columnconfigure(0, weight=1)
        self._build_eval_settings(settings)

        # ======== Reiter "ΔVth": max ΔVth Messung gegen Referenz ========
        self._build_dvth_tab(self.eval_tab_frames["ΔVth"])

        # ---- Unten, in allen Reitern sichtbar ----
        ctk.CTkButton(side, text="Auswerten", command=self._apply_eval_settings).grid(
            row=2, column=0, padx=12, pady=(6, 4), sticky="ew")
        self.eval_settings_status = ctk.CTkLabel(
            side, text=self.SETTINGS_HINT, text_color=App.MUTED, justify="left", anchor="w",
            wraplength=520)
        self.eval_settings_status.grid(row=3, column=0, padx=12, pady=(0, 10), sticky="ew")
        # aktuell übernommene Einstellungen (gelten bis zum nächsten "Auswerten")
        self.applied = self._read_settings()

        self.eval_tab_bar.set("Dateien")
        self._show_eval_tab("Dateien")

        # ---- Rechts: Diagramm ----
        plot = ctk.CTkFrame(self)
        plot.grid(row=1, column=1, padx=(5, 10), pady=10, sticky="nsew")
        plot.grid_columnconfigure(0, weight=1)
        plot.grid_rowconfigure(0, weight=1)
        self.eval_plot = plot
        self.eval_plot_label = ctk.CTkLabel(
            plot,
            text="Im Reiter „Dateien“ eine Messung anklicken.",
            justify="center",
            text_color=App.MUTED,
        )
        self.eval_plot_label.grid(row=0, column=0, padx=20, pady=20)
        self.eval_info = ctk.CTkLabel(plot, text="", text_color=App.MUTED, justify="left",
                                      anchor="w", wraplength=760)
        self.eval_info.grid(row=2, column=0, padx=10, pady=(0, 8), sticky="ew")
        # Ergebnistext des ΔVth-Abgleichs (unter dem Diagramm)
        self.eval_result = ctk.CTkTextbox(plot, font=("Consolas", 13), wrap="none", height=230)
        self._mpl = None
        self._last_view = None

        self._refresh_file_list()

    # ------------------------------------------------------------------
    # Auswerte-Einstellungen (nur Oberfläche)
    # Vorschläge: Vorverarbeitung, Analyse, Anzeige, Export
    # ------------------------------------------------------------------
    @staticmethod
    def _section(parent, row, title, opened=True):
        """Aufklappbarer Abschnitt. Gibt den Inhalts-Frame zurück."""
        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.grid_columnconfigure(1, weight=1)

        state = {"open": opened}

        def toggle():
            state["open"] = not state["open"]
            if state["open"]:
                content.grid()
                header.configure(text=f"▾ {title}")
            else:
                content.grid_remove()
                header.configure(text=f"▸ {title}")

        header = ctk.CTkButton(
            parent, text=f"▾ {title}", anchor="w", command=toggle,
            font=(App.FONT, 14, "bold"), fg_color=App.HEADER,
            text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
        )
        header.grid(row=row, column=0, padx=0, pady=(8, 2), sticky="ew")
        content.grid(row=row + 1, column=0, padx=4, pady=(0, 4), sticky="ew")
        if not opened:
            content.grid_remove()
            header.configure(text=f"▸ {title}")
        return content

    @staticmethod
    def _s_check(parent, row, text, on=False, command=None):
        box = ctk.CTkCheckBox(parent, text=text, command=command)
        box.grid(row=row, column=0, columnspan=2, padx=4, pady=3, sticky="w")
        if on:
            box.select()
        return box

    @staticmethod
    def _s_option(parent, row, label, values, default=None, command=None):
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, padx=4, pady=3, sticky="w")
        menu = ctk.CTkOptionMenu(parent, values=values, width=130,
                                 command=(lambda _v: command()) if command else None)
        menu.grid(row=row, column=1, padx=4, pady=3, sticky="ew")
        if default is not None:
            menu.set(default)
        return menu

    @staticmethod
    def _s_entry(parent, row, label, default=""):
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, padx=4, pady=3, sticky="w")
        entry = ctk.CTkEntry(parent, width=130)
        entry.grid(row=row, column=1, padx=4, pady=3, sticky="ew")
        entry.insert(0, default)
        return entry

    @staticmethod
    def _s_slider(parent, row, label, from_, to, default, fmt, steps=None, on_change=None):
        """Regler mit Wertanzeige. fmt wandelt den Reglerwert in Text um."""
        text = ctk.CTkLabel(parent, text=f"{label}: {fmt(default)}")
        text.grid(row=row, column=0, columnspan=2, padx=4, pady=(4, 0), sticky="w")

        def changed(v):
            text.configure(text=f"{label}: {fmt(v)}")
            if on_change:
                on_change()

        slider = ctk.CTkSlider(parent, from_=from_, to=to, number_of_steps=steps, command=changed)
        slider.set(default)
        slider.grid(row=row + 1, column=0, columnspan=2, padx=4, pady=(0, 4), sticky="ew")
        return slider

    @staticmethod
    def _fmt_freq(log_value):
        f = 10 ** log_value
        return f"{f / 1000:.3g} kHz" if f >= 1000 else f"{f:.3g} Hz"

    def _build_eval_settings(self, parent):
        # ---------------- Vorverarbeitung ----------------
        pre = self._section(parent, 0, "Vorverarbeitung")
        upd = self._settings_changed         # erst mit "Auswerten" übernehmen
        self.pre = {}
        r = 0
        # Standard aus, damit die Rohdaten zuerst unverändert zu sehen sind
        self.pre["lp_on"] = self._s_check(pre, r, "Digitaler Tiefpass", command=upd); r += 1
        # Regler logarithmisch: 10^0 … 10^5 Hz (1 Hz … 100 kHz)
        self.pre["fc"] = self._s_slider(pre, r, "Grenzfrequenz", 0, 5, 2, self._fmt_freq,
                                        on_change=upd); r += 2
        self.pre["kind"] = self._s_option(pre, r, "Filtertyp", ["Bessel", "Butterworth"],
                                          command=upd); r += 1
        self.pre["order"] = self._s_slider(pre, r, "Ordnung", 1, 8, 4, lambda v: f"{int(round(v))}",
                                           steps=7, on_change=upd); r += 2
        self.pre["zero_phase"] = self._s_check(pre, r, "Phasenfrei (filtfilt)", on=True,
                                               command=upd); r += 1
        self.pre["med_on"] = self._s_check(pre, r, "Medianfilter", command=upd); r += 1
        self.pre["med_w"] = self._s_slider(pre, r, "Fensterbreite", 3, 101, 5,
                                           lambda v: f"{int(round(v)) | 1} Punkte", steps=49,
                                           on_change=upd); r += 2
        self._s_option(pre, r, "Drift entfernen", ["Aus", "Linear", "Polynom 2", "Polynom 3"]); r += 1
        self._s_check(pre, r, "50-Hz-Notch (+ Oberwellen)"); r += 1
        self._s_entry(pre, r, "Offset (nA)", "0"); r += 1
        self._s_check(pre, r, "Offset aus Nullmessung"); r += 1
        self.pre["t_start"] = self._s_slider(pre, r, "Zeitbereich Start", 0, 100, 0,
                                             lambda v: f"{v:.0f} %", steps=100, on_change=upd); r += 2
        self.pre["t_end"] = self._s_slider(pre, r, "Zeitbereich Ende", 0, 100, 100,
                                           lambda v: f"{v:.0f} %", steps=100, on_change=upd); r += 2
        self._s_option(pre, r, "Dezimierung", ["1", "2", "5", "10", "100"])

        # ---------------- Analyse ----------------
        ana = self._section(parent, 2, "Analyse")
        analyses = {}

        def show_analysis(name):
            for key, frame in analyses.items():
                if key == name:
                    frame.grid()
                else:
                    frame.grid_remove()

        ctk.CTkLabel(ana, text="Auswertung").grid(row=0, column=0, columnspan=2, padx=4, pady=(3, 0), sticky="w")
        names = [
            "Rohdaten anzeigen",
            "ID-VG / V_th bestimmen",
            "Transient / RTN-Histogramm",
            "Rauschspektrum (PSD)",
            "MSM: ΔV_th über Stresszeit",
        ]
        ctk.CTkOptionMenu(ana, values=names, command=show_analysis).grid(
            row=1, column=0, columnspan=2, padx=4, pady=3, sticky="ew"
        )
        for name in names:
            frame = ctk.CTkFrame(ana, fg_color="transparent")
            frame.grid(row=2, column=0, columnspan=2, sticky="ew")
            frame.grid_columnconfigure(1, weight=1)
            analyses[name] = frame

        def result(frame, row, text):
            ctk.CTkLabel(frame, text=text, text_color=App.MUTED, justify="left").grid(
                row=row, column=0, columnspan=2, padx=4, pady=(6, 3), sticky="w"
            )

        f = analyses["Rohdaten anzeigen"]
        result(f, 0, "Keine weiteren Einstellungen.")

        f = analyses["ID-VG / V_th bestimmen"]
        self._s_option(f, 0, "Methode", ["Konstantstrom", "Max. g_m-Extrapolation"])
        self._s_entry(f, 1, "I_crit (nA)", "100")
        self._s_slider(f, 2, "g_m-Glättung", 1, 21, 5, lambda v: f"{int(round(v))} Punkte", steps=20)
        result(f, 4, "V_th: –   SS: – mV/dec")

        f = analyses["Transient / RTN-Histogramm"]
        self._s_slider(f, 0, "Bins", 10, 500, 100, lambda v: f"{int(round(v))}", steps=49)
        self._s_option(f, 2, "Niveaus", ["2", "3", "4"])
        self._s_option(f, 3, "Schwellwert", ["Automatisch", "Manuell"])
        self._s_entry(f, 4, "Schwelle (nA)", "")
        self._s_check(f, 5, "Time-Lag-Plot anzeigen")
        result(f, 6, "ΔI: –   τ_c: –   τ_e: –")

        f = analyses["Rauschspektrum (PSD)"]
        self._s_option(f, 0, "Segmentlänge", ["256", "1024", "4096", "16384", "65536"], "4096")
        self._s_option(f, 1, "Fenster", ["Hann", "Hamming", "Blackman", "Rechteck"])
        self._s_check(f, 2, "Lorentz-Fit", on=True)
        self._s_check(f, 3, "1/f-Fit")
        result(f, 4, "f_c: –   τ: –")

        f = analyses["MSM: ΔV_th über Stresszeit"]
        self._s_option(f, 0, "Darstellung", ["ΔV_th über t_stress", "Recovery über t_relax"])
        self._s_check(f, 1, "Potenzgesetz-Fit (ΔV_th ∝ tⁿ)", on=True)
        result(f, 2, "n: –")

        show_analysis(names[0])

        # ---------------- Anzeige ----------------
        view = self._section(parent, 4, "Anzeige")
        # auto: ID-VG -> y log; MSM-Transient/SPOT-Lauf/ΔVth -> x log; sonst linear
        self.pre["xscale"] = self._s_option(view, 0, "x-Achse", ["auto", "linear", "log"],
                                            command=upd)
        self.pre["yscale"] = self._s_option(view, 1, "y-Achse", ["auto", "linear", "log"],
                                            command=upd)
        self.pre["unit"] = self._s_option(view, 2, "Einheit", ["A", "µA", "nA", "pA"], "nA",
                                          command=upd)
        self.pre["overlay_raw"] = self._s_check(view, 3, "Roh + gefiltert überlagern", on=True,
                                                command=upd)
        self.pre["multi"] = self._s_check(view, 4, "Mehrere Dateien überlagern (Strg/Shift-Klick)",
                                          command=upd)
        self.pre["run"] = self._s_check(view, 5, "Ganzen Lauf überlagern (alle Zyklen)",
                                        command=upd)

        # ---------------- Export ----------------
        exp = self._section(parent, 6, "Export", opened=False)
        self._s_check(exp, 0, "Einstellungen in .h5 speichern", on=True)
        self._s_option(exp, 1, "Bildformat", ["PNG", "PDF", "SVG"])
        ctk.CTkButton(exp, text="Diagramm exportieren").grid(
            row=2, column=0, columnspan=2, padx=4, pady=3, sticky="ew"
        )
        ctk.CTkButton(exp, text="Daten als CSV", fg_color=App.SECONDARY).grid(
            row=3, column=0, columnspan=2, padx=4, pady=3, sticky="ew"
        )

    # ------------------------------------------------------------------
    # Ordner mit Messungen durchsuchen
    # ------------------------------------------------------------------
    H5_SUFFIXES = (".h5", ".hdf5")

    def _choose_eval_folder(self):
        current = Path(self.eval_folder_entry.get().strip() or APP_DIR)
        folder = filedialog.askdirectory(
            title="Ordner mit Messungen wählen",
            initialdir=str(current) if current.exists() else str(APP_DIR),
        )
        if folder:
            self.eval_folder_entry.delete(0, "end")
            self.eval_folder_entry.insert(0, folder)
            self._refresh_file_list()

    SKIP_DIRS = {".venv", "__pycache__", ".git", "build", "dist"}
    TREE_MAX_DEPTH = 8

    def _style_tree(self):
        """ttk-Treeview an Hell/Dunkel anpassen (CustomTkinter hat keinen Baum)."""
        if ctk.get_appearance_mode() == "Dark":
            c = dict(bg="#1D1E1E", alt="#242526", fg="#DCE4EE", head="gray25", sel="#1F6AA5")
        else:
            c = dict(bg="#FFFFFF", alt="#F2F2F2", fg="#1E1E1E", head="#ECECEC", sel="#308CC6")
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Fetch.Treeview", background=c["bg"], fieldbackground=c["bg"],
                        foreground=c["fg"], rowheight=24, borderwidth=0, font=(App.FONT, 10))
        style.configure("Fetch.Treeview.Heading", background=c["head"], foreground=c["fg"],
                        relief="flat", borderwidth=1, font=(App.FONT, 10))
        style.map("Fetch.Treeview", background=[("selected", c["sel"])],
                  foreground=[("selected", "#FFFFFF")])
        style.map("Fetch.Treeview.Heading", background=[("active", c["head"])])
        self.eval_tree.tag_configure("even", background=c["bg"])
        self.eval_tree.tag_configure("odd", background=c["alt"])   # Streifen wie im Qt-Browser

    def _refresh_file_list(self):
        """Ordner als Baum: Unterordner + .h5-Dateien mit Datum (wie Qt-Dateibrowser)."""
        tree = self.eval_tree
        tree.delete(*tree.get_children())
        self._tree_paths = {}
        self.selected_eval_file = None
        self.selected_eval_files = []

        folder = Path(self.eval_folder_entry.get().strip())
        if not folder.is_dir():
            tree.insert("", "end", text="Ordner nicht gefunden.", values=("",))
            return
        up = tree.insert("", "end", text="📁 ../", values=("",))
        self._tree_paths[up] = folder.parent

        text_filter = self.eval_filter.get().strip().lower()
        found = self._fill_tree("", folder, text_filter, 0)
        if found == 0:
            tree.insert("", "end", text="(keine .h5-Messungen)", values=("",))
        self._stripe_tree()

    def _fill_tree(self, parent, folder, text_filter, depth):
        """Fügt Ordner (nur wenn sie Messungen enthalten) und Dateien ein. Gibt Anzahl Dateien zurück."""
        if depth > self.TREE_MAX_DEPTH:
            return 0
        try:
            entries = sorted(folder.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except OSError:
            return 0
        count = 0
        for path in entries:
            try:
                stamp = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                is_dir = path.is_dir()
            except OSError:
                continue
            if is_dir:
                if path.name in self.SKIP_DIRS or path.name.startswith("."):
                    continue
                item = self.eval_tree.insert(parent, "end", text=f"📁 {path.name}",
                                             values=(stamp,), open=bool(text_filter))
                found = self._fill_tree(item, path, text_filter, depth + 1)
                if found == 0:
                    self.eval_tree.delete(item)      # leere Ordner nicht anzeigen
                else:
                    self._tree_paths[item] = path
                    count += found
            elif path.suffix.lower() in self.H5_SUFFIXES:
                if text_filter and text_filter not in path.name.lower():
                    continue
                item = self.eval_tree.insert(parent, "end", text=f"📄 {path.name}", values=(stamp,))
                self._tree_paths[item] = path
                count += 1
        return count

    def _stripe_tree(self):
        """Abwechselnde Zeilenfarben in der Reihenfolge, wie die Zeilen erscheinen."""
        row = 0

        def walk(parent):
            nonlocal row
            for item in self.eval_tree.get_children(parent):
                self.eval_tree.item(item, tags=("odd" if row % 2 else "even",))
                row += 1
                walk(item)

        walk("")

    def _on_filter_key(self, _event):
        # kurz warten, damit nicht bei jedem Buchstaben der ganze Ordner gelesen wird
        if self._filter_job:
            self.after_cancel(self._filter_job)
        self._filter_job = self.after(300, self._refresh_file_list)

    def _collapse_tree(self):
        def walk(parent):
            for item in self.eval_tree.get_children(parent):
                self.eval_tree.item(item, open=False)
                walk(item)
        walk("")

    def _on_tree_select(self, _event):
        files = [self._tree_paths.get(item) for item in self.eval_tree.selection()]
        files = [p for p in files if p is not None and p.is_file()]
        if not files:
            return
        focus = self._tree_paths.get(self.eval_tree.focus())
        self.selected_eval_files = files
        self._select_eval_file(focus if focus in files else files[-1])

    def _on_tree_double(self, event):
        item = self.eval_tree.identify_row(event.y)
        if self.eval_tree.item(item, "text") == "📁 ../":
            parent = self._tree_paths.get(item)
            if parent is not None:
                self.eval_folder_entry.delete(0, "end")
                self.eval_folder_entry.insert(0, str(parent))
                self._refresh_file_list()

    def _build_dvth_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            tab, justify="left", anchor="w", wraplength=520, text_color=App.MUTED,
            text="Max. ΔVth einer MSM-Messung (Messart IDVG) mit einer Referenz-Messung "
                 "vergleichen. Im Reiter „Dateien“ eine beliebige Datei des Laufs wählen "
                 "und übernehmen – alle Zyklen (c00 …) werden automatisch gefunden.",
        ).grid(row=0, column=0, padx=10, pady=(10, 6), sticky="ew")

        self.dvth_files = {"Messung": None, "Referenz": None}
        self.dvth_labels = {}
        for row, role in ((1, "Messung"), (2, "Referenz")):
            box = ctk.CTkFrame(tab)
            box.grid(row=row, column=0, padx=8, pady=4, sticky="ew")
            box.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(box, text=role, font=(App.FONT, 13, "bold")).grid(
                row=0, column=0, padx=8, pady=(6, 0), sticky="w")
            label = ctk.CTkLabel(box, text="– keine Datei –", anchor="w", justify="left",
                                 wraplength=510, text_color=App.MUTED)
            label.grid(row=1, column=0, padx=8, pady=2, sticky="ew")
            ctk.CTkButton(box, text="Ausgewählte Datei übernehmen", fg_color=App.SECONDARY,
                          command=lambda r=role: self._dvth_take(r)).grid(
                row=2, column=0, padx=8, pady=(2, 8), sticky="ew")
            self.dvth_labels[role] = label

        row = ctk.CTkFrame(tab, fg_color="transparent")
        row.grid(row=3, column=0, padx=8, pady=6, sticky="ew")
        row.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(row, text="I_krit (nA)").grid(row=0, column=0, padx=(2, 6))
        self.dvth_ikrit = ctk.CTkEntry(row)
        self.dvth_ikrit.insert(0, "50")
        self.dvth_ikrit.grid(row=0, column=1, sticky="ew")
        ctk.CTkButton(tab, text="Vergleichen", command=self._dvth_compare).grid(
            row=4, column=0, padx=8, pady=(4, 6), sticky="ew")
        self.dvth_status = ctk.CTkLabel(tab, text="", text_color=App.MUTED, justify="left",
                                        anchor="w", wraplength=520)
        self.dvth_status.grid(row=5, column=0, padx=10, pady=(0, 8), sticky="ew")

    def _dvth_take(self, role):
        path = self.selected_eval_file
        if path is None:
            self.dvth_status.configure(text="Zuerst im Reiter „Dateien“ eine .h5-Datei anklicken.")
            return
        self.dvth_files[role] = path
        self.dvth_labels[role].configure(text=f"{path.parent.name}/{path.name}")
        self.dvth_status.configure(text="")

    def _dvth_compare(self):
        meas, ref = self.dvth_files["Messung"], self.dvth_files["Referenz"]
        if meas is None or ref is None:
            self.dvth_status.configure(text="Bitte Messung und Referenz übernehmen.")
            return
        try:
            i_krit = float(self.dvth_ikrit.get().strip().replace(",", ".")) * 1e-9
            if i_krit <= 0:
                raise ValueError
        except ValueError:
            self.dvth_status.configure(text="I_krit muss eine Zahl > 0 sein (in nA).")
            return
        try:
            res_m = messdaten.analyse_run(meas, i_krit)
            res_r = messdaten.analyse_run(ref, i_krit)
        except (RuntimeError, OSError, KeyError) as exc:
            self.dvth_status.configure(text=f"Lesen fehlgeschlagen: {exc}")
            return
        text = messdaten.compare_text(res_m, res_r, i_krit)
        self._last_view = ("compare", res_m, res_r)
        self.eval_result.configure(state="normal")
        self.eval_result.delete("1.0", "end")
        self.eval_result.insert("1.0", text)
        self.eval_result.configure(state="disabled")
        self._redraw_plot()
        if self._mpl is None:          # ohne matplotlib wenigstens den Text zeigen
            self.eval_plot_label.grid_remove()
            self.eval_result.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.dvth_status.configure(text="✓ Verglichen – Ergebnis rechts.")

    def _select_eval_file(self, path):
        """Datei gewählt -> anzeigen."""
        self.selected_eval_file = path
        self._last_view = ("file", path)
        self._redraw_plot()

    # ---------- Einstellungen erst mit "Auswerten" übernehmen ----------
    SETTINGS_HINT = "Geänderte Einstellungen werden mit „Auswerten“ übernommen."
    UNIT_FACTOR = {"A": 1e-9, "µA": 1e-3, "nA": 1.0, "pA": 1e3}    # von nA umrechnen

    def _read_settings(self):
        p = self.pre
        return {
            "lp_on": bool(p["lp_on"].get()), "fc": 10 ** p["fc"].get(),
            "kind": p["kind"].get(), "order": p["order"].get(),
            "zero_phase": bool(p["zero_phase"].get()),
            "med_on": bool(p["med_on"].get()), "med_w": int(round(p["med_w"].get())),
            "t_start": p["t_start"].get(), "t_end": p["t_end"].get(),
            "xscale": p["xscale"].get(), "yscale": p["yscale"].get(), "unit": p["unit"].get(),
            "overlay_raw": bool(p["overlay_raw"].get()), "multi": bool(p["multi"].get()),
            "run": bool(p["run"].get()),
        }

    def _settings_changed(self):
        if getattr(self, "eval_settings_status", None) is not None:
            self.eval_settings_status.configure(
                text="⚠ Einstellungen geändert – „Auswerten“ drücken, um sie zu übernehmen.",
                text_color=("#B00020", "#F2A65A"))

    def _apply_eval_settings(self):
        self.applied = self._read_settings()
        self.eval_settings_status.configure(text="✓ Einstellungen übernommen. " + self.SETTINGS_HINT,
                                            text_color=App.MUTED)
        if self._last_view is None and self.selected_eval_file is not None:
            self._last_view = ("file", self.selected_eval_file)
        self._redraw_plot()

    # ---------- Diagramm (matplotlib) ----------
    def _eval_ikrit(self):
        try:
            value = float(self.dvth_ikrit.get().strip().replace(",", ".")) * 1e-9
            return value if value > 0 else 50e-9
        except ValueError:
            return 50e-9

    def _ensure_plot(self):
        """matplotlib-Figur einmalig anlegen. False, wenn matplotlib fehlt."""
        if self._mpl is not None:
            return True
        try:
            import matplotlib
            matplotlib.use("TkAgg")
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
        except ImportError:
            self._show_plot_message("matplotlib fehlt – im venv: pip install -r requirements.txt")
            return False
        holder = ctk.CTkFrame(self.eval_plot, fg_color="transparent")
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, master=holder)
        toolbar = NavigationToolbar2Tk(canvas, holder, pack_toolbar=False)   # Zoom, Verschieben, Speichern
        toolbar.update()
        toolbar.pack(side="bottom", fill="x")
        canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        self._mpl = {"holder": holder, "fig": fig, "ax": ax, "canvas": canvas}
        return True

    def _show_plot_message(self, text):
        if self._mpl is not None:
            self._mpl["holder"].grid_remove()
        self.eval_result.grid_remove()
        self.eval_plot_label.configure(text=text)
        self.eval_plot_label.grid(row=0, column=0, padx=20, pady=20)
        self.eval_info.configure(text="")

    def _preprocess(self, data):
        """Vorverarbeitung auf alle Kurven anwenden (nur Anzeige)."""
        cfg = self.applied
        is_time = data["xlabel"].startswith("t ")
        show_raw = cfg["overlay_raw"]
        series, notes = [], []
        for s in data["series"]:
            xlog = cfg["xscale"] == "log" or (cfg["xscale"] == "auto" and data.get("xlog"))
            x, y, yf, n = vorverarbeitung.apply(s["x"], s["y"], cfg, is_time, xlog)
            notes += n
            if yf is None:
                series.append(dict(s, x=x, y=y))
            else:
                if show_raw:
                    series.append(dict(s, x=x, y=y, label=f"{s['label']} roh", raw=True))
                series.append(dict(s, x=x, y=yf, label=f"{s['label']} gefiltert", marker=""))
        active = [name for name, on in (("Zeitbereich", cfg["t_start"] > 0 or cfg["t_end"] < 100),
                                        ("Median", cfg["med_on"]), ("Tiefpass", cfg["lp_on"])) if on]
        if cfg["lp_on"] and not any("Tiefpass" in n for n in notes):
            active[-1] = (f"Tiefpass {cfg['kind']} {int(round(cfg['order']))}. Ordn. "
                          f"{vorverarbeitung_fmt(cfg['fc'])}{' filtfilt' if cfg['zero_phase'] else ''}")
        return dict(data, series=series), active, sorted(set(notes))

    def _redraw_plot(self):
        view = self._last_view
        if view is None or not self._ensure_plot():
            return
        cfg = self.applied
        try:
            files = getattr(self, "selected_eval_files", [])
            if view[0] == "file" and cfg["multi"] and len(files) > 1:
                data = messdaten.view_multi(files, cfg["run"], self._eval_ikrit())
            elif view[0] == "file":
                data = messdaten.view_single(view[1], cfg["run"], self._eval_ikrit())
            else:
                data = messdaten.view_compare(view[1], view[2])
        except (RuntimeError, OSError, KeyError, ValueError) as exc:
            self._show_plot_message(f"Datei kann nicht gelesen werden:\n{exc}")
            return
        extra = ""
        if view[0] == "file":
            data, active, notes = self._preprocess(data)
            if active:
                extra += "\nVorverarbeitung (nur Anzeige): " + ", ".join(active)
            if notes:
                extra += "\n⚠ " + " · ".join(notes)
            data["info"] = data.get("info", "") + extra
        self._draw(data)
        self.eval_plot_label.grid_remove()
        self._mpl["holder"].grid(row=0, column=0, padx=6, pady=6, sticky="nsew")
        if view[0] == "file":
            self.eval_result.grid_remove()
            self.eval_info.configure(text=data.get("info", ""))
        else:
            self.eval_info.configure(text="")
            self.eval_result.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")

    def _draw(self, data):
        fig, ax, canvas = self._mpl["fig"], self._mpl["ax"], self._mpl["canvas"]
        dark = ctk.get_appearance_mode() == "Dark"
        bg, fg = ("#2B2B2B", "#DCE4EE") if dark else ("#FFFFFF", "#202020")
        cfg = self.applied
        ax.clear()
        # Einheit: Ströme kommen in nA, ΔVth in mV (bleibt)
        current = data["ylabel"].startswith("|I")
        factor = self.UNIT_FACTOR[cfg["unit"]] if current else 1.0
        if current:
            data = dict(data, ylabel=f"|I_D| ({cfg['unit']})",
                        series=[dict(s, y=[v * factor for v in s["y"]]) for s in data["series"]],
                        i_krit_nA=(data["i_krit_nA"] * factor) if data.get("i_krit_nA") else None)
        for serie in data["series"]:
            if serie.get("raw"):          # Rohdaten blass hinter der gefilterten Kurve
                ax.plot(serie["x"], serie["y"], linewidth=0.8, alpha=0.35, color="gray",
                        label=serie["label"])
            else:
                ax.plot(serie["x"], serie["y"], marker=serie.get("marker", ""), markersize=4,
                        linewidth=1.2, label=serie["label"])
        if data.get("i_krit_nA"):
            ax.axhline(data["i_krit_nA"], color="gray", linestyle="--", linewidth=0.8)
        if data.get("vth") is not None:
            ax.axvline(data["vth"], color="gray", linestyle=":", linewidth=0.8)
            ax.annotate(f"Vth = {data['vth']:.4f} V", (data["vth"], data["i_krit_nA"]),
                        xytext=(6, -14), textcoords="offset points", color=fg, fontsize=9)
        ylog = cfg["yscale"] == "log" or (cfg["yscale"] == "auto" and current
                                          and data["xlabel"].startswith("V_G"))
        xlog = cfg["xscale"] == "log" or (cfg["xscale"] == "auto" and data.get("xlog"))
        ax.set_yscale("log" if ylog else "linear")
        ax.set_xscale("log" if xlog else "linear")
        ax.set_title(data["title"], fontsize=10, color=fg)
        ax.set_xlabel(data["xlabel"], color=fg)
        ax.set_ylabel(data["ylabel"], color=fg)
        ax.grid(True, which="both", alpha=0.3)
        if len(data["series"]) > 1:
            legend = ax.legend(fontsize=8, facecolor=bg, edgecolor=fg)
            for text in legend.get_texts():
                text.set_color(fg)
        fig.set_facecolor(bg)
        ax.set_facecolor(bg)
        ax.tick_params(colors=fg, which="both")
        for spine in ax.spines.values():
            spine.set_color(fg)
        fig.tight_layout()
        canvas.draw_idle()

    # ------------------------------------------------------------------
    # Reiter-Umschaltung
    # ------------------------------------------------------------------
    def _show_tab(self, name):
        self.tab_frames[name].tkraise()

    # ------------------------------------------------------------------
    # Hilfsfunktionen für den Aufbau der Reiter
    # ------------------------------------------------------------------
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
    def _add_option(parent, label_text, row, col, values):
        ctk.CTkLabel(parent, text=label_text).grid(
            row=row, column=col, padx=(10, 6), pady=8, sticky="w"
        )
        option = ctk.CTkOptionMenu(parent, values=values)
        option.grid(row=row, column=col + 1, padx=(4, 10), pady=8, sticky="ew")
        return option

    @staticmethod
    def _make_param_box(tab, columns):
        """Parameterbereich oben im Reiter."""
        box = ctk.CTkFrame(tab)
        box.grid(row=0, column=0, sticky="ew")
        for col in range(columns):
            box.grid_columnconfigure(col, weight=1)
        return box

    @staticmethod
    def _add_plot_placeholder(tab, text):
        """Diagrammbereich unten im Reiter (noch Platzhalter)."""
        plot = ctk.CTkFrame(tab)
        plot.grid(row=2, column=0, pady=(10, 0), sticky="nsew")
        plot.grid_columnconfigure(0, weight=1)
        plot.grid_rowconfigure(0, weight=1)
        ctk.CTkLabel(plot, text=text, justify="center", text_color=App.MUTED).grid(
            row=0, column=0, padx=20, pady=20
        )
        return plot

    # ------------------------------------------------------------------
    # Datei-Zeile (Speichern unter), HDF5 (.h5)
    # Speichern und Laden selbst sind noch nicht umgesetzt; die Buttons
    # öffnen nur den Dateidialog und merken sich den Pfad.
    # ------------------------------------------------------------------
    H5_FILETYPES = [("HDF5-Datei", "*.h5 *.hdf5"), ("Alle Dateien", "*.*")]

    def _add_file_row(self, tab, tab_name):
        row = ctk.CTkFrame(tab)
        row.grid(row=1, column=0, pady=(10, 0), sticky="ew")
        row.grid_columnconfigure(1, weight=1)

        # Welches Bauteil (DUT) gemessen wird
        ctk.CTkLabel(row, text="Device").grid(
            row=0, column=0, padx=(10, 6), pady=(8, 0), sticky="w"
        )
        device_entry = ctk.CTkEntry(
            row, placeholder_text="z. B. BS170-01  (nur Buchstaben, Ziffern, -)"
        )
        device_entry.grid(row=0, column=1, columnspan=2, padx=(4, 10), pady=(8, 0), sticky="ew")
        self.device_entries[tab_name] = device_entry

        ctk.CTkLabel(row, text="Speicherordner").grid(
            row=1, column=0, padx=(10, 6), pady=8, sticky="w"
        )
        entry = ctk.CTkEntry(row)
        entry.grid(row=1, column=1, padx=4, pady=8, sticky="ew")
        entry.insert(0, self._default_file_name(tab_name))
        self.save_path_entries[tab_name] = entry

        ctk.CTkButton(
            row, text="Durchsuchen…", width=120,
            command=lambda: self._choose_save_file(tab_name),
        ).grid(row=1, column=2, padx=4, pady=8)

        # Info: wie Device/Ordner einzugeben sind, Dateien werden automatisch benannt
        ctk.CTkButton(
            row, text="?", width=36, font=(App.FONT, 15, "bold"), fg_color=App.SECONDARY,
            command=lambda: self._show_naming_info(tab_name),
        ).grid(row=0, column=3, rowspan=2, padx=(4, 10), pady=8, sticky="ns")

    @staticmethod
    def _default_file_name(tab_name):
        # Nur der Ordner; der Dateiname wird automatisch erzeugt (dateinamen.py)
        return str(MEASUREMENT_DIR)

    def _choose_save_file(self, tab_name):
        entry = self.save_path_entries[tab_name]
        current = Path(entry.get().strip() or MEASUREMENT_DIR)
        path = filedialog.askdirectory(
            title=f"Speicherordner für {tab_name}-Messungen",
            initialdir=str(current) if current.exists() else None,
        )
        if path:
            entry.delete(0, "end")
            entry.insert(0, path)

    NAMING_INFO = (
        "Device\n"
        "  Name des Bauteils, z. B. BS170-01 oder W1-D12.\n"
        "  Erlaubt: A–Z, a–z, 0–9 und '-'. Andere Zeichen (Leerzeichen, /, _ …)\n"
        "  werden zu '-'. Leer = 'unbenannt'.\n\n"
        "Speicherordner\n"
        "  Nur den Ordner angeben, keinen Dateinamen.\n"
        "  Pro Device wird ein Unterordner angelegt:  <Ordner>/<Device>/\n\n"
        "Dateiname (automatisch)\n"
        "  <Art>_<Device>_<Bereich>[_<Stress>][_TS<Zeit>|_ref][_c<Zyklus>]_<Datum>.h5\n"
        "  Art:      iv = ID-VG,  tr = Transient,  sp = Spot\n"
        "  Bereich:  I100n = 100 nA,  I10u = 10 µA\n"
        "  Stress:   Typ + Gate-Spannung, z. B. BTI5V0 = 5,0 V,  m2V4 = −2,4 V\n"
        "  TS:       gesamte Stresszeit bis zu dieser Messung (TS500ms, TS11s)\n"
        "  ref/c00:  MSM-Referenz,  c01, c02 … = MSM-Zyklen (je eine Datei)\n"
        "  Datum:    Start der Messung bzw. des ganzen MSM-Laufs\n"
        "  Gibt es den Namen schon, wird _2, _3 … angehängt.\n\n"
        "Beispiele\n"
        "  iv_BS170-01_I10u_20261112-1430.h5\n"
        "  tr_BS170-01_I100n_BTI5V0_ref_c00_20261112-1500.h5\n"
        "  tr_BS170-01_I100n_BTI5V0_TS11s_c02_20261112-1500.h5"
    )

    def _show_naming_info(self, tab_name):
        device = dateinamen.clean(self.device_entries[tab_name].get())
        folder = Path(self.save_path_entries[tab_name].get().strip() or MEASUREMENT_DIR)

        win = ctk.CTkToplevel(self)
        win.title("Device & Speicherort – Dateinamen")
        win.resizable(False, False)
        win.transient(self)
        win.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(win, text="So werden die Messdateien benannt",
                     font=(App.FONT, 15, "bold")).grid(
            row=0, column=0, padx=16, pady=(14, 6), sticky="w")
        ctk.CTkLabel(win, text=self.NAMING_INFO, justify="left", anchor="w",
                     font=("Consolas", 12)).grid(
            row=1, column=0, padx=16, pady=4, sticky="w")
        ctk.CTkLabel(win, text=f"Aktuell landen die Dateien in:\n{folder / device}",
                     justify="left", anchor="w", text_color=App.MUTED).grid(
            row=2, column=0, padx=16, pady=(8, 4), sticky="w")
        ctk.CTkButton(win, text="OK", width=90, command=win.destroy).grid(
            row=3, column=0, padx=16, pady=(6, 14), sticky="e")

        win.after(50, win.grab_set)     # Fenster erst sichtbar, dann modal
        win.focus_force()

    def _show_measure_info(self, tab_name):
        """Fenster mit Erklärung der Messart, der Parameter und der Standardwerte."""
        win = ctk.CTkToplevel(self)
        win.title(f"Info – {tab_name}")
        win.geometry("760x620")
        win.transient(self)
        win.grid_columnconfigure(0, weight=1)
        win.grid_rowconfigure(0, weight=1)

        box = ctk.CTkTextbox(win, font=("Consolas", 12), wrap="none")
        box.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="nsew")
        box.insert("1.0", messinfo.text_for(tab_name))
        box.configure(state="disabled")          # nur lesen
        ctk.CTkButton(win, text="OK", width=90, command=win.destroy).grid(
            row=1, column=0, padx=12, pady=(4, 12), sticky="e")

        win.after(50, win.grab_set)
        win.focus_force()

    def _load_measurement(self, tab_name):
        path = filedialog.askopenfilename(
            title=f"{tab_name}-Messung laden",
            filetypes=self.H5_FILETYPES,
        )
        if path:
            self.instrument.log_queue.put((
                "SYSTEM",
                f"{tab_name}: Datei gewählt: {path} (Laden ist noch nicht umgesetzt)",
            ))

    # ------------------------------------------------------------------
    # Reiter "Transient" (angebunden an Instrument)
    # ------------------------------------------------------------------
    def _build_transient_tab(self, tab):
        params = self._make_param_box(tab, 4)

        self.sample_rate_entry = self._add_entry(
            params, "Sample Rate (Hz)", 0, 0, "100"
        )
        self.measure_time_entry = self._add_entry(
            params, "Measure Time (s)", 0, 2, "10"
        )
        self.points_entry = self._add_entry(
            params, "Messpunktanzahl", 1, 0, "1000"
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

        self.transient_range = self._add_option(params, "Strombereich", 2, 2, list(self.SENSE_RANGES))
        self.transient_avg = self._add_entry(params, "Mittelungen", 3, 0, "100")
        self.transient_settle = self._add_entry(params, "Einschwingzeit (ms)", 3, 2, "100")
        self._add_control_footer(params, 4, 4, "Transient")
        self.tab_status["Transient"].configure(
            text=f"Hinweis: max. {self.TR_MAX_POINTS} Punkte. Die Samplerate muss langsamer sein als ein "
                 "gemittelter Messpunkt dauert – sonst meldet die Firmware „WARN: dt zu kurz“."
        )

        # Data display placeholder: current provided firmware sends no measurement samples.
        self.plot_frame = self._add_plot_placeholder(
            tab,
            "Messdiagramm I(t)\n\n"
            "Die Firmware muss die Transientenmessung implementieren und\n"
            "Messdaten über UART zurücksenden, bevor hier Messkurven erscheinen.",
        )

    # ------------------------------------------------------------------
    # Reiter ohne Funktion (nur Oberfläche). Parameter laut
    # Befehlsreferenz_Python_PC.md, Kapitel 3, 6, 7 und 8.
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # Hilfsfunktionen für gekoppelte Eingabefelder
    # Regel: das Feld, in das gerade getippt wird, wird nie überschrieben –
    # nur die anderen Felder und die Infozeile werden neu berechnet.
    # ------------------------------------------------------------------
    @staticmethod
    def _num(entry):
        return float(entry.get().strip().replace(",", "."))

    @staticmethod
    def _put(entry, value):
        """Wert in ein Feld schreiben (auch wenn es gerade gesperrt ist)."""
        if abs(value - round(value)) < 1e-9:
            text = str(int(round(value)))
        else:
            text = f"{value:.6g}"
        if entry.get() == text:
            return
        state = entry.cget("state")
        if state == "disabled":
            entry.configure(state="normal")
        entry.delete(0, "end")
        entry.insert(0, text)
        if state == "disabled":
            entry.configure(state="disabled")

    @staticmethod
    def _set_enabled(entry, enabled):
        entry.configure(state="normal" if enabled else "disabled")

    @staticmethod
    def _fmt_duration(seconds):
        """Dauer lesbar: 850 ms, 12 s, 3,5 min, 2,1 h, 1,4 Tage."""
        if seconds < 1:
            return f"{seconds * 1000:.0f} ms"
        if seconds < 60:
            return f"{seconds:.3g} s".replace(".", ",")
        if seconds < 3600:
            return f"{seconds / 60:.3g} min".replace(".", ",")
        if seconds < 86400:
            return f"{seconds / 3600:.3g} h".replace(".", ",")
        return f"{seconds / 86400:.3g} Tage".replace(".", ",")

    def _bind_update(self, fields, keys, update):
        for key in keys:
            fields[key].bind("<KeyRelease>", lambda _e, k=key: update(k))

    def _info_label(self, parent, row, columnspan):
        label = ctk.CTkLabel(parent, text="", text_color=App.MUTED, justify="left", anchor="w")
        label.grid(row=row, column=0, columnspan=columnspan, padx=10, pady=(2, 4), sticky="w")
        return label

    # ------------------------------------------------------------------
    # ID-VG: Start / Stop / Schrittweite <-> Messpunkte, Dauer
    # ------------------------------------------------------------------
    def _build_idvg_tab(self, tab):
        body = self._make_param_box(tab, 4)
        f = self.idvg_fields = {}
        f["vd"] = self._add_entry(body, "Drain-Spannung (V)", 0, 0, "0.1")
        self.idvg_range = self._add_option(body, "Strombereich", 0, 2, list(self.SENSE_RANGES))
        f["start"] = self._add_entry(body, "Gate Start (V)", 1, 0, "0")
        f["stop"] = self._add_entry(body, "Gate Stop (V)", 1, 2, "2.5")
        f["step"] = self._add_entry(body, "Gate Schrittweite (V)", 2, 0, "0.05")
        f["points"] = self._add_entry(body, "Messpunkte", 2, 2, "")
        f["settle"] = self._add_entry(body, "Einschwingzeit/Schritt (ms)", 3, 0, "5")
        f["avg"] = self._add_entry(body, "Mittelungen", 3, 2, "100")
        self.idvg_info = self._info_label(body, 4, 4)
        self._add_control_footer(body, 5, 4, "ID-VG")
        self._add_plot_placeholder(tab, "Messdiagramm I_D(V_G)\n\n(noch ohne Funktion)")
        self._bind_update(f, ("start", "stop", "step", "points", "settle"), self._update_idvg)
        self._update_idvg("step")

    def _update_idvg(self, source):
        f = self.idvg_fields
        try:
            start, stop, settle = self._num(f["start"]), self._num(f["stop"]), self._num(f["settle"])
            span = abs(stop - start)
            if source == "points":
                points = int(self._num(f["points"]))
                if points < 2 or span == 0:
                    return
                self._put(f["step"], span / (points - 1))
            else:
                step = self._num(f["step"])
                if step <= 0:
                    return
                points = int(span / step + 1e-9) + 1
                self._put(f["points"], points)
        except ValueError:
            return      # Feld ist gerade halb eingetippt
        self.idvg_info.configure(
            text=f"{points} Punkte · Dauer ≈ {self._fmt_duration(points * settle / 1000)} "
                 "(nur Einschwingzeit, Mittelung kommt dazu)"
        )

    # ------------------------------------------------------------------
    # Stress: DYNAMIC -> Dauer = Zyklen × (On + Off), und umgekehrt
    # ------------------------------------------------------------------
    def _build_stress_tab(self, tab):
        body = self._make_param_box(tab, 4)
        f = self.stress_fields = {}
        self.stress_type = self._add_option(body, "Stress-Typ", 0, 0, ["BTI", "HCD"])
        self.stress_mode = self._add_option(body, "Stress-Modus", 0, 2, ["STATIC", "DYNAMIC"])
        f["vg"] = self._add_entry(body, "Gate-Stressspannung (V)", 1, 0, "5.0")
        f["vd"] = self._add_entry(body, "Drain-Stressspannung (V)", 1, 2, "0")
        f["time"] = self._add_entry(body, "Stressdauer (ms)", 2, 0, "60000")
        f["cycles"] = self._add_entry(body, "Zyklen (dynamisch)", 2, 2, "600")
        f["on"] = self._add_entry(body, "On-Zeit (ms)", 3, 0, "100")
        f["off"] = self._add_entry(body, "Off-Zeit (ms)", 3, 2, "100")
        self.stress_range = self._add_option(body, "Strombereich", 4, 0, list(self.SENSE_RANGES))
        f["avg"] = self._add_entry(body, "Mittelungen", 4, 2, "100")
        self.stress_after_idvg = ctk.CTkCheckBox(
            body, text="Danach ID-VG messen", command=self._update_stress_after)
        self.stress_after_idvg.grid(row=5, column=0, columnspan=2, padx=10, pady=8, sticky="w")
        self.stress_after_transient = ctk.CTkCheckBox(
            body, text="Danach Transient messen", command=self._update_stress_after)
        self.stress_after_transient.grid(row=5, column=2, columnspan=2, padx=10, pady=8, sticky="w")
        self.stress_info = self._info_label(body, 6, 4)
        # Parameter der Nachmessungen – nur sichtbar, wenn angehakt
        self.stress_idvg_frame, self.stress_sweep = self._add_sweep_frame(
            body, 7, 4, "Nachmessung ID-VG", with_drain=True)
        self.stress_tr_frame, self.stress_bias = self._add_bias_frame(
            body, 8, 4, "Nachmessung Transient")
        self._add_control_footer(body, 9, 4, "Stress")
        self._add_plot_placeholder(tab, "Messdiagramm nach Stress\n\n(noch ohne Funktion)")
        self.stress_mode.configure(command=lambda _v: self._update_stress("mode"))
        self._bind_update(f, ("time", "cycles", "on", "off"), self._update_stress)
        self._update_stress("mode")
        self._update_stress_after()

    def _update_stress_after(self):
        for checkbox, frame in ((self.stress_after_idvg, self.stress_idvg_frame),
                                (self.stress_after_transient, self.stress_tr_frame)):
            if checkbox.get():
                frame.grid()
            else:
                frame.grid_remove()

    def _update_stress(self, source):
        f = self.stress_fields
        dynamic = self.stress_mode.get() == "DYNAMIC"
        for key in ("cycles", "on", "off"):
            self._set_enabled(f[key], dynamic)
        try:
            if not dynamic:
                total = self._num(f["time"])
                self.stress_info.configure(text=f"Dauerstress: {self._fmt_duration(total / 1000)}")
                return
            on, off = self._num(f["on"]), self._num(f["off"])
            period = on + off
            if period <= 0:
                return
            if source == "time":
                cycles = max(1, round(self._num(f["time"]) / period))
                self._put(f["cycles"], cycles)
            else:
                cycles = max(1, int(self._num(f["cycles"])))
                self._put(f["time"], cycles * period)
        except ValueError:
            return
        total = cycles * period
        self.stress_info.configure(
            text=f"{cycles} Pulse × ({on:g} ms an + {off:g} ms aus) = {self._fmt_duration(total / 1000)}"
                 f" · reine Stresszeit {self._fmt_duration(cycles * on / 1000)} ({on / period:.0%})"
        )

    # ------------------------------------------------------------------
    # MSM: Zyklen / Startzeit / Faktor <-> Gesamt-Stresszeit
    # Stresszeit im Zyklus k:  t_k = Startzeit · Faktor^k
    # ------------------------------------------------------------------
    def _build_msm_tab(self, tab):
        body = self._make_param_box(tab, 6)
        f = self.msm_fields = {}
        self.msm_stress_type = self._add_option(body, "Stress-Typ", 0, 0, ["BTI", "HCD"])
        f["vg"] = self._add_entry(body, "Gate-Stress (V)", 0, 2, "5.0")
        f["vd"] = self._add_entry(body, "Drain-Stress (V)", 0, 4, "0")
        self.msm_type = self._add_option(body, "Messart", 1, 0, ["SPOT", "IDVG", "TRANSIENT"])
        f["read_vg"] = self._add_entry(body, "Lese-Gate (V)", 1, 2, "1.5")
        f["read_vd"] = self._add_entry(body, "Lese-Drain (V)", 1, 4, "0.1")
        f["cycles"] = self._add_entry(body, "Zyklen", 2, 0, "5")
        f["start"] = self._add_entry(body, "Startzeit (ms)", 2, 2, "1000")
        f["factor"] = self._add_entry(body, "Zeitfaktor", 2, 4, "10")
        f["delay"] = self._add_entry(body, "Mess-Verzögerung (ms)", 3, 0, "1")
        f["recovery"] = self._add_entry(body, "Recovery-Zeit (ms)", 3, 2, "0")
        f["maxpts"] = self._add_entry(body, "Max. Punkte", 3, 4, "5000")
        f["total"] = self._add_entry(body, "Gesamt-Stresszeit (ms)", 4, 0, "")
        self.msm_range = self._add_option(body, "Strombereich", 4, 2, list(self.SENSE_RANGES))
        f["avg"] = self._add_entry(body, "Mittelungen", 4, 4, "100")
        self.msm_recovery_eq = ctk.CTkCheckBox(body, text="Recovery-Zeit = Stresszeit",
                                               command=lambda: self._update_msm("recovery_eq"))
        self.msm_recovery_eq.grid(row=5, column=0, columnspan=3, padx=10, pady=8, sticky="w")
        self.msm_recovery_eq.select()
        self.msm_initial = ctk.CTkCheckBox(body, text="Referenzmessung vor erstem Stress")
        self.msm_initial.grid(row=5, column=3, columnspan=3, padx=10, pady=8, sticky="w")
        self.msm_initial.select()
        # Sweep für Messart IDVG (Drain = Lese-Drain), nur bei IDVG sichtbar
        self.msm_sweep_frame, self.msm_sweep = self._add_sweep_frame(
            body, 6, 6, "ID-VG-Sweep in der Messphase (Drain = Lese-Drain)", with_drain=False)
        self.msm_info = self._info_label(body, 7, 6)
        self._add_control_footer(body, 8, 6, "MSM")
        self._add_plot_placeholder(tab, "MSM-Diagramm (je Zyklus eine Kurve)\n\n(noch ohne Funktion)")
        self.msm_type.configure(command=lambda _v: self._update_msm("type"))
        self._bind_update(f, ("cycles", "start", "factor", "recovery", "total"), self._update_msm)
        self._update_msm("cycles")

    def _update_msm(self, source):
        f = self.msm_fields
        transient = self.msm_type.get() == "TRANSIENT"
        recovery_eq = bool(self.msm_recovery_eq.get())
        # Recovery-Zeit wird laut Befehlsreferenz nur bei TRANSIENT und
        # nur bei MSM_RECOVERY_STRESS_TIME= FALSE verwendet
        self._set_enabled(f["recovery"], transient and not recovery_eq)
        # Messart IDVG: Lese-Gate wird nicht gebraucht, dafür der Sweep (Kap. 8.5)
        idvg = self.msm_type.get() == "IDVG"
        self._set_enabled(f["read_vg"], not idvg)
        if hasattr(self, "msm_sweep_frame"):
            if idvg:
                self.msm_sweep_frame.grid()
            else:
                self.msm_sweep_frame.grid_remove()
        try:
            start, factor = self._num(f["start"]), self._num(f["factor"])
            if start <= 0 or factor <= 0:
                return
            if source == "total":
                total = self._num(f["total"])
                if total <= 0:
                    return
                if abs(factor - 1) < 1e-12:
                    cycles = total / start
                else:
                    cycles = math.log(1 + total * (factor - 1) / start) / math.log(factor)
                cycles = max(1, round(cycles))
                self._put(f["cycles"], cycles)
            else:
                cycles = max(1, int(self._num(f["cycles"])))
            stress_times = [start * factor ** k for k in range(cycles)]
            total = sum(stress_times)
            if source != "total":
                self._put(f["total"], total)
            recovery_fixed = self._num(f["recovery"]) if f["recovery"].get().strip() else 0.0
        except (ValueError, OverflowError):
            return

        if not transient:
            recovery_total = 0.0
        elif recovery_eq:
            recovery_total = total
        else:
            recovery_total = cycles * recovery_fixed

        shown = " · ".join(self._fmt_duration(t / 1000) for t in stress_times[:6])
        if cycles > 6:
            shown += " · …"
        self.msm_info.configure(
            text=f"Stresszeiten je Zyklus: {shown}\n"
                 f"Stress gesamt {self._fmt_duration(total / 1000)} + Recovery "
                 f"{self._fmt_duration(recovery_total / 1000)} ≈ "
                 f"{self._fmt_duration((total + recovery_total) / 1000)} (ohne Messzeiten)"
        )

    def _build_temp_tab(self, tab):
        body = self._make_param_box(tab, 4)
        ctk.CTkLabel(
            body,
            text="Warten auf thermisches Gleichgewicht (Temp_equilibrium_wait)",
        ).grid(row=0, column=0, columnspan=4, padx=10, pady=8, sticky="w")
        self._add_control_footer(body, 1, 4, "Temperatur")
        self._add_plot_placeholder(tab, "Temperaturverlauf\n\n(noch ohne Funktion)")

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

    # ==================================================================
    # Einstellungen an das FETCH-System senden
    # Reihenfolge und Format laut Befehlsreferenz_Python_PC.md:
    #   Grund-Block (Kap. 5) -> Parameter der Messart -> Start-Befehl als
    #   LETZTE Zeile (Kap. 4). Format "NAME= wert", Dezimalpunkt,
    #   Zeiten in ms als ganze Zahl (Firmware liest sie mit strtoul).
    # ==================================================================
    SENSE_RANGES = {"100 nA": 0, "10 µA": 1}     # SENSE_RANGE= 0 / 1
    START_FLAGS_OFF = [
        "SENSE_MODE_IDVG= FALSE",
        "SENSE_MODE_TRANSIENT= FALSE",
        "STRESS_OUTput= OFF",
        "Temp_equilibrium_wait= FALSE",
        "SENSE_MODE_MSM= FALSE",
    ]

    def _add_control_footer(self, parent, row, columnspan, tab_name):
        """Buttons Parameter senden / Starten / Stopp + Statuszeile für einen Reiter."""
        bar = ctk.CTkFrame(parent, fg_color="transparent")
        bar.grid(row=row, column=0, columnspan=columnspan, padx=8, pady=(12, 4), sticky="ew")
        for col in range(3):
            bar.grid_columnconfigure(col, weight=1)
        ctk.CTkButton(bar, text="ⓘ Info", width=80, fg_color=App.SECONDARY,
                      command=lambda: self._show_measure_info(tab_name)).grid(
            row=0, column=3, padx=5, pady=4)
        ctk.CTkButton(bar, text="Parameter senden",
                      command=lambda: self._send_tab(tab_name, start=False)).grid(
            row=0, column=0, padx=5, pady=4, sticky="ew")
        ctk.CTkButton(bar, text=f"{tab_name} starten",
                      command=lambda: self._send_tab(tab_name, start=True)).grid(
            row=0, column=1, padx=5, pady=4, sticky="ew")
        ctk.CTkButton(bar, text="Stopp (ABORT)", command=lambda: self._abort(tab_name),
                      **App.DANGER).grid(row=0, column=2, padx=5, pady=4, sticky="ew")
        status = ctk.CTkLabel(parent, text="", text_color=App.MUTED, justify="left",
                              anchor="w", wraplength=700)
        status.grid(row=row + 1, column=0, columnspan=columnspan, padx=10, pady=(0, 8), sticky="w")
        self.tab_status[tab_name] = status

    def _add_sweep_frame(self, parent, row, columnspan, title, with_drain=True):
        """Unterbereich mit Gate-Sweep-Feldern (für Nachmessung / MSM)."""
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, columnspan=columnspan, padx=8, pady=4, sticky="ew")
        for col in range(4):
            frame.grid_columnconfigure(col, weight=1)
        ctk.CTkLabel(frame, text=title, font=(App.FONT, 13, "bold")).grid(
            row=0, column=0, columnspan=4, padx=10, pady=(6, 0), sticky="w")
        f = {}
        if with_drain:
            f["vd"] = self._add_entry(frame, "Drain-Spannung (V)", 1, 0, "0.1")
        f["start"] = self._add_entry(frame, "Gate Start (V)", 1, 2 if with_drain else 0, "0")
        f["stop"] = self._add_entry(frame, "Gate Stop (V)", 2 if with_drain else 1, 0 if with_drain else 2, "2.5")
        f["step"] = self._add_entry(frame, "Gate Schrittweite (V)", 2, 2 if with_drain else 0, "0.05")
        f["settle"] = self._add_entry(frame, "Einschwingzeit/Schritt (ms)", 3 if with_drain else 2,
                                      0 if with_drain else 2, "5")
        return frame, f

    def _add_bias_frame(self, parent, row, columnspan, title):
        """Unterbereich mit fester Gate- und Drain-Spannung (Nachmessung Transient)."""
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, columnspan=columnspan, padx=8, pady=4, sticky="ew")
        for col in range(4):
            frame.grid_columnconfigure(col, weight=1)
        ctk.CTkLabel(frame, text=title, font=(App.FONT, 13, "bold")).grid(
            row=0, column=0, columnspan=4, padx=10, pady=(6, 0), sticky="w")
        f = {
            "vg": self._add_entry(frame, "Gate-Spannung (V)", 1, 0, "1.5"),
            "vd": self._add_entry(frame, "Drain-Spannung (V)", 1, 2, "0.1"),
        }
        ctk.CTkLabel(frame, text="Hinweis: Mit beiden Nachmessungen gibt es nur eine Drain-Spannung "
                                 "(SOURce2_VOLTage) – es gilt dieser Wert.",
                     text_color=App.MUTED).grid(row=2, column=0, columnspan=4, padx=10, pady=(0, 6), sticky="w")
        return frame, f

    # ---------- Werte lesen und formatieren ----------
    def _val(self, entry, name, positive=False, integer=False, allow_zero=True):
        text = entry.get().strip().replace(",", ".")
        try:
            value = float(text)
        except ValueError:
            raise ValueError(f"„{name}“ ist keine Zahl ({text or 'leer'}).")
        if positive and (value < 0 or (value == 0 and not allow_zero)):
            raise ValueError(f"„{name}“ muss größer als 0 sein.")
        if integer:
            if abs(value - round(value)) > 1e-9:
                raise ValueError(f"„{name}“ muss eine ganze Zahl sein.")
            return int(round(value))
        return value

    @staticmethod
    def _num_text(value):
        """Zahl für die Firmware: Dezimalpunkt, keine Exponentenschreibweise."""
        if isinstance(value, int):
            return str(value)
        text = f"{value:.6f}".rstrip("0").rstrip(".")
        return "0" if text in ("-0", "") else text

    def _base_block(self, range_option, avg_entry):
        """Grund-Block (Befehlsreferenz Kap. 5): kommt vor jeder Messart."""
        avg = self._val(avg_entry, "Mittelungen", positive=True, integer=True, allow_zero=False)
        return [
            f"SENSE_RANGE= {self.SENSE_RANGES[range_option.get()]}",
            "SENSE_AUTORANGE= OFF",
            f"SENSE_MODE_AVERAGE= {avg}",
            "SENSE_MODE_GND= OFF",          # TIA-Eingang ans DUT (beim Start liegt er auf GND)
        ] + self.START_FLAGS_OFF

    def _idvg_sweep_commands(self, f=None, drain_entry=None):
        """Drain fix + Gate-Sweep (Kap. 6.1). Standard: Felder des Reiters ID-VG."""
        f = f or self.idvg_fields
        drain_entry = drain_entry or f["vd"]
        start = self._val(f["start"], "Gate Start")
        stop = self._val(f["stop"], "Gate Stop")
        step = self._val(f["step"], "Gate Schrittweite", positive=True, allow_zero=False)
        if start == stop:
            raise ValueError("Gate Start und Gate Stop sind gleich.")
        return [
            f"SOURce2_VOLTage= {self._num_text(self._val(drain_entry, 'Drain-Spannung'))}",
            f"SOURce1_Sweep_Start= {self._num_text(start)}",
            f"SOURce1_Sweep_Stop= {self._num_text(stop)}",
            f"SOURce1_Sweep_Step= {self._num_text(step)}",
            f"SOURce1_Sweep_TIme= {self._num_text(self._val(f['settle'], 'Einschwingzeit', positive=True))}",
        ]

    TR_MAX_POINTS = 5000            # Puffer in der Firmware (BUF_MAX)
    TR_MAX_DT_US = 32_767_500       # TIM3: max. 32,7 s pro Punkt

    def _transient_timing_commands(self):
        """Samplerate, Punktanzahl, Einschwingzeit des Transienten (Felder im Reiter Transient)."""
        rate = self._val(self.sample_rate_entry, "Sample Rate", positive=True, allow_zero=False)
        dt_us = round(1e6 / rate)
        if not 2 <= dt_us <= self.TR_MAX_DT_US:
            raise ValueError(f"„Sample Rate“ muss zwischen {1e6 / self.TR_MAX_DT_US:.3g} Hz "
                             f"und 500 kHz liegen.")
        points = self._val(self.points_entry, "Messpunktanzahl", positive=True, integer=True,
                           allow_zero=False)
        if points > self.TR_MAX_POINTS:
            raise ValueError(f"„Messpunktanzahl“ max. {self.TR_MAX_POINTS} (Puffer der Firmware).")
        settle = self._val(self.transient_settle, "Einschwingzeit", positive=True, integer=True)
        return [
            f"SENSE_TRANSIENT_DT_US= {dt_us}",
            f"SENSE_TRANSIENT_POINTS= {points}",
            f"SENSE_TRANSIENT_SETTLE= {settle}",
        ]

    def _fixed_bias_commands(self, gate_entry, drain_entry, what):
        """Gate und Drain fix (Transient, Lesespannung bei MSM)."""
        vg = self._val(gate_entry, f"Gate-Spannung ({what})")
        vd = self._val(drain_entry, f"Drain-Spannung ({what})")
        return [f"SOURce1_VOLTage= {self._num_text(vg)}", f"SOURce2_VOLTage= {self._num_text(vd)}"]

    # ---------- Befehlsfolgen je Messart ----------
    def _build_commands(self, tab):
        """Gibt (Parameter-Befehle, Start-Befehl) zurück oder wirft ValueError."""
        if tab == "ID-VG":
            cmds = self._base_block(self.idvg_range, self.idvg_fields["avg"])
            cmds += self._idvg_sweep_commands()
            return cmds, "SENSE_MODE_IDVG= TRUE"

        if tab == "Transient":
            cmds = self._base_block(self.transient_range, self.transient_avg)
            cmds += self._fixed_bias_commands(self.gate_voltage_entry, self.drain_voltage_entry, "Transient")
            cmds += self._transient_timing_commands()
            return cmds, "SENSE_MODE_TRANSIENT= TRUE"

        if tab == "Stress":
            after_idvg = bool(self.stress_after_idvg.get())
            after_transient = bool(self.stress_after_transient.get())
            f = self.stress_fields
            cmds = self._base_block(self.stress_range, f["avg"])
            if after_idvg:
                cmds += self._idvg_sweep_commands(self.stress_sweep)
            if after_transient:
                cmds += self._fixed_bias_commands(self.stress_bias["vg"], self.stress_bias["vd"],
                                                  "Nachmessung Transient")
                # Samplerate/Punkte/Einschwingzeit aus dem Reiter "Transient"
                cmds += self._transient_timing_commands()
            stress_type = self.stress_type.get()
            vd = self._val(f["vd"], "Drain-Stressspannung")
            if stress_type == "BTI":
                vd = 0.0                  # BTI: nur Gate, Drain = 0 V (Kap. 3.3)
            cmds += [
                f"STRESS_TYPE= {stress_type}",
                f"STRESS_MODE= {self.stress_mode.get()}",
                f"STRESS_VOLTage= {self._num_text(self._val(f['vg'], 'Gate-Stressspannung'))}",
                f"STRESS_DRAIN_VOLTage= {self._num_text(vd)}",
            ]
            if self.stress_mode.get() == "STATIC":
                cmds.append(f"STRESS_TIME= {self._val(f['time'], 'Stressdauer', positive=True, integer=True, allow_zero=False)}")
            else:
                cmds += [
                    f"STRESS_ON_TIME= {self._val(f['on'], 'On-Zeit', positive=True, integer=True, allow_zero=False)}",
                    f"STRESS_OFF_TIME= {self._val(f['off'], 'Off-Zeit', positive=True, integer=True)}",
                    f"STRESS_CYCLES= {self._val(f['cycles'], 'Zyklen', positive=True, integer=True, allow_zero=False)}",
                ]
            cmds += [
                f"STRESS_AFTER_IDVG= {'TRUE' if after_idvg else 'FALSE'}",
                f"STRESS_AFTER_TRANSIENT= {'TRUE' if after_transient else 'FALSE'}",
            ]
            return cmds, "STRESS_OUTput= ON"

        if tab == "MSM":
            f = self.msm_fields
            meas_type = self.msm_type.get()
            stress_type = self.msm_stress_type.get()
            vd_stress = self._val(f["vd"], "Drain-Stress")
            if stress_type == "BTI":
                vd_stress = 0.0
            cmds = self._base_block(self.msm_range, f["avg"])
            cmds += [
                f"STRESS_TYPE= {stress_type}",
                "STRESS_MODE= STATIC",       # Zeiten kommen aus MSM_* (Kap. 8)
                f"STRESS_VOLTage= {self._num_text(self._val(f['vg'], 'Gate-Stress'))}",
                f"STRESS_DRAIN_VOLTage= {self._num_text(vd_stress)}",
                f"MSM_CYCLES= {self._val(f['cycles'], 'Zyklen', positive=True, integer=True, allow_zero=False)}",
                f"MSM_START_TIME= {self._val(f['start'], 'Startzeit', positive=True, integer=True, allow_zero=False)}",
                f"MSM_TIME_FACTOR= {self._num_text(self._val(f['factor'], 'Zeitfaktor', positive=True, allow_zero=False))}",
                f"MSM_MEAS_DELAY= {self._val(f['delay'], 'Mess-Verzögerung', positive=True, integer=True)}",
                f"MSM_INITIAL_MEASURE= {'TRUE' if self.msm_initial.get() else 'FALSE'}",
                f"MSM_MAX_POINTS= {self._val(f['maxpts'], 'Max. Punkte', positive=True, integer=True, allow_zero=False)}",
            ]
            # Lesespannungen: SPOT/TRANSIENT fix, IDVG über die Sweep-Parameter (Kap. 8.5)
            if meas_type == "IDVG":
                cmds += self._idvg_sweep_commands(self.msm_sweep, drain_entry=f["read_vd"])
            else:
                cmds += self._fixed_bias_commands(f["read_vg"], f["read_vd"], "MSM-Lesespannung")
            cmds.append(f"MSM_MEAS_TYPE= {meas_type}")
            if meas_type == "TRANSIENT":
                recovery_eq = bool(self.msm_recovery_eq.get())
                cmds.append(f"MSM_RECOVERY_STRESS_TIME= {'TRUE' if recovery_eq else 'FALSE'}")
                if not recovery_eq:
                    rec = self._val(f["recovery"], "Recovery-Zeit", positive=True, integer=True, allow_zero=False)
                    cmds.append(f"MSM_RECOVERY_TIME= {rec}")
            return cmds, "SENSE_MODE_MSM= TRUE"

        if tab == "Temperatur":
            # Kap. 4: Temperatur-Wartezeit allein starten, andere Start-Flags aus
            return list(self.START_FLAGS_OFF[:3]) + ["SENSE_MODE_MSM= FALSE"], "Temp_equilibrium_wait= TRUE"

        raise ValueError(f"Unbekannte Messart {tab}")

    # ---------- Senden / Stoppen ----------
    def _send_tab(self, tab, start):
        status = self.tab_status[tab]
        if not self.instrument.connected:
            status.configure(text="Bitte zuerst links den COM-Port verbinden.")
            return
        if self.instrument.busy:
            status.configure(text="Es wird gerade noch gesendet – bitte kurz warten.")
            return
        try:
            commands, start_command = self._build_commands(tab)
        except ValueError as exc:
            status.configure(text=f"Nicht gesendet – ungültige Eingabe: {exc}")
            return
        if start:
            commands = commands + [start_command]     # Start-Befehl immer als letzte Zeile
            self.run_ctx = self._make_run_ctx(tab, commands)
        self.instrument.send_sequence(commands, tag=(tab, start, start_command))
        duration = len(commands) * self.instrument.COMMAND_DELAY_S
        status.configure(text=f"Sende {len(commands)} Befehle (≈ {duration:.1f} s) …")

    # ---------- Empfangene Datenblöcke speichern ----------
    def _make_run_ctx(self, tab, commands):
        """Alles, was zum Benennen/Speichern der folgenden Datenblöcke nötig ist."""
        start = datetime.now()
        device = dateinamen.clean(self.device_entries[tab].get())
        folder = Path(self.save_path_entries[tab].get().strip() or MEASUREMENT_DIR)
        params = messdaten.commands_to_params(commands)
        stress_ms = None
        if tab == "Stress":
            if params.get("STRESS_MODE") == "STATIC":
                stress_ms = int(params["STRESS_TIME"])
            else:
                stress_ms = int(params["STRESS_ON_TIME"]) * int(params["STRESS_CYCLES"])
        return {"tab": tab, "device": device, "folder": folder, "start": start,
                "run_id": f"{start:%Y%m%d-%H%M%S}_{device}", "params": params,
                "stress_ms": stress_ms}

    def _handle_block(self, hdr, raw):
        ctx = getattr(self, "run_ctx", None)
        if ctx is None:
            start = datetime.now()
            ctx = {"tab": "", "device": "unbenannt", "folder": MEASUREMENT_DIR, "start": start,
                   "run_id": f"{start:%Y%m%d-%H%M%S}_unbenannt", "params": {}, "stress_ms": None}
            self.instrument.log_queue.put(("SYSTEM", "Datenblock ohne Start aus der GUI – "
                                                     "wird als 'unbenannt' gespeichert."))
        p = ctx["params"]
        typ = hdr["TYPE"]
        msm = typ.startswith("MSM") or ctx["tab"] == "MSM"
        stress_type = p.get("STRESS_TYPE") if ctx["tab"] in ("Stress", "MSM") else None
        try:
            name = dateinamen.make_name(
                typ, ctx["device"], ctx["start"],
                int(p.get("SENSE_RANGE", hdr["RANGE"])),
                stress_type=stress_type,
                stress_v=float(p["STRESS_VOLTage"]) if stress_type else None,
                t_stress_ms=hdr["T_STRESS_MS"] if msm else ctx["stress_ms"],
                cycle=hdr["CYCLE"] if msm else None,
                read_vg=(float(p["SOURce1_VOLTage"])
                         if typ == "TRANSIENT" and not stress_type and "SOURce1_VOLTage" in p
                         else None),
            )
            path = dateinamen.make_path(ctx["folder"], ctx["device"], name)
            messdaten.save_block(path, hdr, raw, ctx)
        except (RuntimeError, OSError, KeyError, ValueError) as exc:
            self.instrument.log_queue.put(("ERROR", f"Speichern fehlgeschlagen: {exc}"))
            return
        self.instrument.log_queue.put(("SYSTEM", f"Gespeichert: {path}"))
        status = self.tab_status.get(ctx["tab"])
        if status is not None:
            status.configure(text=f"✓ Gespeichert: {path.name}")

    def _sequence_done(self, tag, ok, sent, total):
        tab, start, start_command = tag
        status = self.tab_status.get(tab)
        if status is None:
            return
        if start == "abort":
            text = ("✓ ABORT gesendet und alle Start-Flags zurückgesetzt." if ok
                    else "✗ ABORT gesendet, Zurücksetzen der Start-Flags unvollständig.")
        elif ok:
            text = f"✓ {sent} Befehle gesendet"
            text += f", zuletzt Start: {start_command}" if start else " (ohne Start-Befehl)"
            text += ". Die Firmware bestätigt Befehle nicht – Details im Log."
        else:
            text = f"✗ Abgebrochen nach {sent} von {total} Befehlen."
        status.configure(text=text)

    def _abort(self, tab):
        """ABORT + alle Start-Flags zurücksetzen (Firmware setzt sie noch nicht
        selbst zurück, Befehlsreferenz Kap. 4)."""
        status = self.tab_status[tab]
        if not self.instrument.connected:
            status.configure(text="Bitte zuerst links den COM-Port verbinden.")
            return
        self.instrument.abort()

        def reset_flags(attempt=0):
            # eine evtl. laufende Befehlsfolge bricht zwischen zwei Befehlen ab
            if not self.instrument.send_sequence(self.START_FLAGS_OFF, tag=(tab, "abort", "")):
                if attempt < 20:
                    self.after(100, reset_flags, attempt + 1)

        self.after(100, reset_flags)
        status.configure(text="ABORT gesendet, Start-Flags werden zurückgesetzt …")

    # ==================================================================
    # Serielle Konsole mit Autofill
    # ==================================================================
    def _build_console_view(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=1, column=1, padx=(5, 10), pady=10, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        self.console_frame = frame

        ctk.CTkLabel(frame, text="Serielle Konsole", font=(App.FONT, 20, "bold")).grid(
            row=0, column=0, padx=15, pady=(12, 0), sticky="w"
        )
        ctk.CTkLabel(
            frame,
            text="Tab = vervollständigen · ↑/↓ = Vorschlag bzw. Verlauf · Enter = senden · Esc = Vorschläge schließen",
            text_color=App.MUTED,
        ).grid(row=0, column=0, padx=15, pady=(12, 0), sticky="e")

        self.console_log = ctk.CTkTextbox(frame, wrap="word", font=("Consolas", 13))
        self.console_log.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")
        self.console_log.insert("end", "Befehle im Format  NAME= wert  eingeben, z. B.  SOURce1_VOLTage= 1.5\n")
        self.console_log.configure(state="disabled")

        input_row = ctk.CTkFrame(frame, fg_color="transparent")
        input_row.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="ew")
        input_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(input_row, text=">", font=("Consolas", 16, "bold")).grid(row=0, column=0, padx=(0, 6))
        self.console_entry = ctk.CTkEntry(
            input_row, font=("Consolas", 14), placeholder_text="Befehl eingeben …"
        )
        self.console_entry.grid(row=0, column=1, sticky="ew")
        ctk.CTkButton(input_row, text="Senden", width=90, command=self._console_send).grid(
            row=0, column=2, padx=(6, 0)
        )
        ctk.CTkButton(
            input_row, text="ABORT", width=80, command=lambda: self._console_send("ABORT"), **App.DANGER
        ).grid(row=0, column=3, padx=(6, 0))
        ctk.CTkButton(
            input_row, text="Leeren", width=80, fg_color=App.SECONDARY, command=self._console_clear
        ).grid(row=0, column=4, padx=(6, 0))

        # Vorschlagsliste: schwebt direkt über dem Eingabefeld
        self.suggestion_box = ctk.CTkFrame(frame, border_width=1)
        self._suggestions = []
        self._suggestion_index = -1
        self._history = []
        self._history_index = 0

        e = self.console_entry
        e.bind("<KeyRelease>", self._on_console_key)
        e.bind("<Tab>", self._on_console_tab)
        e.bind("<Return>", self._on_console_return)
        e.bind("<Up>", lambda _ev: self._on_console_arrow(-1))
        e.bind("<Down>", lambda _ev: self._on_console_arrow(+1))
        e.bind("<Escape>", lambda _ev: self._hide_suggestions())

    # ---------- Ausgabe ----------
    def _console_append(self, line):
        if not hasattr(self, "console_log"):
            return
        self.console_log.configure(state="normal")
        self.console_log.insert("end", line + "\n")
        self.console_log.see("end")
        self.console_log.configure(state="disabled")

    def _console_clear(self):
        self.console_log.configure(state="normal")
        self.console_log.delete("1.0", "end")
        self.console_log.configure(state="disabled")

    # ---------- Senden ----------
    def _console_send(self, command=None):
        if command is None:
            command = self.console_entry.get().strip()
            self.console_entry.delete(0, "end")
        self._hide_suggestions()
        if not command:
            return
        if not self._history or self._history[-1] != command:
            self._history.append(command)
        self._history_index = len(self._history)

        if not scpi_commands.is_known(command):
            self._console_append(
                f"HINWEIS: '{command.partition('=')[0].strip()}' ist kein bekannter Befehl – "
                "die Firmware ignoriert ihn ohne Meldung."
            )
        if not self.instrument.connected:
            self._console_append("FEHLER: Nicht verbunden. Links COM-Port wählen und verbinden.")
            return
        if not self.instrument.send(command):
            self._console_append("FEHLER: Senden fehlgeschlagen (Details im Terminal).")

    # ---------- Tastatur ----------
    def _on_console_key(self, event):
        if event.keysym in ("Up", "Down", "Tab", "Return", "Escape", "ISO_Left_Tab"):
            return
        self._update_suggestions()

    def _on_console_tab(self, _event):
        if self._suggestions:
            index = max(self._suggestion_index, 0)
            self._accept_suggestion(index)
        return "break"  # Fokus nicht weiterspringen lassen

    def _on_console_return(self, _event):
        if self._suggestions and self._suggestion_index >= 0:
            self._accept_suggestion(self._suggestion_index)
        else:
            self._console_send()
        return "break"

    def _on_console_arrow(self, step):
        if self._suggestions:
            count = len(self._suggestions)
            self._suggestion_index = (self._suggestion_index + step) % count
            self._render_suggestions()
        elif self._history:
            # Befehlsverlauf wie in einer Kommandozeile
            self._history_index = min(max(self._history_index + step, 0), len(self._history))
            text = self._history[self._history_index] if self._history_index < len(self._history) else ""
            self.console_entry.delete(0, "end")
            self.console_entry.insert(0, text)
        return "break"

    # ---------- Vorschläge ----------
    def _update_suggestions(self):
        self._suggestions = scpi_commands.suggestions(self.console_entry.get())
        self._suggestion_index = -1
        if self._suggestions:
            self._render_suggestions()
        else:
            self._hide_suggestions()

    def _render_suggestions(self):
        for widget in self.suggestion_box.winfo_children():
            widget.destroy()
        self.suggestion_box.grid_columnconfigure(0, weight=1)
        for i, (text, hint) in enumerate(self._suggestions):
            selected = i == self._suggestion_index
            row = ctk.CTkButton(
                self.suggestion_box,
                text=f"{text:<32} {hint}",
                anchor="w",
                font=("Consolas", 13),
                height=24,
                corner_radius=0,
                border_width=0,
                fg_color=App.SELECT if selected else "transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray80", "gray30"),
                command=lambda k=i: self._accept_suggestion(k),
            )
            row.grid(row=i, column=0, padx=2, pady=0, sticky="ew")
        self.suggestion_box.place(
            in_=self.console_entry, relx=0, rely=0, y=-2, anchor="sw", relwidth=1
        )
        self.suggestion_box.lift()

    def _hide_suggestions(self):
        self._suggestions = []
        self._suggestion_index = -1
        if hasattr(self, "suggestion_box"):
            self.suggestion_box.place_forget()

    def _accept_suggestion(self, index):
        text = self._suggestions[index][0]
        self.console_entry.delete(0, "end")
        self.console_entry.insert(0, text)
        self.console_entry.icursor("end")
        self.console_entry.focus_set()
        # Nach dem Namen gleich die möglichen Werte vorschlagen (ON/OFF, TRUE/FALSE …)
        self._update_suggestions()

    def process_communication_log(self):
        """Move queued serial log messages into the GUI on Tk's main thread."""
        try:
            while True:
                kind, message = self.instrument.log_queue.get_nowait()
                if kind == "DONE":
                    self._sequence_done(*message)
                    continue
                if kind == "BLOCK":
                    self._handle_block(*message)
                    continue
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
                self._console_append(f"[{timestamp}] {label}: {message}")

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


def vorverarbeitung_fmt(f):
    return f"{f / 1000:.3g} kHz" if f >= 1000 else f"{f:.3g} Hz"
