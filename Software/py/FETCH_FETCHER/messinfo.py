"""Info-Texte für die Mess-Reiter (Knopf "Info" neben Parameter senden).

Quelle der Befehle/Standardwerte: Befehlsreferenz_Python_PC.md (Software/py).
"""

GRUNDBLOCK = """\
Gilt für alle Messarten (Grund-Block, Befehlsreferenz Kap. 5)
  Strombereich   Standard 100 nA (Rf 10 MΩ)   -> SENSE_RANGE= 0
                 10 µA (Rf 100 kΩ)            -> SENSE_RANGE= 1
                 100 nA für kleine Ströme (unterschwellig, RTN), 10 µA wenn der
                 Strom größer wird (sonst übersteuert der TIA).
                 Autorange ist immer aus, der Bereich bleibt fest.
  Mittelungen    Standard 100 -> SENSE_MODE_AVERAGE= 100
                 Jeder Messpunkt = Mittelwert aus N ADC-Werten. Rauschen sinkt
                 etwa mit 1/√N (100 -> ca. 10x weniger), dafür dauert jeder Punkt
                 länger. Bei RTN: zu viele Mittelungen verschmieren schnelle Sprünge.
  Ablauf         Erst alle Parameter, dann als letzte Zeile genau EIN Start-Befehl.
                 Die Firmware stellt beim Start Relais (200 ms) und 1 s Wartezeit ein.
  Stopp (ABORT)  Bricht sofort ab und setzt alle Start-Flags auf FALSE/OFF.
"""

