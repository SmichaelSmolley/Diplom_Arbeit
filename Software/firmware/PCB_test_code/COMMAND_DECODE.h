#ifndef COMMAND_DEODE_H
#define COMMAND_DEODE_H

#include <stm32f10x.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#include "SCPI_COMMANDS.h"

typedef struct
{
    /* SOURCE 1 */
    float source1_voltage;
    float source1_sweep_start;
    float source1_sweep_stop;
    float source1_sweep_step;
    float source1_sweep_time;
    bool  source1_output;
    float source1_prot;
    SOURce_RangeTyp source1_range;
    bool  source1_autorange;

    /* SOURCE 2 */
    float source2_voltage;
    float source2_sweep_start;
    float source2_sweep_stop;
    float source2_sweep_step;
    float source2_sweep_time;
    bool  source2_output;
    float source2_prot;
    SOURce_RangeTyp source2_range;
    bool  source2_autorange;

    /* SENSE */
    float sense_current;
    SENSE_RangeTyp sense_range;
    bool sense_autorange;

    bool sense_mode_gnd;
    bool sense_mode_azero;

    float sense_zcorrect_aquire;
    bool  sense_zcorrect;

    uint32_t sense_average;

    bool sense_measurement;

    bool sense_mode_idvg;         // true = Messung ist eine IDVG
    bool sense_mode_transient;    // true = Messung ist ein Transient


    /* STRESS */
    STRESS_TypeTyp stress_type;       // BTI oder HCD
    STRESS_ModeTyp stress_mode;       // STATIC oder DYNAMIC
    float    stress_voltage;          // Gate-Stressspannung [V]
    float    stress_drain_voltage;    // Drain-Stressspannung [V], nur HCD
    uint32_t stress_on_time;          // [ms] Stress pro Puls (DYNAMIC)
    uint32_t stress_off_time;         // [ms] Pause pro Puls (DYNAMIC)
    uint32_t stress_time;             // [ms] Gesamtdauer (STATIC)
    uint32_t stress_cycles;           // Anzahl Pulse (DYNAMIC)
    bool     stress_output;           // Stress ausfuehren ja/nein
    bool     stress_after_idvg;       // nach dem Stressen IDVG starten
    bool     stress_after_transient;  // nach dem Stressen Transienten starten

    /* TEMP */
    bool     temp_equilibrium_wait;   // true = vor der Messung auf thermisches Gleichgewicht warten

} Measure_Param;

void get_Decode_Parameter(char* command, Measure_Param* Parameter);

#endif