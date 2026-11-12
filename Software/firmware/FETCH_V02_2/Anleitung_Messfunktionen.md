# Messfunktionen schreiben (measure.c)

Kurzanleitung für `IDVG()`, `transient()`, `stress()`, `MSM()`, `wait_temp_equi()`.
C90: Variablen am Blockanfang, `/* */`-Kommentare, kein `snprintf`.

## 1. Grundgerüst – gleich für jede Messung

```c
void MESSUNG(Measure_Param *p)
{
    if (measure_prepare(p))          /* Relais, DAC 0 V, 1 s warten */
    {
        /* Spannungen setzen, messen, senden */
    }
    AD5689_set_Voltage(0.0f, AD5689_ADDR_DAC_A);   /* Gate zuerst */
    AD5689_set_Voltage(0.0f, AD5689_ADDR_DAC_B);   /* dann Drain */
    p->START_FLAG   = false;         /* sonst startet sie endlos neu */
    abort_requested = false;
    LED_MEASURE     = 0;
}
```

## 2. Regeln

| Regel | Warum |
|---|---|
| Am Anfang `measure_prepare()` | Relais/Strombereich stimmen, Bauteil spannungsfrei, Einschwingen |
| Spannung: zuerst Drain, dann Gate. Aus: zuerst Gate, dann Drain | Kein Stromstoß durch den TIA |
| Start-Flag am Ende **immer** zurücksetzen | Hauptschleife ruft die Funktion sonst wieder auf |
| Warten nur mit `delay_ms_abortable()` | ABORT muss jederzeit gehen |
| In Schleifen `abort_requested` prüfen | dto. |
| Nach Stress **nicht** `measure_prepare()` und nicht warten | Recovery beginnt sofort, sonst falsche ΔV_th |
| Puffer: gemeinsames `static uint16_t meas_buffer[5000]` | Stack hat nur ca. 1 KB |
| Polling: ID-VG, Spot, DAC. DMA + TIM2: nur Transient- und MSM-Aufnahme | siehe Abschnitt 4 |

## 3. Daten senden

```c
Data_Header hdr;               /* alle Felder setzen, unbenutzte = 0 */
hdr.type = DATA_...;  hdr.n = punkte;  hdr.range = p->sense_range;  hdr.avg = p->sense_average;
/* je nach Typ: dt_us, dt_min_us, log_q24, t_start_us, t_stop_us, cycle, t_stress_ms */

send_measure_header(&hdr);
send_measure_buffer(&hdr, meas_buffer);   /* Rohdaten + "#END SUM=" */
send_measure_done();                      /* nur am Ende von MSM: "#DONE" */
```

Bei ABORT trotzdem senden, mit `hdr.n` = tatsächlich gemessene Punkte.

| TYPE | gesetzte Zeitfelder |
|---|---|
| `DATA_IDVG` | keine (x-Achse = V_G, kennt Python) |
| `DATA_TRANSIENT` | `t_start_us`, `dt_us` |
| `DATA_SPOT` | `t_start_us` (= Mess-Verzögerung), `cycle`, `t_stress_ms`, `n = 1` |
| `DATA_MSM_IDVG` | `cycle`, `t_stress_ms` |
| `DATA_MSM_TRANSIENT` | `t_start_us`, `t_stop_us`, `dt_min_us`, `log_q24`, `cycle`, `t_stress_ms` |

## 4. Ein Messpunkt

**Polling** (ID-VG, Spot):
```c
sum = 0;
for (k = 0; k < avg; k++) sum += ADS8866_GET_CONV();
wert = (uint16_t)((sum + avg / 2) / avg);
```

**DMA + TIM2** (Transient, MSM-Recovery):
```c
spi1_ADC_dma_begin();
init_tim2(abtastrate_hz);
tim2_enable();
/* warten bis n Punkte im Puffer oder ABORT */
spi1_ADC_dma_end();            /* IMMER, auch bei ABORT */
```
Zwischen `begin` und `end` keinen DAC-Befehl senden.

## 5. Die einzelnen Messungen

### ID-VG (`SENSE_MODE_IDVG= TRUE`)
1. `measure_prepare()`
2. Drain = `source2_voltage`
3. Für i = 0 … n−1: Gate = `sweep_start + i·step` (nicht aufaddieren) → `sweep_time` ms warten → Punkt messen
4. Senden als `DATA_IDVG`

