#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include "measure.h"
#include "ADS8866.h"
#include "AD5689.h"
#include "TIMER.h"
#include "UART.h"        
#include "PINs.h"        
#include "settings.h"
#include "SEND_DATA.h"
#include "temp.h"

#define BUF_MAX 5000u                     /* 10 kB*/
#define TEMP_WINDOW      30        /* Anzahl Messwerte im Fenster */
#define TEMP_STABLE_K    0.5f      /* erlaubte Schwankung im Fenster */
#define TEMP_MAX_MEAS    4500
static uint16_t buffer[BUF_MAX];

static uint16_t get_adc_average(uint32_t avg)
{
	uint32_t sum = 0;
	uint32_t i;

	if (avg == 0)
		avg = 1;
	for (i = 0; i < avg; i++)
		sum += ADS8866_GET_CONV();
	return (uint16_t)((sum + avg / 2u) / avg);    /* gerundet */
}

/* TODO: selbst implementieren (leere Funktionen nur, damit der Linker durchlaeuft) */
void IDVG(Measure_Param *param)
{
	Data_Header hdr;
	uint32_t n, i;
	float step, span;

	param->sense_mode_idvg = false;               

	if (measure_prepare(param))
	{
		/* Punktanzahl: |Stop-Start|/Step + 1, gerundet */
		step = param->source1_sweep_step;
		if (step < 0.0f) step = -step;
			span = param->source1_sweep_stop - param->source1_sweep_start;
		if (span < 0.0f) span = -span;
		if (step <= 0.0f)
			n = 1;
		else
			n = (uint32_t)(span / step + 0.5f) + 1u;
		if (n > BUF_MAX)
			n = BUF_MAX;
		if (param->source1_sweep_stop < param->source1_sweep_start)
			step = -step;                         /* abwärts sweepen */

		AD5689_set_Voltage(param->source2_voltage, AD5689_ADDR_DAC_B);   /* Drain fix */

		for (i = 0; i < n; i++)
		{
			if (abort_requested)
				break;
			AD5689_set_Voltage(param->source1_sweep_start + (float)i * step, AD5689_ADDR_DAC_A);
			wait_ms((int)(param->source1_sweep_time + 0.5f));             /* einschwingen */
			buffer[i] = get_adc_average(param->sense_average);
		}

		memset(&hdr, 0, sizeof(hdr));            
		hdr.type  = DATA_IDVG;
		hdr.n     = i;                            
		hdr.range = (param->sense_range == SENSE_RANGE_100n) ? 0u : 1u;
		hdr.avg   = param->sense_average;

		send_measure_header(&hdr);
		send_measure_buffer(&hdr, buffer);
	}

	AD5689_set_Voltage(0.0f, AD5689_ADDR_DAC_A);  
	AD5689_set_Voltage(0.0f, AD5689_ADDR_DAC_B);
	abort_requested = false;
	LED_MEASURE = 0;
}

void transient(Measure_Param *param)
{
	Data_Header hdr;
	uint32_t n, i, dt;
	uint16_t late = 0;
	
	param->sense_mode_transient = false;
	if(measure_prepare(param))
	{
		
		n = param->transient_points;
		if (n == 0)       n = 1;
		if (n > BUF_MAX)  n = BUF_MAX;
		
		AD5689_set_Voltage(param->source2_voltage, AD5689_ADDR_DAC_B);
		AD5689_set_Voltage(param->source1_voltage, AD5689_ADDR_DAC_A);
		wait_ms((int)param->transient_settle_ms);
		
		dt = tim3_set_period(param->transient_dt_us);
		tim3_start();                     /* t = 0 */
		
		for(i = 0; i < n; i++)
		{
			if (i > 0)
			{
				/* UIF schon gesetzt -> letzte Messung dauerte länger als dt */
				if(TIM3->SR & TIM_SR_UIF)
					late++;
				if(tim3_wait())          /* ABORT */
					break;
			}
			buffer[i] = get_adc_average(param->sense_average);
		}
		tim3_stop();
		
		memset(&hdr, 0, sizeof(hdr));    /* nicht benutzte Felder = 0 */
		hdr.type       = DATA_TRANSIENT;
		hdr.n          = i;               /* bei ABORT weniger */
		hdr.range      = (param->sense_range == SENSE_RANGE_100n) ? 0u : 1u;
		hdr.avg        = param->sense_average;
		hdr.dt_us      = dt;              /* echter Abstand */
		hdr.t_start_us = 0;

		send_measure_header(&hdr);
		send_measure_buffer(&hdr, buffer);

		if (late > 0)                     /* Hinweis erscheint im Python-Log */
		{
			uart_put_string("WARN: dt zu kurz, Punkte zu spaet: ");
			uart_put_u32(late);
			uart_put_string("\r\n");
		}
	}
	
	AD5689_set_Voltage(0.0f, AD5689_ADDR_DAC_A);   /* DUT spannungsfrei */
	AD5689_set_Voltage(0.0f, AD5689_ADDR_DAC_B);
	abort_requested = false;
	LED_MEASURE = 0;
}

