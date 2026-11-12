#ifndef SETTINGS_H
#define SETTINGS_H

#include <stdio.h>
#include <stm32f10x.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

#include "COMMAND_DECODE.h"
#include "relai.h"

void apply_settings(const Measure_Param *p);
bool measure_prepare(const Measure_Param *p);

#endif	
