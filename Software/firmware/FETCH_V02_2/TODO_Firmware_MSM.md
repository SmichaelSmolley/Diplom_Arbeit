# TO-DO Firmware PCB_test_code: MSM, Timing, Datenübertragung

Stand 08.11.2026 · Ideen und Code-**Vorschläge**, noch **nicht** im Code umgesetzt.
Zugehörige Dokus im selben Ordner: `Befehlsreferenz_Python_PC.md`, `Datenformat_Rueckgabe.md`, `KONTEXT_Chat_MSM_08_11_2026.md`.

## Übersicht (empfohlene Reihenfolge)

- [ ] 1. Projekt in Keil bauen (MSM-Parameter sind schon drin)
- [ ] 2. Systemtakt klären und `DT_MIN` messen
- [ ] 3. TIM2-ISR prüfen: CS geht zu früh hoch, kein RX-DMA
- [ ] 4. `OK`/`ERR`-Antwort im Decoder
- [ ] 5. Start-Flags am Ende jeder Messfunktion zurücksetzen
- [ ] 6. Baudrate auf 115200 erhöhen und mit der Optokoppler-Isolation testen
- [ ] 7. ms-Zeitbasis mit SysTick (für Stresszeiten)
- [ ] 8. TIM2 mit variabler Periode (logarithmische und lineare Messzeitpunkte)
- [ ] 9. Zeiten auf `uint64_t` umstellen (Überlauf nach 71 min)
- [ ] 10. `DATA_SEND.c/.h` einbauen (siehe `Datenformat_Rueckgabe.md`)
- [ ] 11. ID-VG als erste echte Messung, Vergleich mit Keithley
- [ ] 12. Transient: Befehle für Dauer und Abtastrate
- [ ] 13. `MSM()` umsetzen
- [ ] 14. Aufräumen: Range- und Enum-Defines, `ZCORRECT`, `?`-Abfragen
- [ ] 15. Python: `raw_to_current()`
- [ ] 16. `Dokumentation/Firmware_Doku_PCB_test_code.pdf` aktualisieren

---

## 1. Keil-Build

In `COMMAND_DECODE.h/.c`, `SCPI_COMMANDS.h`, `main.c` und `measure.c` wurden die MSM-Parameter ergänzt, außerdem der `SOURce1/2_PROT`-Fix (Länge 15 → 14). Geprüft wurde bisher nur mit gcc (Syntax). Ein echter Build mit dem ARM-Compiler in Keil fehlt noch.

## 2. Systemtakt und DT_MIN

**Idee:** Alle Zeiten (Timer, SPI, UART) hängen von `SystemCoreClock` ab. Laut Firmware-Doku läuft der Chip auf dem internen 8-MHz-Takt (HSI), `clock_init()` wird aber nicht aufgerufen. Was tatsächlich läuft, bestimmt `SystemInit()` aus dem RTE.

- `SystemCoreClock` im Debugger ansehen, oder einen Pin toggeln und mit dem Oszi messen.
- SPI1: `spi1_set_baud(5)` ergibt f_PCLK/64. Bei 8 MHz ist SCK = 125 kHz, ein 16-Bit-Wert dauert dann ≈ 130 µs. Bei 72 MHz sind es ≈ 15 µs.
- **`DT_MIN` = AVG × Dauer einer Wandlung (inkl. SPI) + Overhead.** Mit dem Oszi am ADC-CS messen. Bei AVG = 100 sind grob 1 bis 13 ms zu erwarten.

## 3. TIM2-ISR: CS zu früh und kein RX-DMA

**Problem (aktueller Code in `TIMER.c`):**

```c
ADC_SPI_NCS = 0;
spi1_tx_dma(spi_dummy, 2);   // startet DMA nur, wartet NICHT
ADC_SPI_NCS = 1;             // -> CS geht hoch, bevor die 2 Byte draussen sind
```

Außerdem wird kein RX-DMA gestartet, die gelesenen Daten landen nirgends.

**Idee:**

- RX-DMA (Kanal 2) **und** TX-DMA (Kanal 3) starten.
- CS erst im **DMA-Transfer-Complete-Interrupt** von RX (Kanal 2) auf 1 setzen.
- Datenblatt ADS8866 beachten: Die CONVST-Flanke startet die Wandlung. Je nach 3-Wire- oder 4-Wire-Modus ist das Timing anders.

```c
/* Skizze */
void DMA1_Channel2_IRQHandler(void)          // RX fertig
{
    if (DMA1->ISR & DMA_ISR_TCIF2)
    {
        DMA1->IFCR = DMA_IFCR_CTCIF2;
        ADC_SPI_NCS = 1;
        adc_sample_ready = true;             // Wert liegt im RX-Buffer
    }
}
```