static bool Temp_equilibrium(float* buffer, int count)
{
	float max = buffer[0];
	float min = buffer[0];
	int i = 0;
	
	if(count < TEMP_WINDOW){return false;}
	
	for(i = 0; i < TEMP_WINDOW; i++)
	{
		if(buffer[i] > max){max = buffer[i];}
		if(buffer[i] < min){min = buffer[i];}
	}
	return ((max - min) <= TEMP_STABLE_K);
}

void wait_temp_equi(Measure_Param *param)
{
	param->temp_equilibrium_wait = false;
	abort_requested = false;  
	
	float buffer[30] = {0};
	char text[32];
	uint16_t count = 0;
	float t;
	int k;
	int i = 0;

	const char *result = "TIMEOUT";
	
	for(k = 0; k < TEMP_MAX_MEAS; k++)
	{
		t = get_temp(OW_ANALOG);
		if (t > -100.0f)                          /* gültig (Fehlerwert ist -1000) */
		{
			buffer[i] = t;
			i = (i + 1) % TEMP_WINDOW;
			if (count < TEMP_WINDOW)
				count++;
			
			sprintf(text, "#TEMP A=%.2f\r\n", (double)t);    /* Zwischenstand fürs Log */
			uart_put_string(text);
			
		}
		if (Temp_equilibrium(buffer, count))
		{
			result = "STABLE";
			break;
		}
	}
	
	if (result == NULL)
	uart_put_string("#ABORTED\r\n");
	else
	{
		sprintf(text, "#TEMP %s A=%.2f\r\n", result, (double)t);
		uart_put_string(text);
	}

	abort_requested = false;
	LED_MEASURE = 0;
}

static bool stress_wait_ms(uint32_t ms)
{
	uint32_t k;
	bool aborted = false;

	tim3_set_period(1000u);           /* 1 ms */
	tim3_start();
	for (k = 0; k < ms; k++)
	{
		if (tim3_wait())
		{
			aborted = true;
			break;
		}
	}
	tim3_stop();
	return aborted;
}

static void stress_on(const Measure_Param *p)
{
	float vd = (p->stress_type == STRESS_HCD) ? p->stress_drain_voltage : 0.0f;

	AD5689_set_Voltage(p->stress_voltage, AD5689_ADDR_DAC_A);   /* Gate  */
	AD5689_set_Voltage(vd,                AD5689_ADDR_DAC_B);   /* Drain */
}

void stress(Measure_Param *param)
{
	uint32_t k;
	bool aborted = false;
	param->stress_output = false;
	
	if(measure_prepare(param))
	{
		if(param->stress_mode == STRESS_STATIC)
		{
			stress_on(param);
			aborted = stress_wait_ms(param->stress_time);
		}
		else //Dynamisch
		{
			for(k = 0; k < param->stress_cycles && !aborted; k++)
			{
				stress_on(param);
				aborted = stress_wait_ms(param->stress_on_time);
				AD5689_set_Voltage(0.0f, AD5689_ADDR_DAC_AB);
				if(!aborted)
				{
					aborted = stress_wait_ms(param->stress_off_time);
				}
			}
		}
		AD5689_set_Voltage(0.0f, AD5689_ADDR_DAC_AB);
		
		if(!aborted && param->stress_after_idvg)
		{
			IDVG(param);
		}
		if(!aborted && param->stress_after_transient)
		{
			transient(param);
		}
	}
	
	AD5689_set_Voltage(0.0f, AD5689_ADDR_DAC_AB);
	abort_requested = false;
	LED_MEASURE = 0;
}

void MSM(Measure_Param *param)
{
	(void)param;
}
