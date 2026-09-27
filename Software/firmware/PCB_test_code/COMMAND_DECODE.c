#include <stm32f10x.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>

#include "SCPI_COMMANDS.h"
#include "COMMAND_DECODE.h"

void get_Decode_Parameter(char *command, Measure_Param *param)
{
	float value;

	/* ================= SOURCE 1 ================= */

	if (strncmp(command, "SOURce1_VOLTage= ", 17) == 0)
	{
		value = (float)atof(command + 17);
		param->source1_voltage = value;
	}

	else if (strncmp(command, "SOURce1_Sweep_Start= ", 21) == 0)
	{
		value = (float)atof(command + 21);
		param->source1_sweep_start = value;
	}

	else if (strncmp(command, "SOURce1_Sweep_Stop= ", 20) == 0)
	{
		value = (float)atof(command + 20);
		param->source1_sweep_stop = value;
	}

	else if (strncmp(command, "SOURce1_Sweep_Step= ", 20) == 0)
	{
		value = (float)atof(command + 20);
		param->source1_sweep_step = value;
	}

	else if (strncmp(command, "SOURce1_Sweep_TIme= ", 20) == 0)
	{
		value = (float)atof(command + 20);
		param->source1_sweep_time = value;
	}

	else if (strncmp(command, "SOURce1_PROT= ", 15) == 0)
	{
		value = (float)atof(command + 15);
		param->source1_prot = value;
	}

	else if (strncmp(command, "SOURce1_RANGE= ", 15) == 0)
	{
		value = (float)atof(command + 15);

		if (value == 25)
			param->source1_range = SOURce_RANGE_25;

		else if (value == 50)
			param->source1_range = SOURce_RANGE_50;
	}

	else if (strncmp(command, "SOURce1_OUTput= ", 16) == 0)
	{
		if (strcmp(command + 16, "ON") == 0)
			param->source1_output = true;

		else if (strcmp(command + 16, "OFF") == 0)
			param->source1_output = false;
	}

	else if (strncmp(command, "SOURce1_AUTOrange= ", 19) == 0)
	{
		if (strcmp(command + 19, "ON") == 0)
			param->source1_autorange = true;

		else if (strcmp(command + 19, "OFF") == 0)
			param->source1_autorange = false;
	}


	/* ================= SOURCE 2 ================= */

	else if (strncmp(command, "SOURce2_VOLTage= ", 17) == 0)
	{
		value = (float)atof(command + 17);
		param->source2_voltage = value;
	}

	else if (strncmp(command, "SOURce2_Sweep_Start= ", 21) == 0)
	{
		value = (float)atof(command + 21);
		param->source2_sweep_start = value;
	}

	else if (strncmp(command, "SOURce2_Sweep_Stop= ", 20) == 0)
	{
		value = (float)atof(command + 20);
		param->source2_sweep_stop = value;
	}

	else if (strncmp(command, "SOURce2_Sweep_Step= ", 20) == 0)
	{
		value = (float)atof(command + 20);
		param->source2_sweep_step = value;
	}

	else if (strncmp(command, "SOURce2_Sweep_TIme= ", 20) == 0)
	{
		value = (float)atof(command + 20);
		param->source2_sweep_time = value;
	}

	else if (strncmp(command, "SOURce2_PROT= ", 15) == 0)
	{
		value = (float)atof(command + 15);
		param->source2_prot = value;
	}

	else if (strncmp(command, "SOURce2_RANGE= ", 15) == 0)
	{
		value = (float)atof(command + 15);

		if (value == 25)
			param->source2_range = SOURce_RANGE_25;

		else if (value == 50)
			param->source2_range = SOURce_RANGE_50;
	}

	else if (strncmp(command, "SOURce2_OUTput= ", 16) == 0)
	{
		if (strcmp(command + 16, "ON") == 0)
			param->source2_output = true;

		else if (strcmp(command + 16, "OFF") == 0)
			param->source2_output = false;
	}

	else if (strncmp(command, "SOURce2_AUTOrange= ", 19) == 0)
	{
		if (strcmp(command + 19, "ON") == 0)
			param->source2_autorange = true;

		else if (strcmp(command + 19, "OFF") == 0)
			param->source2_autorange = false;
	}


	/* ================= SENSE ================= */

	else if (strncmp(command, "SENSE_CURRENT= ", 15) == 0)
	{
		value = (float)atof(command + 15);
		param->sense_current = value;
	}

	else if (strncmp(command, "SENSE_RANGE= ", 13) == 0)
	{
		value = (float)atof(command + 13);

		if (value == 0)
			param->sense_range = SENSE_RANGE_100n;

		else if (value == 1)
			param->sense_range = SENSE_RANGE_10u;
	}

	else if (strncmp(command, "SENSE_AUTORANGE= ", 17) == 0)
	{
		if (strcmp(command + 17, "ON") == 0)
			param->sense_autorange = true;

		else if (strcmp(command + 17, "OFF") == 0)
			param->sense_autorange = false;
	}

	else if (strncmp(command, "SENSE_MODE_GND= ", 16) == 0)
	{
		if (strcmp(command + 16, "ON") == 0)
			param->sense_mode_gnd = true;

		else if (strcmp(command + 16, "OFF") == 0)
			param->sense_mode_gnd = false;
	}

	else if (strncmp(command, "SENSE_MODE_AZERO= ", 18) == 0)
	{
		if (strcmp(command + 18, "ON") == 0)
			param->sense_mode_azero = true;

		else if (strcmp(command + 18, "OFF") == 0)
			param->sense_mode_azero = false;
	}

	else if (strncmp(command, "SENSE_MODE_ZCORRECT_AQUIRE= ", 28) == 0)
	{
		value = (float)atof(command + 28);
		param->sense_zcorrect_aquire = value;
	}

	else if (strncmp(command, "SENSE_MODE_AVERAGE= ", 20) == 0)
	{
		param->sense_average = (uint32_t)strtoul(command + 20, NULL, 10);
	}

	else if (strncmp(command, "SENSE_MODE_MEASUREMENT= ", 24) == 0)
	{
		if (strcmp(command + 24, "START") == 0)
			param->sense_measurement = true;

		else if (strcmp(command + 24, "STOP") == 0)
			param->sense_measurement = false;
	}
}