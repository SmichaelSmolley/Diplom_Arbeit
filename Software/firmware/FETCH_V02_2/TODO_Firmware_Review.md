# TO-DO Firmware FETCH_V02_2 – Code-Review

Stand 11.11.2026, 3. Durchsicht · `[x]` = erledigt, `[ ]` = offen, **NEU** = bei dieser Durchsicht gefunden.
Projekt bleibt bei **C90** (`v6Lang = 1`): kein `snprintf`, Variablen nur am Blockanfang, kein `for (int i = …)`, keine Binär-Literale `0b…`.
Ergänzt `TODO_Firmware_MSM.md` – Querverweise in Klammern, z. B. (MSM-TODO 7).

## Erledigt

- [x] `AD5689.c`: `uint16_t data`
- [x] `ADS8866.c`: richtiger Header (`ads8866.h`)
- [x] `NVIC.c`: `ICPR`/`ISER` mit `=`
- [x] `SEND_DATA.c`: `#END SUM=` wird gesendet, `uint32_t i`, Header-Puffer 265 Byte
- [x] `main.c`: `set_default_params()` über Zeiger, `init_all()`, `#include "relai.h"`, Startzustand passt (`SENSE_RANGE_10u` + `set_range_100k()`, `sense_mode_gnd = false` + `reset_GND_Relai()`)
- [x] `settings.c/.h`: `apply_settings()` + `measure_prepare()`
- [x] `UART.h/.c`: `uart_put_u32()` ohne `static`, Prototyp im Header
- [x] `SPI.c`: `RXDMAEN` nicht mehr in `spi1_init()`; `spi1_ADC_dma_begin()` / `spi1_ADC_dma_end()` vorhanden
- [x] leere `apply_settings.c/.h` gelöscht

## 1 – Warnungen / C90 (schnell)

- [ ] **NEU `SPI.c`:** `spi1_ADC_dma_end()` ruft `tim2_disable()` auf, aber `#include "TIMER.h"` fehlt → implizite Deklaration
- [ ] **NEU `SPI.c` Z. 102:** `uint8_t rx_data = …` steht nach Anweisungen (C90) → `uint8_t rx_data;` an den Funktionsanfang
- [ ] **NEU `TIMER.c` Z. 56/59/62:** `uint32_t total_divider/psc/arr` nach Anweisungen (C90) → an den Anfang von `init_tim2()`
- [ ] **NEU `ADS8866.c` Z. 26/28:** `uint16_t rx1;` und `int i;` stehen nach `spi1_mode(...)` (C90) → nach oben; `int i` ist unbenutzt → löschen; `#include "relai.h"` unnötig
- [ ] **NEU `AD5689.h`:** Binär-Literale `0b0001`, `0b1000`, `0b1001` gibt es in C90 nicht → `0x1`, `0x8`, `0x9`
- [ ] `SEND_DATA.c` Z. 51: `char END_buffer[20];` an den Funktionsanfang (C90); `sum` mit `(unsigned)` casten
- [ ] `SEND_DATA.c`: Bereichsprüfung `hdr->type < 5` vor `type_names[...]`
- [ ] `SEND_DATA.c/.h`: `send_measure_done()` → `"#DONE\r\n"`
- [ ] `AD5689.c`: `#include "TIMER.h"` fehlt (`wait_ms()` in `AD5689_init()`)
- [ ] `UART.h/.c`: `uart_put_string(const char *)`
- [ ] `main.c`: `void init_all()` → `static void init_all(void)`; `#include "clock.h"` + `dummy_buffer` entfernen; `"scpi_commands.h"` → `"SCPI_COMMANDS.h"`

## 2 – Start / Takt

- [ ] `main.c`: `SystemCoreClockUpdate();` als erste Zeile in `init_all()`
- [ ] `main.c` Z. 163: `wait_ms(10000)` = **10 s** bis `FETCH READY` – gewollt?
- [ ] Takt 72 MHz aus HSE 8 MHz einmal messen/prüfen (MSM-TODO 2)
- [ ] `AD5689_init()`: Power-Down-Befehl `0xFF3C` mit Datenblatt prüfen
- [ ] Schaltplan prüfen: DAC A = Gate, DAC B = Drain; `set_GND_Relai()` = Eingang auf GND

## 3 – Zeitbasis