## 4. OK/ERR-Antwort im Decoder

**Idee:** Python sieht sofort, ob ein Befehl angekommen ist und erkannt wurde. Damit braucht es keine 20-ms-Pausen mehr: Python schickt die nächste Zeile erst nach `OK`.

```c
/* COMMAND_DECODE.h */
bool get_Decode_Parameter(char* command, Measure_Param* Parameter);

/* COMMAND_DECODE.c: am Ende der if/else-if-Kette */
	else
	{
		return false;          // unbekannter Befehl
	}
	return true;
}

/* main.c */
if (uart_string_received())
{
    if (get_Decode_Parameter(uart_get_string(), &measure))
        uart_put_string("OK\r\n");
    else
        uart_put_string("ERR\r\n");
}
```

Einschränkung: Ein falscher Wert bei einem bekannten Befehl (z. B. `SENSE_MODE_IDVG= JA`) liefert so trotzdem `OK`. Wenn nötig, in den `ON`/`OFF`- bzw. `TRUE`/`FALSE`-Zweigen ein `else return false;` ergänzen.

## 5. Start-Flags zurücksetzen

Am Ende von `IDVG()`, `transient()`, `stress()`, `wait_temp_equi()` und `MSM()`:

```c
param->sense_mode_idvg = false;        // bzw. passendes Flag
uart_put_string("#DONE\r\n");          // Python weiss: fertig
```

Sonst ruft die Hauptschleife die Funktion endlos wieder auf.

## 6. Baudrate

`main.c`: `uart1_set_baud(9600)` durch `uart1_set_baud(115200)` ersetzen, ebenso `USART_BAUD` in `sys_hard_settings.h`.

- Die Grenze setzen USB-UART-Chip und Optokoppler (Datenblatt: max. Datenrate bzw. Propagation Delay).
- Zum Vergleich: 5000 Punkte binär (10 kB) brauchen bei 9600 Baud ≈ 10,4 s, bei 115200 Baud ≈ 0,87 s, bei 1 MBaud ≈ 0,1 s.
- Ein Fehler der Baudrate ist bei 8 MHz HSI ohne PLL relativ groß, BRR-Rundung prüfen (RM0008, USART).

## 7. ms-Zeitbasis mit SysTick

**Idee:** `wait_ms()` ist eine Zählschleife und blockiert. Für MSM muss die Stresszeit **während des Sendens** weiterlaufen. Deshalb kommt ein Millisekundenzähler über SysTick dazu:

```c
volatile uint32_t ms_ticks = 0;

void SysTick_Handler(void)
{
    ms_ticks++;
}

void systick_init(void)
{
    SysTick_Config(SystemCoreClock / 1000u);   // 1 ms
}

/* Verwendung */
uint32_t t0 = ms_ticks;
/* ... Daten senden ... */
while ((ms_ticks - t0) < stress_ms && !abort_requested) { }
```

`ms_ticks - t0` funktioniert auch über den Überlauf hinweg (unsigned). Der Zähler läuft erst nach 49 Tagen über.

## 8. TIM2 mit variabler Periode (log und linear)

**Idee:** Das bisherige `init_tim2(freq)` stellt nur eine feste Frequenz ein. Für logarithmische Messzeitpunkte wird im Interrupt nach jedem Punkt eine **neue Periode** in `ARR` geladen.

- 1 Tick = 1 µs, also PSC = SystemCoreClock/1 000 000 − 1.
- TIM2 ist beim F103 **16 Bit**, die längste Periode ist 65,5 ms. Längere Abstände werden in mehrere Perioden zerlegt.
- `ARPE` aus: Der neue `ARR` gilt sofort. Das ist unkritisch, solange die Periode ≫ ISR-Latenz ist (bei ≥ 1 ms gegeben). Beim Zerlegen deshalb halbieren, damit das Reststück nie winzig wird.
- Die Zeit driftet nicht, weil der Zähler beim Update-Event in Hardware neu startet.
- Mit `q24 = 0` ist der Abstand immer `dt_min`, also linear. Dieselbe Funktion dient damit auch für den normalen Transienten.

