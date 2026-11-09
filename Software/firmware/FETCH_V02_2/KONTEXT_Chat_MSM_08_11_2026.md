# Kontext: Chat vom 08.11.2026 – MSM in der Firmware PCB_test_code

Zusammenfassung des Chats mit Claude. Damit kann man (oder eine neue Claude-Sitzung) an dieser Stelle weitermachen.

## Projekt

- Diplomarbeit „Analyse von Degradationseffekten bei Feldeffekttransistoren“ (HTL Hollabrunn)
- Test-PCB mit STM32F103RB, ADC ADS8866 (16 Bit), DAC AD5689, TIA mit Rf 10 MΩ / 100 kΩ, Test-DUT BS170
- Firmware: `Software/firmware/PCB_test_code`
- Kommunikation über UART/USB mit Optokoppler-Isolation, Textbefehle `NAME= wert`

## Was im Code geändert wurde

1. **Fix in `COMMAND_DECODE.c`:** `SOURce1_PROT= ` und `SOURce2_PROT= ` hatten Länge und Offset 15 statt 14. Die Befehle wurden deshalb nie erkannt. Danach wurden alle `strncmp`-Längen und Offsets per Skript geprüft: Alle stimmen.
2. **MSM-Parameter hinzugefügt:**
   - `SCPI_COMMANDS.h`: Kommentarblock, MSM-Defines, Enum `MSM_MeasTypeTyp {MSM_SPOT, MSM_IDVG, MSM_TRANSIENT}`
   - `COMMAND_DECODE.h`: 10 Felder in `Measure_Param`
   - `COMMAND_DECODE.c`: 10 Decode-Zweige
   - `main.c`: Standardwerte
   - `measure.c`: leere `MSM()`, damit der Linker durchläuft
   - Mit gcc ist die Syntax geprüft, ein Keil-Build fehlt noch.

## MSM-Parameter (beschlossen)

| Befehl | Standard | Bedeutung |
|---|---|---|
| `SENSE_MODE_MSM= TRUE/FALSE` | FALSE | startet MSM |
| `MSM_CYCLES=` | 5 | Anzahl Zyklen |
| `MSM_START_TIME=` [ms] | 1000 | erste Stressdauer |
| `MSM_TIME_FACTOR=` | 10 | Stresszeit pro Zyklus × Faktor |
| `MSM_MEAS_TYPE= SPOT/IDVG/TRANSIENT` | SPOT | Messart in der Messphase |
| `MSM_MEAS_DELAY=` [ms] | 1 | Stress aus → erster Messwert |
| `MSM_RECOVERY_STRESS_TIME= TRUE/FALSE` | TRUE | TRUE: Recovery-Zeit = Stresszeit |
| `MSM_RECOVERY_TIME=` [ms] | 0 | feste Recovery-Zeit, nur bei FALSE |
| `MSM_INITIAL_MEASURE= TRUE/FALSE` | TRUE | Referenzmessung vor dem ersten Stress |
| `MSM_MAX_POINTS=` | 5000 | max. Punkte pro Messung |

Dazu wurde festgelegt:

- **Spannungen:** Stress kommt aus `STRESS_VOLTage` und `STRESS_DRAIN_VOLTage` (BTI/HCD über `STRESS_TYPE`), Lesen aus `SOURce1_VOLTage` (Gate) und `SOURce2_VOLTage` (Drain).
- **SPOT:** ein gemittelter Punkt nach `MEAS_DELAY`, danach **sofort** der nächste Stress. Die Recovery-Zeit wird nicht abgewartet.
- **IDVG:** ein Sweep; die Recovery-Zeit wird nicht verwendet.
- **TRANSIENT:** Die Recovery wird aufgezeichnet, die Punkte liegen logarithmisch mit Mindestabstand `DT_MIN`.
- **Recovery = Stresszeit:** Das Verhältnis t_rec/t_stress ist in jedem Zyklus konstant, die Kurven sind gut vergleichbar (Grasser 2007). Feste kurze Recovery entspricht klassischem MSM.
- **Kürzeste Stresszeit:** Gestartet wird bei **1 s** und nicht bei 0,1 s. Die 0,1-s-Dekade bringt wenig, weil die Messverzögerung im ms-Bereich liegt und der BS170 bei so kurzem Stress kaum degradiert. So reicht die Zeit, um während des Stresses zu senden.
- **Puffer:** kein Ring-Buffer, sondern ein linearer Buffer mit 5000 Punkten (10 kB). Gemessen wird in den Buffer, gesendet während des nächsten Stresses.

## Datenübertragung (Vorschlag, Doku `Datenformat_Rueckgabe.md`)