n = (|stop − start| / step) + 1. Den Sweep als eigene Funktion `idvg_sweep(p, type, cycle, t_stress)` ohne `measure_prepare()` schreiben → wiederverwendbar für Stress und MSM.

### Transient (`SENSE_MODE_TRANSIENT= TRUE`)
1. `measure_prepare()`
2. Drain = `source2_voltage`, Gate = `source1_voltage`
3. Aufnahme mit DMA + TIM2, n Punkte im Abstand `dt_us`
4. Senden als `DATA_TRANSIENT` (`dt_us` = **tatsächlicher** Timer-Abstand aus PSC/ARR)

Offen: Befehle für Dauer und Abtastrate fehlen noch im Decoder.

### Stress (`STRESS_OUTput= ON`)
1. `measure_prepare()`
2. Drain = BTI: 0 V, HCD: `stress_drain_voltage`; Gate = `stress_voltage`
3. STATIC: `stress_time` ms. DYNAMIC: `stress_cycles` × (Gate an `on_time` / Gate 0 V `off_time`)
4. Gate auf 0 / Lesespannung, Drain auf Lesespannung
5. Sofort danach (ohne Warten): `stress_after_idvg` → `idvg_sweep()`, `stress_after_transient` → Transient-Aufnahme
6. Flag: `stress_output = false`

Lange Zeiten mit SysTick-`millis()`, nicht mit `wait_ms()` (Überlauf ab 4,5 min).

### MSM (`SENSE_MODE_MSM= TRUE`)
```
measure_prepare()                         nur EINMAL
falls msm_initial_measure: messen (cycle 0, t_stress 0)
für k = 1 … msm_cycles:
    t_k = msm_start_time · msm_time_factor^(k−1)
    Stress t_k ms  (Startzeit merken, über millis() bis Ende warten)
    -> währenddessen: vorigen Block senden, log_calc_q24() rechnen
    Stress aus, sofort Lesespannungen
    msm_meas_delay ms warten
    messen: SPOT / IDVG / TRANSIENT (cycle k, t_stress = Summe)
send_measure_done()
```
- SPOT: 1 Punkt per Polling, sofort weiter mit dem nächsten Stress
- IDVG: `idvg_sweep(p, DATA_MSM_IDVG, k, summe)`
- TRANSIENT: log. Zeitpunkte bis Stresszeit (`msm_recovery_stress_time`) oder `msm_recovery_time`; pro Punkt `t = log_next_time(t, dt_min, q24)`
- Senden des Blocks **während des nächsten Stresses**, nicht davor (sonst verlängert sich die Recovery)

### Temperatur (`Temp_equilibrium_wait= TRUE`)
DS18B20 zyklisch lesen, warten bis Änderung < Schwelle über x s, Flag zurücksetzen. `temp.c/.h` sind noch leer.

## 6. Checkliste pro Funktion

- [ ] `measure_prepare()` am Anfang (außer Nachmessungen in Stress/MSM)
- [ ] Spannungsreihenfolge Drain → Gate, aus: Gate → Drain
- [ ] Alle Wartezeiten abbrechbar
- [ ] Header vollständig, `n` = gemessene Punkte
- [ ] Bei DMA: `spi1_ADC_dma_end()` in jedem Ausgang
- [ ] DAC 0 V, Start-Flag `false`, `abort_requested = false`, LED aus

## Quellen

- `Befehlsreferenz_Python_PC.md` – Kap. 3 (Parameter), 4 (Start-Flags), 6–8 (Abläufe)
- `Datenformat_Rueckgabe.md` – Kap. 2–5 (Header, Zeitachse), 7 (MSM-Ablauf, `#DONE`), 8 (`log_calc_q24`, `log_next_time`)
- `TODO_Firmware_MSM.md` – Punkte 7 (SysTick), 11–13 (ID-VG, Transient, MSM)
- `Dokumentation/Stressing.md` – Drain-Strom beim Stressen
- B. Kaczer et al., „Ubiquitous Relaxation in BTI Stressing“, IEEE IRPS 2008 – Recovery beginnt sofort nach Stressende
- K. Tselios, Dissertation TU Wien 2025, Kap. 6.1–6.2 – ID-VG, MSM, RTN-Messung
