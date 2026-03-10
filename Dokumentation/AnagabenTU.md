# Diplomarbeitsspezifikationen

## Grundlegende Angaben:
Es soll ein modulares und rauscharmes Messsystem zur Charakterisierung von MOSFETs und zur Untersuchung deren RTN-Effekten entworfen werden. RTN entsteht durch einzelne Defekte im Gate-Oxid oder an der Grenzfläche, welche durch das Einfangen und Abgeben von Ladungsträgern entstehen. Durch diesen Vorgang entstehen diskrete Stromstufen im Sourcestrom des MOSFETs. Mit diesem Messsystem sollen diese Stromfluktuationen analysiert sowie die Auswirkungen von Stressspannungen auf das Auftreten von Defektaktivitäten untersucht werden.

## Funktionelle Angaben:

ID-VG:
Die Gate-Spannung soll mittels eines DC-Sweeps variiert werden, während die Drain-Spannung konstant gehalten wird. Der Sourcestrom des MOSFETs wird über einen TIA gemessen. Die Drain- und Gate-Spannung sollen auch durch das Messgerät zur Verfügung gestellt werden. Die Sweep-Parameter (Startspannung, Endspannung, Schrittweite) sollen konfigurierbar sein.

RTN Messung:
Für die Untersuchung von Random Telegraph Noise wird ein fester Arbeitspunkt am MOSFET eingestellt (konstante Gate- und Drain-Spannung). Anschließend wird der zeitabhängige Strom über einen längeren Zeitraum aufgezeichnet. Bei kleinen MOSFET-Strukturen können dabei Stromstufen auftreten. Diese können durch einzelne aktive Defekte im Isolator oder an der Grenzschicht zwischen Isolator und Bulk-Material entstehen. Die Messdaten werden anschließend analysiert. Folgende Auswertungen sind vorgesehen: Histogramm der Stromwerte, Stromsprunghöhen, Dwell-Times der einzelnen Zustände und Power Spectral Density (PSD) zur Analyse des Low-Frequency-Noise.

Stress Messung:
Beim Stressen wird eine erhöhte Gate-Spannung über einen definierten Zeitraum angelegt, wodurch sich Defekte im Gate-Oxid oder an der Grenzfläche laden können. Nach der Stressphase wird der MOSFET erneut am Arbeitspunkt vermessen, um Veränderungen im Stromverhalten oder der Defektaktivität zu analysieren. Je nach Device-Größe kann es zu Stromstufen oder zu einem kontinuierlichen Stromanstieg kommen.

Frequenzanalyse:
Die aufgezeichneten Stromtransienten sollen zur Berechnung der PSD verwendet werden, um das Rauschen des Messgerätes zu analysieren. Weiters soll die PSD verwendet werden, um charakteristische Noise-Spektren sowie mögliche Störfrequenzen zu identifizieren.

Strom Messbereich:
Das Messsystem soll mehrere Bereiche abdecken, um sowohl kleine als auch größere Ströme messen zu können. Das Hauptziel ist die Messung von Strömen im Bereich unter 10 nA, da RTN-Effekte typischerweise in diesem Bereich auftreten.
Strom-Messbereich:
10 nA – 1 µA
1 µA – 1 mA

Rauschverhalten
Das Messsystem soll so ausgelegt werden, dass das Eigenrauschen des Verstärkers möglichst gering ist, um Ströme im Nanoampere-Bereich detektieren zu können. Das Rauschverhalten soll über die Power Spectral Density (PSD) charakterisiert werden. Das Eigenrauschen des Messsystems soll klein genug sein, um Stromfluktuationen im Bereich unter 10 nA detektieren zu können.

Linearität:
Die Linearität des Strommesspfades soll mit Hilfe einer Referenzstromquelle überprüft werden. Dabei sollen Offsetfehler, Gainfehler sowie die Nichtlinearität des Systems bestimmt werden.