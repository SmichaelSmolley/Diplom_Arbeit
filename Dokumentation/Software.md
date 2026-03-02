## Software

Anzudenken ist eine funktion die Stresst (n cycles-mit den itgegebenen parametern), dann misst, und wieder stresst,( es sollen einfach ein programm ablauf vorgenommen werden, die die mitgegebenen parameter nimmt)

Parameter einer Messung:

**Allgemein:**

- Messdauer
- Messfrequenz/Samplingrate
- Mittelung
- Mittelungsfaktor
- Temperaturkompensation?

**Messart:**

- IDVG
    - Gate von bis
    - Gate Step
    - Drain Spannung
- Transienten
    - Parameter funktion
    - Imported IDVG
- Transienten fixed Gate
    - Gate Spannung
    - Drain Spannung
    - Imported IDVG?
        - Source Current
- Stressing
    - Cycles
    - Count
    - Stress Spannung
    - Stress Dauer

**Signalverarbeitung:**

- Oversampling Faktor
- Offsetkorrektur
- Driftkompensation
- Moving Average
- IIR Filter (Dig TP)

**Kalibrierung:**

- ADC cal
- DAc cal
- Temp cal
- Offset cal
- Referenzquelle auswählen
- Auto cal bei Start-up?

**Datenauzichnung:**

- Speicherung?
- Speicherort
    - RAM
    - SD
- Live Logging?
    - Logging Intervall
- Timestamp?

**Kommunikation:**

- Live-Daten?
- Schnittstelle
    - USB
- Baudrate
- Streaming
    - kontinuierlich
    - paketbasiert

**Systemparameter:**

- Save Settings at Startup?
- Watchdog?
- Sicherheit
    - Max Gate Spannung
    - Max Drain Spannung
    - Max Strom

**DUT:**

- N-MOS - P-MOS?
- Floating Gate?
    - Program/Erase-Spannung
- Uth

