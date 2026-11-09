# Dokumentation Pinbelegung FETCH V02.2

Vergleich zwischen der aktuellen Firmware (`PCB_test_code`, `PINs.h` vom 14.09.2026) und dem Schaltplan FETCH V02.2.
Die neue Belegung selbst steht in `PINBELEGUNG_FETCH_V02.2.md`.

## 1. Was sich geändert hat

### Verschoben

| Signal | Alt | Neu |
|---|---|---|
| `cal_Select_set` | PC0 | **PC2** |
| `cal_Select_Reset` | PC1 | **PC0** |
| `Range_Select_set` | PC2 | **PC3** |
| `Range_Select_Reset` | PC3 | **PC1** |
| `DAC_NRESET` | PB4 | **PB5** |
| 1-Wire Master 01 | PB0 | **PB9** |
| LEDs | PB8, PB9 | **PC8 bis PC11** |

Die vier Relais-Pins sind nur vertauscht. Falsch gelassene Makros kompilieren daher fehlerfrei, schalten aber das falsche Relais.
PB9 war früher `LED_GREEN` und ist jetzt der 1-Wire-Bus.

### Unverändert

PA1 `DAC_SPI_NCS`, PA2 `DAC_GAIN`, PA4 `ADC_SPI_NCS`, PA5 bis PA7 SPI1, PA9/PA10 USART1, PA13/PA14 SWD.

### Neu

| Pin | Signal | Zweck |
|---|---|---|
| PA3 | `SPI1_EN_SEND` | Gibt die Sender für CLK, MOSI und beide SYNC-Leitungen frei |
| PB12 | `SPI_ANALOG_EN` | Gibt den MISO-Sender auf der Analogkarte frei |
| PB14 | `PRE_KALIB_CARD` | Kartenerkennung Kalibrierkarte |
| PB15 | `PRE_ANALOG_CARD` | Kartenerkennung Analogkarte |
| PC5 | `OW2_MASTER_*` | 1-Wire zum DS18B20 auf der Analogkarte |

### Entfallen

| Makro | Alt | Grund |
|---|---|---|
| `PER_33V_PSU_EN` | PB11 | Alle Regler laufen fest, ihre Enable-Pins hängen an IN |
| `OPV_PSU_EN` | PB7 | wie oben |
| `ANALOG_5V_PSU_EN` | PB1 | wie oben |
| `ADC_NRESET` | PC13 | ADS8866 hat keinen Reset-Pin |
| `ADC_NALARM` | PC12 | ADS8866 hat keinen Alarm-Pin |
| `LED_GREEN`, `LED_RED` | PB9, PB8 | ersetzt durch die vier neuen LEDs |

`OW_BUS_MASTER_OUT/IN` heißt jetzt `OW1_MASTER_OUT/IN`. Der alte Name wurde im Code nirgends verwendet.

## 2. Signalweg SPI

Die SPI-Leitungen laufen differenziell (M-LVDS) über die Backplane:

```
STM32 SPI1 ── U12 SN65MLVD047 ══ Backplane ══ U25 SN65MLVD048 ── AD5689R / ADS8866
STM32 PA6  ── U11 SN65MLVD048 ══ Backplane ══ U27 SN65MLVD047 ── ADS8866 DOUT
```

- **Beide Enables sind Pflicht:** Laut Datenblatt sendet der SN65MLVD047 nur bei EN = High und EN# = Low. EN# liegt fest auf GND, und die Pull-downs R12 und R33 halten EN nach dem Reset auf Low.
- **Folge für die Firmware:** Ohne `SPI1_EN_SEND = 1` und `SPI_ANALOG_EN = 1` kommt nichts auf der Analogkarte an bzw. nichts zurück. Fehlt nur PB12, liest die Firmware falsche ADC-Werte, ohne dass ein Fehler auffällt.
- **Eine Analogkarte:** SYNC-Leitungen und `SPI1_ANALOG_EN` liegen an allen Slots parallel. Mit der jetzigen Belegung lässt sich daher nur eine Analogkarte betreiben.

## 3. Nötige Änderungen in der Firmware

### Kompiliert sonst nicht

| Datei | Änderung |
|---|---|
| `main.c` Zeile 34 bis 36 | Die drei `*_PSU_EN = 1` löschen |
| `ads8681.c` Zeile 52, 55 | `ADC_NRESET` entfällt, siehe ADC-Treiber unten |

### main.c

Direkt nach `spi1_init();` ergänzen:

```c
SPI1_EN_SEND = 1;
SPI_ANALOG_EN = 1;
```

### Relais-Puls beim Start beseitigt

Die alte `PIN_init()` setzt mit `GPIOC->BSRR = 0x300F` die Pins PC0 bis PC3 auf High. Auf V02.2 würde das über die MOSFETs Set- und Reset-Spule beider Relais gleichzeitig bestromen, bis `main.c` die Pins wieder löscht.
Die neue `PIN_init()` hält diese Pins Low.

### ADC-Treiber ersetzen

