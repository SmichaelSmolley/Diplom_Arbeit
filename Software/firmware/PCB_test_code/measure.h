#ifndef MEASURE_H
#define MEASURE_H

#include <stdio.h>
#include <stm32f10x.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

#include "COMMAND_DECODE.h"

void start_measure(Measure_Param *param);
void transient_measure(Measure_Param *param);
void IDVG_measure(Measure_Param *param);

#endif	
