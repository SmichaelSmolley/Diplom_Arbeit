## To-Do Liste

+ Zeichnen des Blockdiagramms (done)
+ Blockdiagramm für ein Modulares Messsystems (done)
+ erklärung Diff-Leitungen Stecker Systems(done)
+ peter Quälen

**Versorgung**
- [ ] Eigangsspannung auf Platinen Definieren(Drop out berücksichtigen)
- [ ] Verlustleitung der LDO's berechnen
- [ ] Termische evaluierung der LDO's
- [ ] PG(Power Good) Signal entweder verwenden oder nicht (eher schon schon wichtig beim LT3094 **BIGL** fragen)
- [ ] ESD Schutz und überspannung Schutzkonzept

**Ground-Konzept**
- [ ] Durchgehende Ground-Plane
- [ ] Via-Fence bedenken
- [ ] Rückstrompfade analysieren (Digital und Analog)
- [ ] Sicherstellen: Kein Split unter LVDS-Leitungen
- [ ] Analog-Referenzpunkte klar definieren und stützen

**TIA / Hochimpedanzbereich**
- [ ] Guard-ring und pines für opa928 einplanen
- [ ] feadback wiedestand villeicht mit reed relais
- [ ] hoch impedanz leitungen kurz halten maybe guard
- [ ] Leckstromquellen klein halten (Stecker, Fluxreste, Feuchte)
- [ ] Masse für analog stabil und keine hohe leistung und keins Schalten

**Rauschbetrachtung**
- [ ] Noise maybe berechnen 
- [ ] PSRR der LDOs prüfen 100Hz
- [ ] 50-Hz-Einkopplung analysieren
- [ ] EMV box bauen
- [ ] Digitale Lastströme vom Analogbereich fernhalten

**LDO-Layout**
- [ ] Ausgangskondensatoren laut Datenblatt auswählen
- [ ] SET-/Noise-Kondensator korrekt dimensionieren
- [ ] Masseanschlüsse lokal bündeln
- [ ] Datenblatt-Layout-Empfehlungen umsetzen

---

### Impedanzkontrolle
- [ ] Zielimpedanz definieren (100 Ω differentiell)
- [ ] PCB-Stackup festlegen (2-Layer oder 4-Layer)
- [ ] Leiterbahnbreite und Abstand berechnen
- [ ] Hersteller-Stackup-Daten einholen
- [ ] Impedanzsimulation durchführen (falls möglich)

---

### Routing-Regeln
- [ ] Beide Leitungen gleich lang führen
- [ ] Gleiche Anzahl an Vias pro Leitung
- [ ] Keine Via-Stubs
- [ ] Keine Unterbrechung der Referenzebene
- [ ] Keine 90°-Winkel
- [ ] GND nahe am Diff-Pair platzieren

---

### Stecksystem
- [ ] Board-to-Board oder Edge-Connector festlegen
- [ ] Mechanische Führung berücksichtigen
- [ ] GND-Pins um jedes LVDS-Paar anordnen
- [ ] Kontaktanzahl für Erweiterung prüfen

---

### Mechanik
- [ ] Steckzyklen abschätzen
- [ ] Einschubmechanik definieren
- [ ] Führungsschienen oder Zentrierhilfen planen
- [ ] Toleranzen berücksichtigen
- [ ] Verriegelung oder Verschraubung einplanen
- [ ] EMV-Schirmkonzept berücksichtigen

---

### 5. Digitale Integration

- [ ] LVDS-Pegel prüfen
- [ ] 100-Ω-Termination am Empfänger platzieren
- [ ] Referenzspannung prüfen
- [ ] Clock-Verteilung bewerten
- [ ] Übersprechen zwischen LVDS und Analogbereich analysieren

---

### 6. Test- und Debug-Konzept

- [ ] Messpunkte einplanen (LDO, Sternpunkt, TIA-Ausgang)
- [ ] Analog- und Digitalteil separat testbar machen
- [ ] LVDS-Testpattern-Einspeisung vorsehen
- [ ] Versorgung getrennt messbar machen
- [ ] Optionale Serienwiderstände oder Jumper für Debug einplanen

---

### 7. Dokumentation

- [ ] Blockdiagramm erstellen
- [ ] Ground-Return-Path grafisch darstellen
- [ ] Impedanzberechnung dokumentieren
- [ ] LDO-Auswahl technisch begründen
- [ ] Noise-Budget berechnen
- [ ] Layoutentscheidungen begründen
- [ ] Alternativen vergleichen
- [ ] TIA berechnungen dokumentieren

---

### Themen zur Vertiefung

- [ ] Rückstrompfade bei High-Speed-Signalen
- [ ] Microstrip vs. Stripline
- [ ] Differential Impedance Berechnung
- [ ] Low-Frequency Noise bei LDOs
- [ ] EMV-Grundlagen
- [ ] Ground-Bounce und Referenzverschiebung
- [ ] Leckstrom-Mechanismen auf PCBs
