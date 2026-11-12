# Dateinamen der Messdateien (.h5)

Stand 12.11.2026 · Schema im Stil der Reisinger-Software (`ar_…`, `tr_…`).
Umsetzung: `dateinamen.py`, aufgerufen beim Empfang jedes Datenblocks (`gui.py` → `_handle_block`).

## Regel

- **Jeder Datenblock = eigene Datei.** Bei MSM also eine Datei pro Zyklus.
- Ordner: `messungen/<Device>/`
- Name: `<Präfix>_<Device>_<Bereich>[_<Stress>|_VG<…>][_TS<Zeit>|_ref][_c<Zyklus>]_<Datum>.h5`

| Teil | Inhalt | Beispiel |
|---|---|---|
| Präfix | `iv` = ID-VG, `tr` = Transient, `sp` = Spot | `tr` |
| Device | Feld „Device“, nur `A–Z a–z 0–9 -` (Rest wird `-`), leer = `unbenannt` | `BS170-01` |
| Bereich | Strombereich aus der GUI-Einstellung (gesendetes `SENSE_RANGE=`, nicht aus dem MCU-Header): `I100n` = 100 nA, `I10u` = 10 µA | `I100n` |
| Stress | Typ + Gate-Stressspannung | `BTI5V0`, `HCD2V5` |
| VG | nur Transient einzeln: Gate-Spannung | `VG1V5` |
| TS | **gesamte** Stresszeit (Header `T_STRESS_MS`): < 1 s in ms, sonst ganze s | `TS500ms`, `TS11s` |
| ref | MSM-Referenzmessung vor dem ersten Stress (statt TS) | `ref` |
| c | MSM-Zyklus, 2-stellig (Header `CYCLE`) | `c00`, `c03` |
| Datum | Start der Messung; bei MSM **Start des ganzen Laufs** (alle Zyklen gleich) | `20261112-1430` |

Spannungen: Dezimalpunkt als `V` (`5V0` = 5,0 V, `1V25` = 1,25 V), negativ mit `m` (`m2V4` = −2,4 V).
Existiert die Datei schon: `_2`, `_3`, … anhängen.

## Beispiele

```
messungen/BS170-01/
├─ iv_BS170-01_I10u_20261112-1430.h5                    ID-VG einzeln
├─ tr_BS170-01_I100n_VG1V5_20261112-1435.h5              Transient einzeln
├─ iv_BS170-01_I10u_BTI5V0_TS60s_20261112-1440.h5       Stress 60 s -> Nachmessung ID-VG
├─ tr_BS170-01_I100n_BTI5V0_ref_c00_20261112-1500.h5     MSM Referenz
├─ tr_BS170-01_I100n_BTI5V0_TS1s_c01_20261112-1500.h5    MSM Zyklus 1
├─ tr_BS170-01_I100n_BTI5V0_TS11s_c02_20261112-1500.h5   MSM Zyklus 2 (1 s + 10 s)
└─ tr_BS170-01_I100n_BTI5V0_TS111s_c03_20261112-1500.h5  MSM Zyklus 3
```

## Offen / noch festzulegen

- [x] Strombereich im Namen (`I100n` / `I10u`)
- [ ] Temperatur (z. B. `T25`) – vorerst nicht, später eventuell (Reisinger: `T75`)
- [ ] Datum mit Sekunden (`20261112-143005`), falls zwei Läufe in derselben Minute starten?
- [ ] Device-Namen im Team einheitlich festlegen (z. B. `BS170-01`, `W1-D12`)

## Quellen

- `SENSE_RANGE= 0/1`: `Befehlsreferenz_Python_PC.md`, `gui.py` (`SENSE_RANGES`)

- Header-Felder `TYPE`, `CYCLE`, `T_STRESS_MS`: `Datenformat_Rueckgabe.md` Kap. 3, 7
- Windows: unerlaubte Zeichen in Dateinamen (`\ / : * ? " < > |`): https://learn.microsoft.com/de-de/windows/win32/fileio/naming-a-file
