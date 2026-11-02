# Begriffsdefinition

**ADC** – Analog-to-Digital Converter

**BTI** – Bias Temperature Instability

**DAC** – Digital-to-Analog Converter

**DUT** – Device Under Test

**FET** – Field-Effect Transistor

**GIDL** – Gate-Induced Drain Leakage

**HC** – Hot Carrier

**IDVG** – Drain Current over Gate Voltage

**MOS** – Metal-Oxide-Semiconductor

**MOSCAP** – MOS Capacitor

**MOSFET** – MOS Field-Effect Transistor

**MSM** – Measure-Stress-Measure

**OPV** – Operational Amplifier

**PSD** – Power Spectral Density

**RAM** – Random Access Memory

**RDS** – Resistance between Drain and Source

**RTN** – Random Telegraph Noise

**RTS** – Random Telegraph Signal

**SILC** – Stress-Induced Leakage Current

**SNR** – Signal-to-Noise Ratio

**SPICE** – Simulation Program with Integrated Circuit Emphasis

**VTH** – Threshold Voltage

\pagebreak

# Ausgangslage

In der modernen Elektronik werden Schalter meist mit Feldeffekttransistoren realisiert. Diese sind geeignet für hohe Schaltfrequenzen, können kleiner hergestellt und zuverlässiger designt werden. Diese nutzen das Prinzip der elektrischen Felder. Durch das Anlegen einer Spannung am Gate des Transistors wird die Breite des leitfähigen Kanals zwischen den Drain- und Source-Anschlüssen moduliert. Durch diese Gegebenheit sind die Feldeffekttransistoren geeignet, als elektrische Schalter verwendet zu werden.

Doch auch rein elektrische Schalter wie MOSFETs können mit der Verwendung immer unzuverlässlicher werden, allerdings können sich auch die Eigenschaften wie der RDS mit der Alterung der Bauteile ändern. Ursache für diese Änderung mit dem Alter können Defekte in der Kristallstruktur des Bauteiles sein.

Da immer neue Verfahren zur Herstellung von MOSFETs entstehen und die entstehenden Produkte auf die Zuverlässigkeit und den MTTF untersucht werden. Effekte, die verstärkt mit zunehmendem Alter auftreten, sind Drifts der Vth und die Zunahme des GIDL. Neben diesen zeitlich langsamen Veränderungen können Defekte auch zu zeitlich veränderlichen elektrischen Signalen führen.

Diese Änderungen der Eigenschaften können Rückschlüsse auf die MTTF als auch die Ageing Rate erlauben. Weiters kann durch die Untersuchung solcher Effekte die Auswirkung von Defekten auf das Verhalten eines MOSFETs genauer charakterisiert werden.

# Aufgabenstellung

Wir wollen  wien messgerät entwerfen nicht nur hadware auls auch software selber entwikeln um die degradation von elektrischen bauteilen nachzuweisen. das gerät soll die notwendigen parameter zu sorcen und die einstehenden größen zu vermessen. Es soll möglich sein das zu erstellt gerät mittels SCPI (Standart Communication programmable instroments) programmier bar sein und die messparameter bestimmbar.

# Theoretische Grundlagen

Während der Herstellung von Halbleitern werden verschiedene Schichten von verschieden dotiertem Silizium aufgetragen. Auch bei diesem Auftragen der Schichten können an den Grenzflächen zwischen Schichten Defekte auftreten, in Form von nicht verbundenen Atombindungen. Auch innerhalb einer Schicht können z. B. Einschlüsse von O (Sauerstoff-)Atomen oder fehlende Verbindungen zu Defekten in der Kristallstruktur des Siliziums führen.

Die Defekte an der Verbindungsstelle zwischen dem Isolator des MOSFETs und der Siliziumschicht, in der sich der leitfähige Kanal bildet, sind die Defekte, welche den größten Einfluss auf die Degradation haben. Dadurch, dass diese Defekte Ladungsträger aufnehmen oder abgeben können, sind geringere Energien der Ladungsträger notwendig. Da diese Ladungsträger auch leichter wieder abgeben können, sind diese Defekte eher für kurzfristige Effekte verantwortlich.

Defekte im Isolator sind stabiler und können Ladungsträger über längere Zeit speichern. Durch das Auf- und Abgeben von Ladungsträgern können sich Defekte im Isolator verändern und zur weiteren Degradation beitragen.

Degradation bedeutet, dass Defekte im MOSFET ihren Zustand ändern, dadurch, dass sie Ladungsträger aufnehmen. Durch das Abgeben und Aufnehmen von Ladungsträgern können Defekte aktiviert, verändert oder erzeugt werden.