- **Aufbau:** ASCII-Header `#HDR TYPE=… N=… RANGE=… AVG=… DT_US=… DT_MIN_US=… LOG_Q24=… T_START_US=… T_STOP_US=… CYCLE=… T_STRESS_MS=…`, dann N × uint16 little endian, dann `#END SUM=…` (Summe mod 65536). Am Ende von MSM kommt `#DONE`.
- **Logarithmische Zeitachse:** `t(i+1) = t(i) + max(DT_MIN_US, (t(i)*LOG_Q24) >> 24)`. Nur Ganzzahlen, damit Firmware und Python bitgenau dieselbe Zeitachse berechnen.
- **Rechenbeispiel 1 ms bis 1 s, DT_MIN = 1 ms:** nur ≈ 960 Punkte statt 5000, ab ≈ 0,72 s logarithmisch.
- **Übertragungszeit:** 5000 Punkte = 10 kB. Bei 9600 Baud ≈ 10,4 s, bei 115200 Baud ≈ 0,87 s. Gesendet wird binär.
- Funktionsvorschläge `send_measurement_data()`, `log_calc_q24()` und `log_next_time()` stehen in der Doku. Mit gcc ist der Ablauf Firmware → Python getestet.

## Erkenntnisse und Probleme

- **Befehle können verloren gehen:** Der UART-Interrupt verwirft Zeichen, solange die vorige Zeile noch nicht abgeholt ist. Abhilfe: 20 ms Pause pro Befehl oder `OK`/`ERR`-Antwort.
- **Keine Rückmeldung:** Die Firmware antwortet nicht, unbekannte Befehle werden stillschweigend ignoriert.
- **Start-Flags** werden nicht zurückgesetzt, die Messungen laufen sonst endlos.
- **Range- und Enum-Defines** passen nicht zum Decoder. Python muss `25`/`50`, `0`/`1`, `BTI`/`HCD` und `STATIC`/`DYNAMIC` schicken.
- **TIM2-ISR:** CS geht sofort wieder hoch, obwohl die DMA nur gestartet ist; außerdem gibt es keinen RX-DMA.
- **TIM2 ist 16 Bit.** Für log-Abstände wird ARR im Interrupt pro Punkt neu geladen, lange Abstände werden zerlegt.
- **µs in uint32** laufen nach 71 min über. Die Standardwerte (letzter Zyklus 10 000 s) brauchen deshalb `uint64_t`.
- **Systemtakt unklar** (8 MHz HSI oder 72 MHz). Davon hängen SPI, `DT_MIN` und die Baudrate ab.

## Erstellte Dateien (alle in `PCB_test_code`)

- `Befehlsreferenz_Python_PC.md/.pdf`: welche Befehle Python für jede Messart schickt
- `Datenformat_Rueckgabe.md/.pdf`: Header, Datenformat, Zeitachse, C- und Python-Vorschlag
- `TODO_Firmware_MSM.md`: offene Punkte mit Ideen und Code-Vorschlägen
- `KONTEXT_Chat_MSM_08_11_2026.md`: diese Datei

## Nächste Schritte

Siehe `TODO_Firmware_MSM.md`. Kurz:

1. Keil-Build
2. Takt und `DT_MIN` messen
3. TIM2-ISR korrigieren
4. `OK`/`ERR`, Flags zurücksetzen, Baudrate
5. SysTick und TIM2 variabel, `uint64_t`
6. ID-VG als erste echte Messung
7. dann Transient, Stress und MSM

**Arbeitsweise:** Claude soll Änderungen zuerst als Vorschau zeigen und auf OK warten. Die Messroutinen programmiert das Team selbst. Quellen immer angeben.

## Quellen

- B. Kaczer et al., „Ubiquitous Relaxation in BTI Stressing – New Evaluation and Insights“, IEEE IRPS 2008
- T. Grasser et al., „The Universality of NBTI Relaxation and its Implications for Modeling and Characterization“, IEEE IRPS 2007
- H. Reisinger et al., „Analysis of NBTI Degradation- and Recovery-Behavior Based on Ultra Fast VT-Measurements“, IEEE IRPS 2006
- D. K. Schroder, J. A. Babcock, J. Appl. Phys. 94, 1 (2003)
- T. Grasser (Hrsg.), *Bias Temperature Instability for Devices and Circuits*, Springer 2014
- STMicroelectronics RM0008, PM0056, Datenblatt STM32F103xB (in `Software/firmware/Datenblätter_Cortex/`)
- TI ADS8866 Datenblatt (SBAS606)
- pySerial: <https://pyserial.readthedocs.io/en/latest/>
