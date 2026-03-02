# Diplomarbeitsspezifikationen

## Grundlegende Angaben:
Es soll ein modulares und rauscharmes Messsystem zur Charakterisierung von MOSFETS und die Untersuchung deren RTN-Effekten entworfen werden. Mit dem Messsystem soll die Stress-Induzierte Degradation analysiert und Leakage-Ströme im Nanoampere-Bereich erfasst werden können.

## Funktionelle Angaben:

- IDVG-Messung:
     Die Gate-Spannung soll per DC Sweep dargestellt werden. Die Drain-Spannung wird entweder per DC Sweep oder Konstant-Betrieb angegeben. Die Sweeps sollen entweder linear oder logarithmisch aufgetragen werden können. Mittels eines Trans-Impedanz-Amplifier (TIA) soll die Sourcemessung vorgenommen werden.

* RTN-Messung:
     Die RTN-Messdauer soll maximal 5min dauern und dabei eine Abtastrate von 1Ms/s haben. Folgende Auswertungsdiagramme sollen erstellt werden: Histogramm, Delta I, Dwell Times; Es soll der Leakage-Current gemessen werden.

     Bei der Stressfunktion soll die Möglichkeit gegeben sein die Stresszyklen anzugeben. Die Stressspannung soll dabei programmierbar sein um eine zyklische Belastung zu definieren. Der Nutzer soll die Messreihenfolge selbst bestimmen können, beispielsweise; 1. Stress-Messung, 2. IDVG-Messung, 3. RTN, oder 1.Stress-Messung, 2. RTN-Messung, 3. Stess, 4. RTN, usw.

     Die daraus enstehenden Rohdaten sollen für eine FFT (Fast Fourier Transformation exportiert werden. 

## Elektrische Angaben

* Strom-Messbereich:
     Erhofft wird sich ein Bereich von 10nA bis 1uA und 1uA bis 1mA. Das eigentliche Ziel ist ein Messbereich unter 10nA

- Rausch-Verhalten:
     Das Eingangsrauschen soll kleiner als 10nA Effektivwert bei einer Bandbreite von 10kHz sein, um Rauschen im gewählten Messbereich zu verhindern.
  
- Frequenzanalyse:
    Die Rohdaten sollen zur Erstellung einer FFT-Analyse verwendet werden. Außerdem sollen die Noisepeaks gemessen und begründet werden um diese danach zu minimieren. Nach der Optimierung soll der Noise-Floor bestimmt werden. 
      
- Effektive Auflösung:
    Es soll die effektive Auflösung des Messgeräts bestimmt werden um die Genauigkeit abzuschätzen (Enob ≥ 14).
    (Enob = (SNR - 1.76) / 6.02)

- Linearität:
    Bei der Linearität sollen Integrale- & Differentiale Nicht-Linearität, der Gain-Fehler und Offset-Fehler gemessen werden können. Diese sollen per Referenzstromquelle kalibriert werden.

- Temperaturvehalten
    Wenn das Messgerät länger ohne Unterbrechungen misst kann es zu Langzeit-Drift kommen (Erwärmung von Bauteilen). Durch das Messen der Temperatur soll das entstehende Offset kompensiert werden.

## Ziele der Arbeit:

Am Ende sollen MOSFETS charakterisiert und deren Verschleiß analysiert werden können. Außerdem soll die RTN untersucht werden und die Stress-Induzierte Degradation soll analysierbar sein.
