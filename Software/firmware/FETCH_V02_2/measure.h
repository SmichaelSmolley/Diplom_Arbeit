#ifndef MEASURE_H
#define MEASURE_H

#include <stdio.h>
#include <stm32f10x.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

#include "COMMAND_DECODE.h"

static uint16_t get_adc_average(uint32_t avg);

void transient(Measure_Param *param);
void IDVG(Measure_Param *param);
void stress(Measure_Param *param);
void wait_temp_equi(Measure_Param *param);
void MSM(Measure_Param *param);

#endif	