```c
static volatile uint32_t tim_t_us;      // aktueller Soll-Zeitpunkt ab Start [us]  (-> uint64_t, siehe Punkt 9)
static volatile uint32_t tim_rest_us;   // Rest bis zum naechsten Punkt
static volatile bool     tim_point_due; // Flag: Messpunkt jetzt aufnehmen
static uint32_t tim_dt_min, tim_q24;

static void tim2_load(uint32_t us)
{
    uint32_t chunk;

    if (us > 2u * 65536u)      chunk = 65536u;
    else if (us > 65536u)      chunk = us / 2u;
    else                       chunk = us;

    TIM2->ARR   = (uint16_t)(chunk - 1u);
    tim_rest_us = us - chunk;
}

/* Start bei "Stress aus". q24 = 0 -> linear mit dt_min */
void tim2_start_log(uint32_t t_start_us, uint32_t dt_min_us, uint32_t q24)
{
    RCC->APB1ENR |= RCC_APB1ENR_TIM2EN;
    TIM2->CR1 &= ~(TIM_CR1_CEN | TIM_CR1_ARPE);

    TIM2->PSC = (uint16_t)(SystemCoreClock / 1000000u - 1u);
    TIM2->EGR = TIM_EGR_UG;
    TIM2->SR  = ~TIM_SR_UIF;

    tim_dt_min    = dt_min_us;
    tim_q24       = q24;
    tim_t_us      = t_start_us;
    tim_point_due = false;
    tim2_load(t_start_us);
    TIM2->CNT = 0;

    TIM2->DIER |= TIM_DIER_UIE;
    NVIC_SetPriority(TIM2_IRQn, 1);
    NVIC_EnableIRQ(TIM2_IRQn);
    TIM2->CR1 |= TIM_CR1_CEN;
}

void TIM2_IRQHandler(void)
{
    uint32_t next;

    if (TIM2->SR & TIM_SR_UIF)
    {
        TIM2->SR = ~TIM_SR_UIF;

        if (tim_rest_us > 0)
        {
            tim2_load(tim_rest_us);
            return;
        }

        tim_point_due = true;

        next = log_next_time(tim_t_us, tim_dt_min, tim_q24);
        tim2_load(next - tim_t_us);
        tim_t_us = next;
    }
}
```

So sieht die Messschleife aus:

```c
tim2_start_log(t_start, dt_min, q24);
while (n < n_max && tim_t_us <= t_stop && !abort_requested)
{
    while (!tim_point_due && !abort_requested) { }
    tim_point_due = false;
    buffer[n++] = mittelwert_aus_avg_wandlungen();   // muss < dt_min dauern!
}
tim2_disable();
```

`log_calc_q24()` und `log_next_time()` stehen in `Datenformat_Rueckgabe.md`, Kapitel 8.

## 9. Zeiten auf uint64_t

**Problem:** µs in `uint32_t` laufen nach 2³² µs ≈ **71,6 min** über. Mit den Standardwerten (5 Zyklen, Start 1 s, Faktor 10, Recovery = Stresszeit) hat der letzte Zyklus 10 000 s Recovery, das sind 10¹⁰ µs. Das ist zu groß.

**Idee:**

- `tim_t_us`, `tim_rest_us`, `t_start_us` und `t_stop_us` als `uint64_t`;
- `log_next_time()` mit `uint64_t t_us`: das Produkt `t * q24` passt bei t < 2⁴⁰ µs (≈ 12 Tage) noch in 64 Bit;
- Header: `uart_put_u64()` statt `uart_put_u32()`;
- Python ist das egal (beliebig große int).

```c
static void uart_put_u64(uint64_t v)
{
    char buf[20];
    int i = 0;

    if (v == 0) { uart_put_char('0'); return; }
    while (v > 0) { buf[i++] = (char)('0' + (v % 10)); v /= 10; }
    while (i > 0) uart_put_char(buf[--i]);
}

uint64_t log_next_time(uint64_t t_us, uint32_t dt_min_us, uint32_t q24)
{
    uint64_t gap = (t_us * q24) >> 24;
    if (gap < dt_min_us) gap = dt_min_us;
    return t_us + gap;
}
```

Hinweis: 64-Bit-Division (`v / 10`) ist am Cortex-M3 eine Bibliotheksfunktion und langsam. Für den Header (ein paar Zahlen) ist das egal.

## 10. DATA_SEND.c/.h

Komplett ausgearbeitet in `Datenformat_Rueckgabe.md` (Kapitel 8), inklusive Python-Empfang (Kapitel 9). Auf `uint64_t` anpassen (Punkt 9). Mit gcc getestet: Firmware-Ausgabe → Python-Parser funktioniert.

## 11. ID-VG als erste echte Messung

Mit der Keithley-Messung vergleichen (`Dokumentation/Keithley_23_24_10meg.xlsx`, `Device#01_idvg_*`). Wenn beide übereinstimmen, passen DAC, TIA, ADC und Umrechnung.

## 12. Transient: Dauer und Abtastrate

Dafür gibt es noch keine Befehle. Vorschlag:

| Befehl | Feld | Einheit |
|---|---|---|
| `SENSE_TRANSIENT_TIME= <ms>` | `sense_transient_time` | ms (Dauer) |
| `SENSE_TRANSIENT_DT= <us>` | `sense_transient_dt` | µs (Abstand, ≥ `DT_MIN`) |

