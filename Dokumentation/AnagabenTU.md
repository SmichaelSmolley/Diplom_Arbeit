# Speks

## Grundangaben
Entwicklung eines modularen, rauschar­men Messsystems zur:
* Charakterisierung von MOSFETs
* Untersuchung von RTN-Effekten
* Analyse von Stress-induzierten Degradationen
* Erfassung von Leakage-Strömen im nA-Bereich

## Funktions Angaben

- IDVG messung
    - Sweep Gate-Spannung
    - Sweep Drain Spannung oder Konstant betreib
    - Strommesssung mittels TIA
    - linearer oder log sweep
- RTN messung
    - Messdauer bis 300s/5 min
    - Abtastung bis 1Ms/s
    - Histogramm, Delta I, Dwell Times
- leak current messung
- Stressen mit cycle angabe(TDDB)
    - Programmierbare Stressspannung
    - Zyklische Belastung
    - Messreihenfolge angaben
- Messreinfolgen angabe
    - Messreihenfolge: Stress IDVG RTN or Stress RTN Stress RTN …
- Rohdaten export zur FFT  

## elektrische Angaben

- Strom messbereich
    - erhofft: 10nA - 1uA, 1uA - 1mA
    - ziel: <10nA
- Rausch verhalten
    - input-referred noise < 10nA RMS (BW = 10kHz)
- Frequenzanalyse
    - FFT Analyse der Rohdaten
    - bestimmung der Noise peaks + begründung
    - bestimmung Noise foor
- effektive auflösung
    - Enob = (SNR - 1.76) / 6.02
- Linearität
    - INL
    - DNL
    - Gain-Fehler
    - Offset-Fehler
    - vill kalibrierung über refstromquelle
- Temperaturvehalten
    - Offsetdrift (nA/*C) compensation
    - Langzeit drift

## Ziehle der Arbeit

- Charakteriserung Mosfets
- analyse von verschleis
- Untersuchung von RTN
- Analyse von Stress-induzierten Degadation