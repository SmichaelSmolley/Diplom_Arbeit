# Stressing

das Stresen ist eine der Haupt analysen der DIPA, in der DIP sollen 2 Arten von MOSFET's gestresst werden ein "Normaler" und ein FG.
Stressen heist das GAte mit hohen spannungen (je nach MOSFET) zu versoregen(natürlich ohne das auf drain einespannung liegt also 0V um einen zu hohen Drain Strom zu verhindern, welcher den Source TIA und den Drain Dirver zerstören könnte). Normaler nMOS TDDB, Floating-Gate Endurance das vermessen des TDDB(Time-Dependent Dielectric Breakdown) und der Endurence eines FG kann auskunft geben auf die Lebensdauer und auswirkungen des Übersteuerungs faktor bei der Klassischen ansteuerung eines Mosfet. 

Das stressen wird in cyclen aufgebaut, z.b. es sollen 100 Stresscyclen vorgenommen werden, danach eine IDVG messung vorgenommen werden,und weider 100 Stresscyclen…
durch das Stressen ist erwartet volgende effekte in der Messung der IDVG zu erkennen:

- Verschiebung der Threshold spannung
    - Das Aufladen von Traps(Fallen Oxid) TDDB
    - Verschiebt die Kurve nach rechts bei einem Nkanal.
- LEckstrüme durch das Oxid
    - Durch das Stressen können lokale schwachstellen enstehen-> leakage steigt
    - kann im Subthreshold bereich den Strom steigern
- Reduzierung des Kanalstromes
    - wenn fallen aufgeladen sind kann es zu Mobility beeinträchtigung kommen
    - IDVG wird flacher

Messung eines FG

- Tunneloxid abbau
    - jedes schreiben oder löschen erzeugt Traps und lokale defektr
    - dann zu th verscheibung führen auch im nicht beschreiebenen zustand oder zum ladungsverlsuut am FG
- Ladung auf dem Floating Gate kann sich auch ohne Strom langsam ändern.
- Vth-Drift:Der gleiche Program/Erase-Befehl führt nach 100 Zyklen **zu einer anderen V\<sub>th\</sub>**, weil sich Fallen im Oxid angesammelt haben.
- Subthreshold-Leck: Leichte Erhöhung durch Oxiddefekte.
- Programmier-/Lösch-Effizienz sinkt: Die Zelle benötigt evtl. **höhere Spannung oder längere Zeit**, um denselben V\<sub>th\</sub> zu erreichen.
- Langzeit-Ausfallrisiko:Nach sehr vielen Zyklen (10⁴–10⁶) kann das Oxid durchbrechen → permanente Datenverluste.
- durch das nallysiern der th verscheibung und durch das steigen des RTN aufkommen lassen sich rückschlusse auf die lebenszeit schliesen


