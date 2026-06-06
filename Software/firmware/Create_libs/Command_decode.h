#include <stm32f10x.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define drain_voltage "SOURce1"
#define gate_voltage "SOURce2"
#define TIA "SENSe1"

#define voltage "VOLTage"
#define current "CURRent"

#define messure_range "RANGe"

#define range_mode_Auto_on "AUTO ON"
#define range_mode_Auto_off "AUTO OFF"

#define start_value "START"
#define step_size "STOP"
#define end_value "STEP"

#define mode_sweep "MODE SWEep"
#define mode_GND "MODE GND"
#define mode_Auto_zero "AZEro"

#define AZEro_state_on "STATe ON"
#define AZEro_state_off "STATe OFF"

#define command_init "INITiate"
#define command_reset "*CLS"

