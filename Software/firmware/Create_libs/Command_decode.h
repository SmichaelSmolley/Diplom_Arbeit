#include <stm32f10x.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#include "SCPI_Defines.h"

typedef struct
{
    float drain_voltage;
    float gate_voltage;

    float drain_sweep_start;
    float drain_sweep_stop;
    float drain_sweep_step;

    float gate_sweep_start;
    float gate_sweep_stop;
    float gate_sweep_step;

    float current_limit;

    bool drain_output;
    bool gate_output;

    bool autorange;

    uint32_t averaging;

} messurment_param_t;

