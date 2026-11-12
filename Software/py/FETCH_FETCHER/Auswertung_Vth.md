# Vth-Bestimmung für den Vergleich (Entscheidung)

Stand 12.11.2026 · **Methode: Konstantstrom (Constant Current)**

## Regel

- Vth = Gate-Spannung, bei der ID = I_krit.
- I_krit ist einstellbar (Auswerten → Einstellungen), Standard **50 nA** (100-nA-Bereich).
- Zwischen den zwei Punkten um I_krit wird **in log(ID) linear interpoliert**:
  `Vth = VG1 + (log I_krit − log I1) / (log I2 − log I1) · (VG2 − VG1)`
- ΔVth = Vth(Messung) − Vth(Referenz).
- Alle verglichenen Dateien verwenden **denselben I_krit**.
- Erreicht eine Kurve I_krit nicht → keine Vth, Warnung anzeigen.
- SPOT-MSM (ein Punkt pro Zyklus): ΔVth ≈ −ΔID / gm, gm aus der Referenz-ID-VG (c00) bei der Lese-Gatespannung.

## Warum nicht lineare Extrapolation

- Braucht starke Inversion (µA–mA), das liegt über dem 10-µA-Bereich bzw. ist mit max. 2,5 V Gate beim BS170 evtl. nicht erreichbar.
- Ableitung gm ist rauschempfindlich (RTN).
- Mobilitätsänderung (v. a. HCD) fließt mit in Vth ein.

## Quellen

- D. K. Schroder, *Semiconductor Material and Device Characterization*, 3. Aufl., Wiley 2006, Kap. 4.4
- A. Ortiz-Conde et al., „A review of recent MOSFET threshold voltage extraction methods“, Microelectronics Reliability 42 (2002) 583–596
- onsemi BS170 Datenblatt: https://www.onsemi.com/pdf/datasheet/bs170-d.pdf