- [ ] **SysTick-ms-Zeitbasis** (`millis()`) für Stresszeiten (MSM-TODO 7)
- [ ] `wait_ms()`: `int j < 7987*ms` **läuft ab ca. 269 000 ms (4,5 min) über**; nur bei 72 MHz und `-O0` richtig

## 4 – SPI / DMA / ADC (Transient + MSM)

- [ ] TIM2-ISR (`TIMER.c` Z. 11–20): CS geht sofort wieder hoch, bevor der DMA gesendet hat; RX-DMA (`spi1_rx_dma()`) wird nicht gestartet; kein Ziel-Puffer/Index für die Messwerte → CS erst im **DMA-Transfer-Complete-Interrupt von Kanal 2** hochsetzen (MSM-TODO 3)
- [ ] Ablauf im DMA-Betrieb festlegen: Wandlung starten (CONVST/CS) → Wandlungszeit abwarten → 2 Byte per DMA lesen → Wert in Puffer, Index++
- [ ] `spi1_ADC_dma_end()` in **jedem** Abbruchpfad aufrufen (ABORT, Fehler, Ende)
- [ ] MSM: kein DAC-Befehl (Polling) zwischen `begin` und `end`
- [ ] `ADS8866_GET_CONV()`: Wandlungszeit `wait_us(10)` mit Datenblatt/Oszi prüfen
- [ ] Stromformel für Python: I = raw/65536 · 2,5 V / (STAGE_GAIN · R_f), STAGE_GAIN = 10k/30k (MSM-TODO 15)

## 5 – Kommunikation

- [ ] UART-Empfang: Zeichen gehen verloren, solange `uart_rx_complete == true` → Ringpuffer/zweiter Zeilenpuffer (`UART.c` Z. 44–70)
- [ ] `abort_requested` in allen Messschleifen prüfen
- [ ] `OK`/`ERR`-Antwort, `SENSE_MODE_ZCORRECT=`, `?`-Abfragen, Range-/Enum-Makros (MSM-TODO 4, 14)

## 6 – Hardware-Einstellungen

- [ ] `SOURce_RANGE 25/50` → DAC-Bereich (`DAC_GAIN`) + `volt_to_dac()` für die Endstufe (siehe `Dokumentation/TO-DO.md`)

## 7 – Messroutinen (`measure.c`, alle noch leer)

- [ ] `measure.c`: `settings.h` und `SEND_DATA.h` einbinden
- [ ] Am Anfang jeder Messung `measure_prepare()`, am Ende DAC 0 V (Gate zuerst, dann Drain) und **Start-Flag zurücksetzen**, auch bei ABORT (MSM-TODO 5)
- [ ] `IDVG()` (Polling): Drain setzen → Gate-Sweep → Einschwingzeit → AVG × `ADS8866_GET_CONV()` → Header + Puffer senden (MSM-TODO 11)
- [ ] `transient()` (DMA + TIM2): Befehle für Dauer und Abtastrate (MSM-TODO 12)
- [ ] `stress()`: STATIC/DYNAMIC, BTI (Drain 0 V)/HCD, Nachmessung **ohne** erneutes `measure_prepare()`
- [ ] `MSM()`: `measure_prepare()` nur einmal am Anfang; `log_calc_q24()` während des Stresses, `log_next_time()` pro Punkt; `#DONE` am Ende (MSM-TODO 13)
- [ ] `wait_temp_equi()` + `temp.c/.h` (DS18B20, leer)
- [ ] Messpuffer `uint16_t buffer[5000]` **static/global**

## Quellen

- Eigener Code: `FETCH_V02_2/*.c, *.h`, `PCB_test.uvprojx`
- Eigene Doku: `TODO_Firmware_MSM.md`, `Befehlsreferenz_Python_PC.md`, `Datenformat_Rueckgabe.md`
- ST RM0008 (SPI mit DMA Kap. 25.3.9, DMA Kap. 13, TIM2) und PM0056 (NVIC, SysTick) – in `Software/firmware/Datenblätter_Cortex/`
- TI ADS8866: https://www.ti.com/lit/ds/symlink/ads8866.pdf · AD5689R: `Hardware/Datasheet/AD5689R_5687R.pdf`
- C90-Regeln: https://en.cppreference.com/w/c/99 (was erst ab C99 erlaubt ist)
