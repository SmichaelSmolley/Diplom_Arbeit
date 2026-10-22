#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include "measure.h"
#include "ads8681.h"
#include "AD5689.h"
#include "TIMER.h"
#include "dma.h"
#include "temp.h"

void start_measure(Measure_Param *param)
{
	if(param->source2_sweep_step != 0 || param->source1_sweep_step != 0)
	{
		IDVG(param);
	}
	if(param->source2_sweep_step == 0 || param->source1_sweep_step == 0)
	{
		transient(param);
	}
}

/* TODO: selbst implementieren (leere Funktionen nur, damit der Linker durchlaeuft) */
void IDVG(Measure_Param *param)
{
	(void)param;
}

void transient(Measure_Param *param)
{
	(void)param;
}

void wait_temp_equi(Measure_Param *param)
{

}

void stress(Measure_Param *param)
{
	(void)param;
}