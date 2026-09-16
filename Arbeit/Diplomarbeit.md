---
title: "Analyse von Degradationseffekten bei Feldeffekttransistoren"
author: "Watzek, Traube, Siedersleben, Pernerstorfer"
toc: false
toc-title: Inhaltsverzeichnis
toc-depth: 3
shift-heading-level-by: 1

header-includes:
  # header and footer
  - \usepackage{fancyhdr, titling, lastpage}
  - \pagestyle{fancy}
  - \fancyhf{}
  - \fancyhead[L]{27.01.2026}
  - \fancyhead[R]{Analyse von Degradationseffekten bei Feldeffekttransistore}
  - \fancyfoot[L]{\hspace{0.5cm}HTBL – Hollabrunn}
  - \fancyfoot[C]{Watzek, Traube, Siedersleben, Pernerstorfer}
  - \fancyfoot[R]{\thepage~/~\pageref{LastPage}\hspace{0.5cm}}
  - \renewcommand{\headrulewidth}{0pt}               # header line remove
  - \renewcommand{\footrulewidth}{0.4pt}             # footer line add

  # higher title
  - \usepackage{titling}
  - \setlength{\droptitle}{-8em}

  # margin
  - \usepackage[left=3cm,right=3cm,top=2cm,bottom=2cm]{geometry}
  - \setlength{\headwidth}{\textwidth}
---

\input{titlepage.tex}
\pagebreak
\renewcommand{\contentsname}{Inhaltsverzeichnis}
\tableofcontents
\pagebreak

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

Heutzutage werden in der Elektronik Schalter meist mit Feldeffekttransistoren realisiert. Diese sind geeignet für hohe Schaltfrequenzen, können kleiner hergestellt und zuverlässiger designt werden. Diese nutzen das Prinzip der elektrischen Felder. Durch das Anlegen einer Spannung am Gate des Transistors wird die Breite des leitfähigen Kanals zwischen den Drain- und Source-Anschlüssen moduliert. Durch diese Gegebenheit sind die Feldeffekttransistoren geeignet, als elektrische Schalter verwendet zu werden.

Doch auch rein elektrische Schalter wie MOSFETs können mit der Verwendung immer unzuverlässlicher werden, allerdings können sich auch die Eigenschaften wie der RDS mit der Alterung der Bauteile ändern. Ursache für diese Änderung mit dem Alter können Defekte in der Kristallstruktur des Bauteiles sein.

Da immer neue Verfahren zur Herstellung von MOSFETs entstehen und die entstehenden Produkte auf die Zuverlässigkeit und den MTTF untersucht werden. Effekte, die verstärkt mit zunehmendem Alter auftreten, sind Drifts der Vth und die Zunahme des GIDL. Neben diesen zeitlich langsamen Veränderungen können Defekte auch zu zeitlich veränderlichen elektrischen Signalen führen.

Diese Änderungen der Eigenschaften können Rückschlüsse auf die MTTF als auch die Ageing Rate erlauben. Weiters kann durch die Untersuchung solcher Effekte die Auswirkung von Defekten auf das Verhalten eines MOSFETs genauer charakterisiert werden.

# Theoretische Grundlagen

Während der Herstellung von Halbleitern werden verschiedene Schichten von verschieden dotiertem Silizium aufgetragen. Auch bei diesem Auftragen der Schichten können an den Grenzflächen zwischen Schichten Defekte auftreten, in Form von nicht verbundenen Atombindungen. Auch innerhalb einer Schicht können z. B. Einschlüsse von O (Sauerstoff-)Atomen oder fehlende Verbindungen zu Defekten in der Kristallstruktur des Siliziums führen.

Die Defekte an der Verbindungsstelle zwischen dem Isolator des MOSFETs und der Siliziumschicht, in der sich der leitfähige Kanal bildet, sind die Defekte, welche den größten Einfluss auf die Degradation haben. Dadurch, dass diese Defekte Ladungsträger aufnehmen oder abgeben können, sind geringere Energien der Ladungsträger notwendig. Da diese Ladungsträger auch leichter wieder abgeben können, sind diese Defekte eher für kurzfristige Effekte verantwortlich.

Defekte im Isolator sind stabiler und können Ladungsträger über längere Zeit speichern. Durch das Auf- und Abgeben von Ladungsträgern können sich Defekte im Isolator verändern und zur weiteren Degradation beitragen.

Degradation bedeutet, dass Defekte im MOSFET ihren Zustand ändern, dadurch, dass sie Ladungsträger aufnehmen. Durch das Abgeben und Aufnehmen von Ladungsträgern können Defekte aktiviert, verändert oder erzeugt werden.

Die relevantesten Eigenschaften, die sich durch die Degradation verändern, sind unter anderem die Ladungsträgermobilität im Leitungskanal und damit der RDS. Bei den in dieser Arbeit hauptsächlich behandelten N-Kanal-MOSFETs kann eine zunehmende Anzahl von Defekten und eingefangenen Ladungsträgern zu einer Verringerung der Ladungsträgermobilität führen. Dadurch kann der RDS zunehmen.
