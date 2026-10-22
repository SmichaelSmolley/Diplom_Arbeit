#ifndef MEASURE_H
#define MEASURE_H

#include <stdio.h>
#include <stm32f10x.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

#include "COMMAND_DECODE.h"

#define std_room_temp 25

void start_measure(Measure_Param *param);
void transient(Measure_Param *param);
void IDVG(Measure_Param *param);
void stress(Measure_Param *param);
void wait_temp_equi(Measure_Param *param);

#endif	
