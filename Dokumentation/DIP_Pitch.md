# DIP_PITCH

## Bauteile

### Digital
MPU ESP32 Wroom dev board
LVTTL Diff. Sender SN65LVDS1
LVTTL Diff. Transsever SN65LVDS2
LVTTL Diff. Quad Recifer DS90LV048A
LVTTL Diff. Quad Sender DS90LV047A

### Analog
OPV OPA928 ultra low Bias, low noise Opv
OPV LMC6001 low Bias, low noise Opv

### Converter
ADC ADS8681 16Bit, variable Input range, low glitch adc

### PSU
LDO LT3094EMSE#TRPBF low noise, low DropOut, Negative LDO
LDO LT3042EMSE#TRPBF low noise, low Dropout, Positive LDO

## Dokumentation

### Idee der Arbeit

Durch den Aufbau des MOSFET, liegt eine Isolierungsschicht am Balk, da solche Isolatoren fertigungsbedingt nicht perfekt hergestellt werden können enstehen unreinheiten, sogenannten ladungsfallen, denn bei einem stromfluss durch den nkanal kann durch den Tunneleffekt dazu kommen das siche ladungsfallen mit elektronen befüllt werden diese verringern durch ihre ladung die dicke des kanales und diese änderung äusert sich als RTN(Random Telegram Noise), dieses ist wiederum messbar. durch analyse des RTN lassen sich rückschlusse auf die Lebensdauer und beschaffenheit von solchen Halbleitern evaluieren.

### Bereichseingrenzung

Es soll eine messschaltung für die messung von nA strömen entworfen werden um die änderung im Strom durch das RTN zu vermessen. Auch die Ansteerung der anschlüsse (Drain, Gate), sollen ansteurbar sien zur automatischen erfassung von der IDVG kennlineie und einstellung des Source stromes. dies soll von einer MCU gstert und reguliert werden diese nimmt die messdaten auf und speichert diese bis zum ende der messung und sendet diese nach dem beendigen der messung an ein Auswerte gerät weiter leiten. 

Auf diesem Auswerte gerät sollen die messdaten entgegengenommen werden und analysiert werden(FFT, Transienten, Digital Tiefpassfilter).

### Motivation der Arbeit

war cool und so

## Arbeitsprogress

+ programmerstellung für die berechnung der TIA stufe
+ Block-Diagramm des Analog Messsystems
+ Auswahl des ADS8681
+ Besprechung mit TU-Kontakt
+ Programm lib erstellung für ADS8681 Kommunikation
+ Herstellung einer Test Kommunikations Platine
+ Entwicklung eines entwurfes für ein Modulares Messsystems

## To-Do Liste

+ Zeichnen des Blockdiagramms
+ Blockdiagramm für ein Modulares Messsystems
+ erklärung Diff-Leitungen Stecker Systems

## Markdown Ideen


