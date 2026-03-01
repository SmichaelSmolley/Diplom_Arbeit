# Stressing-Messure

## Stressing

das Stresen ist eine der Haupt analysen der DIPA, in der DIP sollen 2 Arten von MOSFET's gestresst werden ein "Normaler" und ein FG.
Stressen heist das GAte mit hohen spannungen (je nach MOSFET) zu versoregen(natürlich ohne das auf drain einespannung liegt also 0V um einen zu hohen Drain Strom zu verhindern, welcher den Source TIA und den Drain Dirver zerstören könnte). Normaler nMOS TDDB, Floating-Gate Endurance das vermessen des TDDB(Time-Dependent Dielectric Breakdown) und der Endurence eines FG kann auskunft geben auf die Lebensdauer und auswirkungen des Übersteuerungs faktor bei der Klassischen ansteuerung eines Mosfet. 

Das stressen wird in cyclen aufgebaut, z.b. es sollen 100 Stresscyclen vorgenommen werden, danach eine IDVG messung vorgenommen werden,und weider 100 Stresscyclen…
durch das Stressen ist erwartet volgende effekte in der Messung der IDVG zu erkennen:

- Verschiebung der Threshold spannung
    - Das Aufladen von Traps(Fallen Oxid) TDDB
    - Verschiebt die Kurve nach rechts bei einem Nkanal.

![IDVG](./dokumentation_bilder/IdVg_dVth.png)

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

## Messure

Die Grösen die Vermessen werden sollen sind das RTN, IDVG, leak currend. 

### RTN

Bei RTN handelt es sich um Random Telegrapf noise, bei diesen handelt ews sich um rauschen in nA grßen ordnung. Es ahndelt sich um ein Digital ähnliches raushcen(deswegen Telegrapf). dieses tritt auf beim laden und entladen von Fallen im oxid. die heufigkeit von diesem Rauschen kann rückschlusse liefern auf den zusaqnde dees Oxides, und damit auf die auswirkungen des Stressens. bei einem langen stressen eine FG kann das Tunnel oxid beschädigt werden und so kann es zu höheren RTN vorkommen kommen. 

### IDVG

Bei der IDVG handelt es sich um die kennlinie eines MOSFET(der Drain strom über die Gate spannung).

![IDVG](./dokumentation_bilder/IdVg-curves.png)

diese Können durch einen sweep über die gain spannung erstellt werden. Bei dieser kennliene kann sich verändren durch verschiedeneste Stresseffecte. die Vth kann durch das stessen geladene Ladungs fallen nach oben verschoben werden was die gesammte kennliene nach rechts verschiebt. die steil heist kann ebenfalls durch das Stressen beeinflusst werden. Ebenfals der Subth Strom kann durch beschädigungen im oxid welche leakigcurrent zulassen beeinflusst werdn.