Auf der Analogkarte sitzt ein **ADS8866** (16 Bit, Referenz 2,5 V). Die Firmware enthält noch einen ADS8681-Treiber. Der ADS8866 hat keine Register, also kann `ads8681.c/.h` nicht angepasst, sondern nur ersetzt werden. Das betrifft auch `ADS8681_get_voltage()` und `ADS8681_get_current()`.

Ablauf im 3-Wire-CS-Modus (DIN = DVDD), mit `ADC_SPI_NCS` als CONVST:

1. Steigende Flanke an CONVST startet die Wandlung.
2. CONVST bleibt mindestens 8,8 µs High.
3. CONVST geht Low, das MSB liegt sofort an DOUT.
4. 16 Bit einlesen.
5. CONVST wieder High, die nächste Wandlung startet.

Der Strom berechnet sich laut Schaltplan aus `I = (V_ADC - 66,7 mV) * 3 / Rf`.

Das aktuelle SPI-Format CPOL 0 / CPHA 1 kann bleiben: Der AD5689R braucht es, und der ADS8866 lässt das Einlesen auf der fallenden Flanke zu, sofern die Hold-Zeit `th_CK_DO` eingehalten wird. Den Zahlenwert habe ich nicht geprüft.

### TIM2-Interrupt

`TIM2_IRQHandler` in `TIMER.c` setzt `ADC_SPI_NCS = 1` direkt nach dem Start des DMA-Transfers, also solange SPI noch taktet. Beim ADS8866 bricht das den Lesevorgang ab und startet mitten im Transfer eine neue Wandlung. CS darf erst im DMA-Fertig-Interrupt wieder hoch.

### Weitere Punkte

- `AD5689_init()` wird in `main.c` nicht aufgerufen. Die neue `PIN_init()` hält `DAC_NRESET` aber auf High, der DAC ist also nicht im Reset.
- PB4 wird nicht mehr benötigt, ein JTAG-Remap ist damit kein Thema.
- Ein 1-Wire-Treiber fehlt noch. Die beiden Busse sind fertig vorbereitet.

## 4. Vor der Inbetriebnahme prüfen

| # | Punkt | Warum | Prüfung |
|---|---|---|---|
| 1 | **UART TX/RX** | PA9 hängt am Netz `TGT_TX`, das am DAPLink-Pin `TGT_TX` endet. Sind die Pins aus Sicht des Moduls benannt, treffen TX und TX aufeinander | Doku des DAPLink-Moduls lesen, oder „SAFDAT READY“ am PC erwarten und an PA9 messen |
| 2 | **Semantik GND-Relais** | Laut Symbol verbindet „set“ TIA_IN mit dem TIA und „reset“ legt TIA_IN auf GND. `set_GND_Relai()` nutzt „set“, wird also vermutlich das Gegenteil seines Namens tun | Mit dem Multimeter messen, dann Funktion umbenennen oder tauschen |
| 3 | **Bereichsrelais** | Laut Symbol ist Reset = 100 kΩ und Set = 10 MΩ, das passt zur Firmware. Annahme: Das Symbol zeigt die Reset-Lage | Mit dem Multimeter messen |
| 4 | **Schaltplanstand** | Das Projekt wurde nach dem PDF-Export noch gespeichert, und ein Backup vom 18.10. existiert. Beide konnte ich nicht auslesen. Für das CORTEX-Blatt bestätigt dein Screenshot die Belegung, die übrigen Blätter stammen aus den PDFs | Prüfen, ob Digital-Hauptblatt und Analog-Blatt noch aktuell sind |

## 5. Kleine Unstimmigkeiten im Schaltplan

Alle ohne elektrische Wirkung, aber fürs Protokoll oder eine nächste Revision relevant:

- PB6 ist als `I2C1_PB7 SCL` beschriftet, richtig wäre `I2C1_PB6 SCL`.
- Die Pin-Beschriftungen weichen von den Netznamen ab: `SPI_ANALOG_EN` / `SPI1_ANALOG_EN`, `Pre_Kalibrate_card` / `Pre_Kalibration_card`, `cal_Select_*` / `GND_Relai_*`.
- Die Netze `USB_DP`/`USB_DM` an PA12/PA11 sind nirgends angeschlossen. Die PC-Verbindung läuft über das DAPLink-Modul.
- Die Bauteilnamen im PDF sind veraltet: Der Screenshot zeigt X1/X2 für die Quarze und H1/H2 für die Boot-Header.

## 6. Quellen

- Schaltpläne `SCH_digital_2026-10-15.pdf`, `SCH_analog_2026-10-15.pdf`, `SCH_Backplane_2026-10-16.pdf`
- Screenshot CORTEX-Blatt vom 03.11.2026
- Firmware `PCB_test_code`
- [SN65MLVD047 Datenblatt](https://mouser.com/ds/2/405/slls606a-121810.pdf)
- [ADS8866 Datenblatt, 3-Wire CS Mode](https://www.ti.com/document-viewer/ADS8866/datasheet/3-wire-cs-mode-sbas5573633)