INFO = {
"ID-VG": """\
ID-VG – Übertragungskennlinie
═════════════════════════════
Die Drain-Spannung bleibt fest, die Gate-Spannung wird in Schritten von Start
bis Stop gefahren. Bei jedem Schritt wird der Drain-Strom gemessen.
Daraus: Schwellspannung Vth, Subthreshold-Swing, Steilheit gm.
Vergleich vorher/nachher Stress -> Verschiebung ΔVth (Degradation).

Parameter                      Standard   Befehl / Erklärung
Drain-Spannung (V)             0.1        SOURce2_VOLTage. Klein = linearer Bereich,
                                          belastet den Transistor kaum (kein HCD).
Gate Start (V)                 0          SOURce1_Sweep_Start
Gate Stop (V)                  2.5        SOURce1_Sweep_Stop (2.5 V = aktueller DAC-Bereich)
Gate Schrittweite (V)          0.05       SOURce1_Sweep_Step -> 51 Punkte
Messpunkte                     (berechnet) wird aus Start/Stop/Schritt gerechnet und
                                          umgekehrt; nur Hilfe, wird nicht gesendet.
Einschwingzeit/Schritt (ms)    5          SOURce1_Sweep_TIme. Wartezeit nach jedem
                                          Spannungsschritt (Empfehlung 5 ms).
Strombereich                   100 nA     siehe unten
Mittelungen                    100        siehe unten

Gestartet mit: SENSE_MODE_IDVG= TRUE
Dauer ≈ Punkte × (Einschwingzeit + Messzeit): 51 × ≈ 6 ms ≈ 0,3 s

Quellen
  Befehlsreferenz_Python_PC.md Kap. 3.1, 6.1
  D. K. Schroder, Semiconductor Material and Device Characterization, 3. Aufl.,
  Wiley 2006, Kap. 4 (Vth-Bestimmung aus ID-VG)
""",

"Transient": """\
Transient – Strom über der Zeit
═══════════════════════════════
Gate und Drain bleiben fest, der Drain-Strom wird über die Zeit aufgezeichnet.
Damit sieht man RTN (Sprünge zwischen zwei/mehreren Stromniveaus durch einzelne
Traps) und Drift/Recovery nach einem Stress.

Parameter                      Standard   Befehl / Erklärung
Sample Rate (Hz)               1000       Messpunkte pro Sekunde
Measure Time (s)               10         Gesamtdauer
Messpunktanzahl                10000      = Rate × Zeit; die drei Felder rechnen
                                          sich gegenseitig nach.
                                          ACHTUNG: noch kein Firmware-Befehl, werden
                                          nicht gesendet (Befehlsreferenz Kap. 6.2).
Gate-Spannung / Source 1 (V)   0          SOURce1_VOLTage. Für RTN eine Gate-Spannung
                                          nahe Vth wählen (z. B. 1.5 V), bei 0 V
                                          ist der Transistor aus.
Drain-Spannung / Source 2 (V)  0.1        SOURce2_VOLTage. Klein halten (linearer
                                          Bereich, kein zusätzlicher Stress).
Strombereich                   100 nA     RTN-Stufen sind klein -> 100 nA
Mittelungen                    100        siehe unten

Gestartet mit: SENSE_MODE_TRANSIENT= TRUE

Quellen
  Befehlsreferenz_Python_PC.md Kap. 3.1, 6.2
  T. Grasser (Hrsg.), Bias Temperature Instability for Devices and Circuits,
  Springer 2014 (RTN / einzelne Defekte)
""",

"Stress": """\
Stress – Transistor gezielt altern lassen
═════════════════════════════════════════
Eine erhöhte Spannung wird für eine bestimmte Zeit angelegt. Dadurch entstehen
bzw. laden sich Defekte im Gateoxid -> Vth verschiebt sich.
  BTI (Bias Temperature Instability): nur Gate-Spannung, Drain = 0 V.
  HCD (Hot Carrier Degradation): Gate UND Drain, Strom fließt -> heiße Ladungsträger.
Optional wird direkt danach ID-VG und/oder Transient gemessen.

Parameter                      Standard   Befehl / Erklärung
Stress-Typ                     BTI        STRESS_TYPE (BTI / HCD)
Stress-Modus                   STATIC     STRESS_MODE. STATIC = Dauerstress,
                                          DYNAMIC = gepulst (On/Off)
Gate-Stressspannung (V)        5.0        STRESS_VOLTage
Drain-Stressspannung (V)       0          STRESS_DRAIN_VOLTage, nur HCD.
                                          Bei BTI wird immer 0 gesendet.
Stressdauer (ms)               60000      STRESS_TIME, nur STATIC (60 s)
Zyklen (dynamisch)             600        STRESS_CYCLES, nur DYNAMIC
On-Zeit (ms)                   100        STRESS_ON_TIME, nur DYNAMIC
Off-Zeit (ms)                  100        STRESS_OFF_TIME, nur DYNAMIC
                                          -> 600 × 200 ms = 120 s, davon 60 s Stress
Strombereich / Mittelungen     100 nA/100 für die Nachmessung
Danach ID-VG messen            aus        STRESS_AFTER_IDVG + Sweep-Parameter
Danach Transient messen        aus        STRESS_AFTER_TRANSIENT + Gate/Drain fix
                                          (Standard 1.5 V / 0.1 V)

Gestartet mit: STRESS_OUTput= ON  (nicht zusätzlich SENSE_MODE_IDVG)

ACHTUNG HCD: hohe Drain-Spannung bei leitendem Kanal -> großer Strom, kann TIA
und Drain-Treiber beschädigen. Strombereich und Grenzen prüfen.

Quellen
  Befehlsreferenz_Python_PC.md Kap. 3.3, 7
  Dokumentation/Stressing.md
  T. Grasser et al., „The Universality of NBTI Relaxation …“, IEEE IRPS 2007
""",

"MSM": """\
MSM – Measure-Stress-Measure
════════════════════════════
Wechsel aus Stress und kurzer Messung. Die Stresszeit wächst pro Zyklus um
einen Faktor (1 s, 10 s, 100 s …). So sieht man die Degradation über viele
Zeitdekaden. Jeder Zyklus wird eine eigene Datei (c00, c01 …).

Ablauf:  [Referenz c00] -> Stress 1 s -> Messung c01 -> Stress 10 s -> c02 …

Parameter                      Standard   Befehl / Erklärung
Stress-Typ                     BTI        STRESS_TYPE (BTI: Drain-Stress = 0)
Gate-Stress (V)                5.0        STRESS_VOLTage
Drain-Stress (V)               0          STRESS_DRAIN_VOLTage, nur HCD
Messart                        SPOT       MSM_MEAS_TYPE
                                            SPOT: 1 Messpunkt pro Zyklus
                                            IDVG: 1 Sweep pro Zyklus (Sweep-Felder)
                                            TRANSIENT: I(t) während der Recovery
Lese-Gate (V)                  1.5        SOURce1_VOLTage (nicht bei IDVG)
Lese-Drain (V)                 0.1        SOURce2_VOLTage
Zyklen                         5          MSM_CYCLES
Startzeit (ms)                 1000       MSM_START_TIME, erste Stressdauer
Zeitfaktor                     10         MSM_TIME_FACTOR -> 1/10/100/1000/10000 s
Gesamt-Stresszeit (ms)         (berechnet) 11 111 s ≈ 3 h 5 min. Eingabe hier
                                          rechnet die Zyklen zurück.
Mess-Verzögerung (ms)          1          MSM_MEAS_DELAY: Stress aus -> 1. Messwert.
                                          Kurz halten, sonst erholt sich das
                                          Bauteil schon (Recovery).
Recovery-Zeit (ms)             0          MSM_RECOVERY_TIME, nur TRANSIENT und nur
                                          wenn „Recovery = Stresszeit“ aus (> 0)
Recovery-Zeit = Stresszeit     an         MSM_RECOVERY_STRESS_TIME (nur TRANSIENT)
Referenzmessung vor 1. Stress  an         MSM_INITIAL_MEASURE -> Datei c00/ref
Max. Punkte                    5000       MSM_MAX_POINTS (nur TRANSIENT),
                                          log. verteilt. 5000 Pkt = 10 kB ≈ 0,87 s
                                          bei 115200 Baud -> Startzeit muss größer
                                          sein als die Übertragung.
Strombereich / Mittelungen     100 nA/100

Gestartet mit: SENSE_MODE_MSM= TRUE (STRESS_MODE wird fix STATIC gesendet)

Quellen
  Befehlsreferenz_Python_PC.md Kap. 3.5, 8 (Tabelle 8.5)
  B. Kaczer et al., „Ubiquitous Relaxation in BTI Stressing“, IEEE IRPS 2008
  T. Grasser et al., „The Universality of NBTI Relaxation …“, IEEE IRPS 2007
""",

"Temperatur": """\
Temperatur – auf thermisches Gleichgewicht warten
═════════════════════════════════════════════════
Die Firmware wartet, bis sich die Temperatur nicht mehr ändert. Wichtig, weil
BTI und Leckströme stark temperaturabhängig sind.

Keine Parameter.
Gestartet mit: Temp_equilibrium_wait= TRUE (die anderen Start-Flags werden
auf FALSE gesetzt). Soll vor einer Messung gewartet werden: zuerst dies,
Ende abwarten, dann die Messung starten.

Quellen
  Befehlsreferenz_Python_PC.md Kap. 3.4, 4
""",
}


def text_for(tab_name):
    """Kompletter Info-Text eines Reiters inkl. Grund-Block."""
    text = INFO.get(tab_name, f"Zu „{tab_name}“ gibt es noch keine Info.\n")
    if tab_name != "Temperatur":
        text += "\n" + GRUNDBLOCK
    return text
