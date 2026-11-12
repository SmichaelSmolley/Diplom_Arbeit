#ifndef SEND_DATA_H
#define SEND_DATA_H

#include <stm32f10x.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#include "COMMAND_DECODE.h"

typedef enum {
    DATA_IDVG,
    DATA_TRANSIENT,
    DATA_SPOT,
    DATA_MSM_IDVG,
    DATA_MSM_TRANSIENT
} Data_TypeTyp;

typedef struct {
    Data_TypeTyp type;
    uint32_t n;            // Anzahl Punkte
    uint32_t range;        // 0 = 100 nA, 1 = 10 uA
    uint32_t avg;          // Mittelungen pro Punkt
    uint32_t dt_us;        // linearer Abstand [us], sonst 0
    uint32_t dt_min_us;    // Mindestabstand log [us], sonst 0
    uint32_t log_q24;      // (r-1) * 2^24, sonst 0
    uint32_t t_start_us;   // erster Punkt [us]
    uint32_t t_stop_us;    // Ende Messfenster [us], sonst 0
    uint32_t cycle;        // MSM-Zyklus, sonst 0
    uint32_t t_stress_ms;  // gesamte Stresszeit [ms], sonst 0
} Data_Header;

void send_measure_header(const Data_Header *hdr);
void send_measure_buffer(const Data_Header *hdr, const uint16_t *buffer);

#endif