Gemessen wird mit `tim2_start_log(0, dt, 0)`, also linear.

## 13. MSM() umsetzen: Ablauf-Skizze

```c
void MSM(Measure_Param *p)
{
    /* 0. Pruefen: bei TRANSIENT + RECOVERY_STRESS_TIME=FALSE muss recovery_time > 0 sein;
          start_time >= Sendezeit eines vollen Blocks + Reserve -> sonst "ERR" und return */
    uint64_t t_stress_ms = p->msm_start_time;
    uint64_t sum_ms      = 0;
    bool     pending     = false;          // liegt ein Block zum Senden bereit?

    if (p->msm_initial_measure)
    {
        messphase(p, 0, 0);                // Block CYCLE=0 in Buffer
        pending = true;
    }

    for (uint32_t c = 1; c <= p->msm_cycles && !abort_requested; c++)
    {
        stress_ein(p);                     // STRESS_VOLTage / DRAIN, TIA-Eingang auf GND
        uint32_t t0 = ms_ticks;

        if (pending) { send_measurement_data(&hdr, buffer); pending = false; }

        while ((ms_ticks - t0) < t_stress_ms && !abort_requested) { }

        stress_aus_lesespannung_an(p);     // SOURce1/2_VOLTage, TIA ans DUT
        sum_ms += t_stress_ms;

        messphase(p, c, sum_ms);           // SPOT / IDVG / TRANSIENT -> Buffer + hdr
        pending = true;

        t_stress_ms = (uint64_t)(t_stress_ms * p->msm_time_factor);
    }

    if (pending) send_measurement_data(&hdr, buffer);
    send_measurement_done();
    alles_auf_0V();
    p->sense_mode_msm = false;
}
```

- **SPOT:** `wait meas_delay`, dann ein gemittelter Punkt, die Recovery wird nicht abgewartet.
- **IDVG:** Sweep wie in `IDVG()`, die Recovery wird nicht verwendet.
- **TRANSIENT:** `t_rec = msm_recovery_stress_time ? t_stress : msm_recovery_time`, gemessen mit `tim2_start_log(meas_delay_us, dt_min, q24)`.
- **Achtung beim Umschalten Stress → Messen:** Die Reihenfolge der Relais und Spannungen muss den TIA schützen (siehe `Dokumentation/Stressing.md`).

## 14. Aufräumen

- **`SCPI_COMMANDS.h`:** `SOURce_RANGE(1, SOURce_RANGE_25)` erzeugt `"SOURce1_RANGE= SOURce_RANGE_25"`, der Decoder erwartet aber `25`. Dasselbe gilt für `SENSE_RANGE` (erwartet 0/1), `STRESS_TYPE` (BTI/HCD) und `STRESS_MODE` (STATIC/DYNAMIC). Lösung: Die Makros mit dem Literal aufrufen (z. B. `SOURce_RANGE(1, 25)`, `STRESS_TYPE(BTI)`) und das im Kommentar vermerken, oder den Decoder auf die Enum-Namen erweitern.
- **`SENSE_MODE_ZCORRECT=`:** Decode-Zweig fehlt, `sense_zcorrect` wird nie gesetzt.
- **`?`-Abfragen:** Keine davon wird beantwortet.
- **`SENSE_MODE_MEASUREMENT=`:** wird decodiert, aber nirgends ausgewertet.

## 15. Python: raw_to_current()

Die Umrechnung hängt von ADC-Referenz (2,5 V), ADS8866-Format, Nachverstärker (−10/30) und Rf ab (`RANGE`: 10 MΩ oder 100 kΩ). Die Formel aus dem Schaltplan herleiten und mit einer Referenzmessung prüfen.

## 16. Firmware-Doku aktualisieren

`Dokumentation/Firmware_Doku_PCB_test_code.pdf` kennt MSM, das Datenformat und die neuen Timer-Funktionen noch nicht.

---

## Quellen

- STMicroelectronics RM0008: Kap. TIM2–TIM5 (PSC, ARR, ARPE, Update-Event), DMA, SPI, USART, RCC. Liegt in `Software/firmware/Datenblätter_Cortex/`
- STMicroelectronics PM0056 (Cortex-M3: SysTick, keine FPU, UMULL), ebenfalls in `Datenblätter_Cortex/`
- TI ADS8866 Datenblatt (SBAS606), Digital Interface / CONVST: <https://www.ti.com/product/ADS8866>
- pySerial: <https://pyserial.readthedocs.io/en/latest/>
- B. Kaczer et al., „Ubiquitous Relaxation in BTI Stressing – New Evaluation and Insights“, IEEE IRPS 2008
- T. Grasser et al., „The Universality of NBTI Relaxation and its Implications for Modeling and Characterization“, IEEE IRPS 2007
