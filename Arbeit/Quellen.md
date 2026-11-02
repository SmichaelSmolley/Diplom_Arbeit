# Quellen – nach Themen geordnet

Diese Übersicht ordnet die markierten Stellen aus meinen Quellen nach Themen der Diplomarbeit. Zu jedem Thema gibt es eine kurze Zusammenfassung und darunter die Belegstellen.
Seitenzahlen = gedruckte Seitenzahlen im Dokument (nicht PDF-Seiten). Kurzzeichen der Quellen siehe [Literatur](#literatur) am Ende.

---

## 1. MOSFET im Subthreshold-Betrieb (V_GS < V_th)

Auch unterhalb der Schwellspannung fließt ein kleiner Strom zwischen Drain und Source, der **Subthreshold-Strom**. Er hängt **exponentiell** von V_GS ab: In halblogarithmischer Darstellung (log I_D über V_GS) ist die Kennlinie eine Gerade. Die Größenordnung liegt typisch im **nA-Bereich**. Hu nennt 100 nA pro Transistor als „bescheidenen“ Wert für I_off. In der Praxis wird V_th oft über ein Konstantstrom-Kriterium festgelegt. I_ref liegt dabei je nach Technologie zwischen **1 nA und 200 nA**, also bewusst im Subthreshold-Bereich.

**Für die Arbeit:** Der zu messende Drainstrom liegt im Bereich pA bis einige 100 nA. Daraus ergibt sich, dass ein empfindlicher Strommessverstärker (TIA) nötig ist.

| Quelle | Seite | Kapitel | Aussage |
|---|---|---|---|
| [Hu] | S. 263 | 7.2 Subthreshold Current | Definition Subthreshold-Strom und I_off, Beispiel 100 nA pro Transistor |
| [Hu] | S. 263 | 7.2 Subthreshold Current | log I_DS über V_GS ist eine Gerade, also exponentielle Abhängigkeit |
| [Tselios] | S. 46 | 6.1.1 Transfer Characteristics | I_ref typisch 1 nA bis 200 nA, Konstantstrom-Methode für V_th und ΔV_th |

---

## 2. Defekte im MOSFET, Random Telegraph Noise (RTN) und 1/f-Rauschen

Defekte im Gate-Oxid oder an der Grenzfläche Si/SiO₂ können **einzelne Ladungsträger einfangen und wieder abgeben**. Dadurch ändern sich die Anzahl der Ladungsträger im Kanal und deren Beweglichkeit. Jede Umladung stört das Oberflächenpotential und verändert so den Drainstrom I_DS.

- **Kleine Transistoren** (kleines W×L): Oft ist nur ein Defekt aktiv. Der Strom springt zwischen zwei Niveaus (Trap leer oder besetzt). Das ist **Random Telegraph Noise (RTN)**.
- **Große Transistoren:** Viele Defekte überlagern sich. Jeder einzelne Defekt hat ein Lorentz-Spektrum (Plateau, dann Abfall mit f⁻²). Die Summe ergibt **1/f-Rauschen**.

Die Physik der Defekte ist nicht trivial. Defekte können ihr Verhalten mit der Spannung ändern (Switching Traps, Fixed Traps), zwischen stabilen und metastabilen Zuständen wechseln und sogar zufällig deaktiviert und wieder aktiviert werden.

| Quelle | Seite | Kapitel | Aussage |
|---|---|---|---|
| [Hu] | S. 235 | 6.15.3 MOSFET Flicker Noise | Ladungsträgeranzahl und Beweglichkeit schwanken. Ein Trap ergibt RTN, viele Traps ergeben 1/f-Rauschen. |
| [Tselios] | S. 52 | 6.2.3 RTN Measurements | Große Bauteile zeigen 1/f-Rauschen, kleine diskrete Stufen. Lorentz-Spektrum pro Defekt. |
| [Waltl] | S. 243–244 | I.B Requirements for Defect Spectroscopy | Große Bauteile driften gleichmäßig, kleine zeigen diskrete Stufen durch einzelne Umladungen |
| [Waltl] | S. 244 | II. Defect Characterization | Jede Umladung stört das Oberflächenpotential und moduliert I_DS. Komplexe Defekt-Physik (Switching Traps, metastabile Zustände, Deaktivierung). |

---

## 3. Degradation und Zuverlässigkeit (BTI, Oxid-Durchbruch)

Durch **Betrieb bei hohen Feldstärken und Temperaturen** werden schwache chemische Bindungen an der Grenzfläche Si/SiO₂ aufgebrochen. Dadurch entstehen Oxidladungen und neue Defekte. Die Folge ist eine **Verschiebung der Schwellspannung V_th**, und Schaltungen ändern mit der Zeit ihr Verhalten. Diese Effekte heißen zusammenfassend **Bias Temperature Instability (BTI)**. Typische Auswirkungen sind:

1. Drift der Schwellspannung V_th
2. flacherer Subthreshold Slope
3. veränderte Beweglichkeit der Ladungsträger
4. höherer On-Widerstand

Bei sehr dünnen Oxiden kommt **Tunnel-Leckstrom** dazu. Unter etwa 1,5 nm SiO₂ ist er der wichtigste begrenzende Faktor. High-k-Materialien helfen dagegen, bringen aber selbst mehr Oxidladung mit.

Der **Oxid-Durchbruch** hängt von der Belastungsdauer ab (Time-Dependent Dielectric Breakdown, TDDB). Je länger die Belastung dauert, desto niedriger ist die Durchbruchfeldstärke. Modell: Tunnelnde Ladungsträger erzeugen nach und nach Defekte im Oxid, bis an einer Stelle eine kritische Defektdichte erreicht ist.

| Quelle | Seite | Kapitel | Aussage |
|---|---|---|---|
| [Waltl] | S. 242 | I. Introduction | BTI: V_th-Drift, Subthreshold Slope, Beweglichkeit, On-Widerstand |
| [Hu] | S. 270 | 7.4 Reducing Gate-Insulator Thickness and Tunneling Leakage | Langzeitbetrieb bei hoher Feldstärke und Temperatur bricht Bindungen, das verschiebt V_t |
| [Hu] | S. 270 | 7.4 | Unter 1,5 nm SiO₂ ist Tunnel-Leckstrom der begrenzende Faktor |
| [Hu] | S. 271 | 7.4 | High-k-Dielektrika: Probleme, dünne SiO₂-Zwischenschicht |
| [Hu] | S. 271–272 | 7.4, Kasten „SiO₂ Breakdown Electric Field“ | Durchbruchfeldstärke hängt von der Testdauer ab (TDDB), Modell der kritischen Defektdichte |

---

## 4. Warum einzelne Defekte untersuchen? (Single-Defect Spectroscopy)

Bei der Untersuchung **einzelner Defekte** werden Eigenschaften sichtbar, die bei großen Bauteilen im Mittelwert verloren gehen. Dazu gehören die **räumliche Lage** der Defekte, aus der man auf ihre Herkunft und Vermeidung schließen kann, und ihr **zeitliches Verhalten** (Stabilität, Lebensdauer). Kleine Bauteile machen die Umladung einzelner Defekte als Stromstufen sichtbar. Damit lassen sich Modelle für die Spannungs- und Temperaturabhängigkeit entwickeln. Diese Stufen zu messen ist aber eine große Herausforderung für **Messauflösung und Rauschen**.

| Quelle | Seite | Kapitel | Aussage |
|---|---|---|---|
| [Tselios] | S. 7 | 1.4 Single Defect Analysis | Räumliche Lage und zeitliches Verhalten einzelner Defekte |
| [Waltl] | S. 244 | I.B Requirements | Kleine Bauteile machen einzelne Defekte messbar, das ist anspruchsvoll für Auflösung und Rauschen |
| [Waltl] | S. 245 | II. (Ende) | Ziel: Stufen mit höchster Auflösung bei vernünftiger Abtastrate messen |

---

## 5. Messmethoden

### 5.1 I_D(V_G)-Kennlinie (Transferkennlinie)
Die Gate-Spannung soll **möglichst schnell** durchgefahren werden. So ist das Oxid nur kurz belastet, und das Bauteil bleibt im Ausgangszustand („pristine state“). Aus der Kennlinie wird V_th bestimmt, meist mit dem **Konstantstrom-Kriterium** (I_D = I_ref · W/L, I_ref = 1–200 nA). Waltl wählt den Recovery-Arbeitspunkt ebenfalls über ein Konstantstrom-Kriterium (I_DS = −500 nA). So hat jedes Bauteil trotz Streuung von V_th dieselbe Oxidfeldstärke.

### 5.2 RTN-Messung
Ablauf: **Gate-Spannung konstant halten** und **I_DS mit gleichmäßiger Abtastrate** über eine bestimmte Zeit aufzeichnen. Mit der vorher gemessenen I_D(V_G)-Kennlinie wird der Strom in ein V_th-Signal umgerechnet. Aktive Defekte zeigen sich als **diskrete Stufen**.

### 5.3 Measure-Stress-Measure (MSM / eMSM)
Nach der ersten I_D(V_G)-Kennlinie wechseln sich **Stress** (hohe Gate-Spannung, Defekte werden geladen) und **Recovery** (niedrige Gate-Spannung, Defekte entladen sich) ab, mit steigender Dauer. In der Recovery-Phase wird der Strom gemessen und in ΔV_th umgerechnet. Für TDDS braucht man typisch etwa **100 Stress/Recovery-Zyklen** pro Messpunkt.

### 5.4 Konstante Gate-Spannung oder konstanter Drainstrom
- **Konstante Gate-Spannung:** Ein TIA misst den Kanalstrom. Einfach und stabil, aber der Strom muss nachträglich über die I_D(V_G)-Kennlinie in ΔV_th umgerechnet werden.
- **Konstanter Drainstrom:** Ein Regelkreis führt die Gate-Spannung nach. Änderungen von g_m und der Kennlinie werden automatisch berücksichtigt, die Umrechnung entfällt.

Die Wahl hängt von Einfachheit, Stabilität und dem zulässigen Fehler ab.

| Quelle | Seite | Kapitel | Aussage |
|---|---|---|---|
| [Tselios] | S. 46 | 6.1.1 Transfer Characteristics | Schneller Sweep, Bauteil bleibt im Ausgangszustand |
| [Tselios] | S. 46 | 6.1.1 | Konstantstrom-Methode, I_ref 1–200 nA |
| [Waltl] | S. 247 | Fig. 11 | Recovery-Bias über Konstantstrom-Kriterium (−500 nA), 65 pMOS-Transistoren |
| [Tselios] | S. 52 | 6.2.3 RTN Measurements | Ablauf der RTN-Messung, Umrechnung in V_th, diskrete Stufen |
| [Tselios] | S. 52 | Fig. 6.5 (gehört zu 6.2.1 MSM) | eMSM: Stress und Recovery abwechselnd, Umrechnung in ΔV_th |
| [Waltl] | S. 244 | II. Defect Characterization | MSM: Laden im Stress, Entladen in der Recovery |
| [Waltl] | S. 248 | IV.B | TDDS braucht ca. 100 Stress/Recovery-Zyklen |
| [Tselios] | S. 53 | 6.3 Measurement Setup | Konstante Gate-Spannung mit TIA gegen Konstantstrom-Methode |
| [Tselios] | S. 54 | 6.3 | Vorteile der Konstantstrom-Methode, Kriterien für die Wahl |

---

## 6. Aufbau eines Messgeräts für Einzeldefekte

### 6.1 Systemaufbau
Das Messgerät der TU Wien (Defect Probing Instrument, DPI) ist **modular** aufgebaut:
- **Pattern Generator Unit (PGU):** programmierbare Spannungen mit DACs, ARM-Prozessor, USB
- **Device Connector Unit (DCU):** wandelt den Strom in eine Spannung um (TIA)
- **Data Acquisition Unit (DAU):** ADC

Alle Einheiten sind über einen Bus synchronisiert und werden über USB konfiguriert. **Digital- und Analogteil sind galvanisch getrennt**, damit die analogen Signalwege möglichst rauscharm bleiben.

### 6.2 Transimpedanzverstärker (TIA)
Herzstück ist ein **TIA**. Bei idealem OPV gilt I = V_o / R. Der **Kondensator parallel zum Rückkopplungswiderstand** legt die Bandbreite fest und erhöht die Phasenreserve, damit die Schaltung stabil bleibt.

### 6.3 Bauteilwahl gegen Leckströme
- **OPVs mit FET-Eingang**, weil sie sehr kleine Eingangsströme haben
- **Mechanische Relais statt integrierter Analogschalter** für die Umschaltung der Messbereiche, weil integrierte Schalter zu viel Leckstrom haben
- Nach dem TIA wird die Source-Spannung V_S abgezogen, und ein **Filter** begrenzt die Bandbreite auf die Abtastrate des ADC

### 6.4 Messbereiche: Auflösung gegen Bandbreite
Mehrere Rückkopplungswiderstände ergeben mehrere Messbereiche (beim DPI 7 Kanäle). Grundregel: **Je feiner die Stromauflösung (größeres R_f), desto kleiner die Bandbreite.** Bei Verstärkung G = 10⁶ und 100 kHz Abtastrate erfasst das DPI über 70 % der Defekte. Eine geringere Bandbreite verlangt längere Messzeiten. Eine Verlängerung der Recovery-Zeit von 1 ks auf 10 ks würde bei 65 Bauteilen etwa 7 Tage mehr Messzeit bedeuten.

**Für die Arbeit:** Diese Punkte entsprechen direkt den Designentscheidungen im eigenen nA-Messgerät (umschaltbares R_f mit 100 kΩ / 10 MΩ, FET-Eingangs-OPV, galvanische Trennung über USB-Isolation, ADC).

| Quelle | Seite | Kapitel | Aussage |
|---|---|---|---|
| [Waltl] | S. 245 | III. Defect Probing Instrument | Modularer Aufbau aus PGU, DCU und DAU, Bus, USB |
| [Waltl] | S. 245 | III.A Pattern Generator Unit | ARM-Prozessor, USB, interner Bus |
| [Waltl] | S. 246 | III.C Current Converter Unit | TIA, I = V_o/R |
| [Waltl] | S. 247 | III.C | C_f parallel bestimmt Bandbreite und Phasenreserve |
| [Waltl] | S. 247 | III.C | OPVs mit FET-Eingang, Relais statt integrierter Schalter |
| [Tselios] | S. 56 | 6.3.1 Custom-Made Low Noise Measurement Unit | FET-OPV, 7 Kanäle mit mechanischen Relais, V_S abziehen, Filter |
| [Tselios] | S. 54 | 6.3 Measurement Setup | Relais für Messbereiche, SNR und Timing als Herausforderungen |
| [Waltl] | S. 246 | Fig. 10 | Messbereiche und Bandbreite: feinere Auflösung, kleinere Bandbreite |
| [Waltl] | S. 248 | IV.B Intrinsic Noise | G = 10⁶ bei 100 kHz erfasst über 70 % der Defekte |
| [Waltl] | S. 248 | IV.B | Mehr Messzeit bei kleinerer Bandbreite (ca. 7 Tage) |

---

## 7. Anforderungen an die Messauflösung

Handelsübliche Messgeräte (SMUs, General-Purpose Instruments) erreichen eine Auflösung für Stromstufen von nur etwa **5 nA bei mindestens 1 kHz**. Damit sind Einzeldefekte nur bei sehr kleinen Transistoren messbar (**W×L < 200 nm × 200 nm**). Weil die Stufenhöhe mit größerer Gate-Fläche schnell abnimmt, braucht man für größere Bauteile ein eigens entwickeltes, rauscharmes Messgerät.

**Für die Arbeit:** Das ist die zentrale Begründung, warum ein eigenes nA-Messgerät entwickelt wird.

| Quelle | Seite | Kapitel | Aussage |
|---|---|---|---|
| [Waltl] | S. 247 | IV.A Extraction of Step Height Distribution | Grenze handelsüblicher Geräte etwa 5 nA bei 1 kHz, nur bis W×L < 200 nm × 200 nm |
| [Waltl] | S. 247 | Fig. 11 | Nachweisgrenze etwa 5 nA bei 1 kHz eingezeichnet |
| [Waltl] | S. 243–244 | I.B Requirements | Auflösung und Rauschen als größte Herausforderung |

---

## Literatur

- **[Hu]** C. Hu, *Modern Semiconductor Devices for Integrated Circuits*, Pearson/Prentice Hall, 2010. Kap. 6 und 7.
  Dateien: `Dokumentation/Datashit/Chenming-Hu_ch6-1.pdf`, `Dokumentation/Datashit/Chenming-Hu_ch7.pdf`
- **[Tselios]** K. Tselios, *Statistical Analysis of Reliability and Variability Effects in CMOS Technologies Based on Single-Defect Spectroscopy*, Dissertation, Technische Universität Wien, 2025. Betreuer: M. Waltl.
  Datei: `Dokumentation/Datashit/20.500.12708_195047.pdf`
- **[Waltl]** M. Waltl, „Ultra-Low Noise Defect Probing Instrument for Defect Spectroscopy of MOS Transistors“, *IEEE Transactions on Device and Materials Reliability*, Bd. 20, Nr. 2, S. 242–250, 2020. DOI: 10.1109/TDMR.2020.2988650.
  Datei: `Dokumentation/Datashit/ep4P4PrcGnjnrCY_us.pdf`