Die relevantesten Eigenschaften, die sich durch die Degradation verändern, sind unter anderem die Ladungsträgermobilität im Leitungskanal und damit der RDS. Bei den in dieser Arbeit hauptsächlich behandelten N-Kanal-MOSFETs kann eine zunehmende Anzahl von Defekten und eingefangenen Ladungsträgern zu einer Verringerung der Ladungsträgermobilität führen. Dadurch kann der RDS zunehmen.

# Technische Grundlagen

## Aufbau und Funktionsweise des MOSFET

Quelle: Hu Kap. 5–6

## Kennlinie im Subthreshold-Betrieb

Quelle: Hu S. 263-265

im bereich in dem Vgs < Vth ist ist es der sub threshold, weiters gibt es den Ioff das ist der id bei Vgs = 0. Wenn Vgs < Vth wenn man semilog Ids vs. Vgs plottet eine gerade linei das bedeutet das im Subthreshold bereich eine exponential line ist. 
Der subthreshold strom häng von der technologie ab die man untersuchen will ist aber standart mäsig im bereich von 1nA und 200nA.

## Defekte im MOSFET

Quelle: Tu kp2

## Degradation BTI HCD SILC Oxid-Durchbruch

Waltl S. 242
Hu S. 270-272

## RTN und 1/f Rauschen

quelle: Hu S. 235 Tu S.52

## Einzeldefekt-Spektroskopie

quelle: tu S.7, Waltl S 243-245

# Messmethoden

## ID(VG) Kennlinie und Bestimmung von Vth

Es ist notwendig bei der vermessung der Kennline Id vs Vg möglichst schnell zu messen da bei langen anlegen erhöter Gate spannungen, dies minimiert den einfluss von defecten mit kürzerer einfang und abgebe zeiten als die messdauer. Weiters wird bei eben kürzeren sweeps der ausgangszustand des devices erhalten.

## Delta Vth bestimmung

um bei defekt absobrtion oder emmission delta vth zu bestimmen gibt entweder über die methode einer Konstanten Gate-Spannung oder über einen Konstanten Drainstrom. In dieser Arbeit wird die methode der Konstanten  gatespannung verwendet, wobei der Sourcestrom vermessenwird. da in Dieser arbeit nur der Source strom vermessen wird müssen änderungen dieses in eine delta Vth üngerenet werden, miteles einer referenz IDVG welche zuerst aufgezeichnet werden muss.

$$\Delta V\_{th} = V\_{G,\text{angelegt}} - V\_G^{\text{Ref}}(I\_{S,\text{neu}})$$ $$\Delta V\_{th} \approx -\frac{\Delta I\_S}{g\_m}, \qquad g\_m = \frac{dI\_S}{dV\_G}\bigg|\_{\text{Arbeitspunkt}}$$ $$\Delta V\_{th} = -SS \cdot \log\_{10}\left(\frac{I\_{S,\text{neu}}}{I\_{S,\text{alt}}}\right)$$

## Measure-Stress-Measure MSM

quelle: Tselios S. 52

Das prinzip MSM wird verwendet um die enderung in der Vth zu vermessen. zuerst wird die referenz IDVGvermessen werden um delta Vth zu bestimmen. Nach dem erstmaligen vermessei wird alternierend eine stress spannung und eine recoveryx spannung an das Gate des MOSFETs angelegt.Wärend dem recovern wird der Source stroms vermessen.

quelle: Watl S.244

Beim MSM wird ganz bewust eine stresspannung angelegt um defekte zu laden. in der folgenden recovery time entladen sich die defecte wieder.

quelle: Tu dis S.52

bei kleinen Divce sizes ist da einzele defecte erkenn bar sind discrete steps beim recovern, bei größeren devices sind es eher kontnuiliche änderungen.

## Konstante Gate-Spannung oder konstanter Drainstrom

Quelle: Tu S. 53-54, Wathl

# Anforderungen an das Messgerät

# Systemkonzept

# Hardware

## Spannungsversorgung und Referenzen

## DAC und Gate- bzw. Drain-Ansteuerung

## Transimpedanzverstärker und Messbereichsumschaltung

## ADC-Treiber und ADC

## Digitalteil: MCU, SPI, USB-Isolator, Temperatursensor, LEDs

## Backplane: Verpolungsschutz, LVDS

## Layout: Guarding, AGND/DGND (Kester S. 9.53 ff., MT-031)

## Gehäuse

