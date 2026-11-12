#include <stdio.h>
#include <stm32f10x.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

#include "COMMAND_DECODE.h"
#include "settings.h"
#include "relai.h"
#include "AD5689.h"
#include "TIMER.h"
#include "PINs.h"
#include "UART.h"

#define SETTLE_MS 1000u      /* Einschwingen nach Relais/DAC (Temperatur, TIA) */

void apply_settings(const Measure_Param *p)
{
	if (p->sense_range == SENSE_RANGE_100n) set_range_10meg();
	else                                    set_range_100k();

	if (p->sense_mode_gnd) set_GND_Relai();
	else                   reset_GND_Relai();

	AD5689_set_Voltage(0.f, AD5689_ADDR_DAC_A);
	AD5689_set_Voltage(0.f, AD5689_ADDR_DAC_B);
}

/* Am Anfang JEDER Messung aufrufen.
   Rückgabe: true = ok, false = per ABORT abgebrochen */
bool measure_prepare(const Measure_Param *p)
{
    abort_requested = false;              /* alten Abbruch vergessen */
    LED_MEASURE = 1;

    apply_settings(p);                    /* Relais (2 x 100 ms) + DAC, immer */

    if (delay_ms_abortable(SETTLE_MS))    /* 1 s, ABORT funktioniert weiter */
    {
        LED_MEASURE = 0;
        return false;
    }
    return true;
}