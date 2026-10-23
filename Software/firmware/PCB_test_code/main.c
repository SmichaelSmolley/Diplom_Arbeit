//Blockdiagramm vom CODE herstellen
//==========<std_libs>==========
#include <stm32f10x.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>

//==========<drivers>==========
#include "SPI.h"
#include "UART.h"
#include "PINs.h"
#include "TIMER.h"
#include "dma.h"
#include "clock.h"

//==========<device_libs>==========
#include "ads8681.h"
#include "AD5689.h"

//==========<scpi_lib>==========
#include "scpi_commands.h"
#include "COMMAND_DECODE.h"

//==========<firmware>==========
#include "measure.h"

uint8_t dummy_buffer[2] = {0x00,0x00};

int main()
{
	PIN_init();
	set_up_uart1();
	spi1_init();
	
	PER_33V_PSU_EN = 1;
	ANALOG_5V_PSU_EN = 1;
	OPV_PSU_EN = 1;
	
	cal_Select_Reset = 0;
	cal_Select_set = 0;
	Range_Select_Reset = 0;
	Range_Select_set = 0;
	
	DAC_GAIN=0;
	DAC_SPI_NCS = 1;
	ADC_SPI_NCS = 1;

	uart1_set_baud(115200);
	
	{
		uint16_t i;
		for( i = 0; i < 10000; i++);
	}
	
	spi1_set_baud(5);

	 set_range_100k();
	set_GND_Relai();
	
	AD5689_set_Voltage(0,AD5689_ADDR_DAC_AB);
	
	wait_ms(1000);
	
	uart_put_string("FETCH READY\r\n");
	
	uart1_Rx_Interupt(true); //Vergessen für ersten Test der Kommunikation
	
	/* ==========================================
	 STANDARDWERTE
	 ========================================== */
	Measure_Param measure;
	
	memset(&measure, 0, sizeof(measure));

	measure.source1_voltage = 0.0f;
	measure.source1_sweep_start = 0.0f;
	measure.source1_sweep_stop = 0.0f;
	measure.source1_sweep_step = 0.0f;
	measure.source1_sweep_time = 0.0f;

	measure.source1_output = false;
	measure.source1_prot = 0.0f;
	measure.source1_range = SOURce_RANGE_25;
	measure.source1_autorange = false;


	measure.source2_voltage = 0.0f;
	measure.source2_sweep_start = 0.0f;
	measure.source2_sweep_stop = 0.0f;
	measure.source2_sweep_step = 0.0f;
	measure.source2_sweep_time = 0.0f;

	measure.source2_output = false;
	measure.source2_prot = 0.0f;
	measure.source2_range = SOURce_RANGE_25;
	measure.source2_autorange = false;


	measure.sense_current = 0.0f;
	measure.sense_range = SENSE_RANGE_100n;
	measure.sense_autorange = false;

	measure.sense_mode_gnd = false;
	measure.sense_mode_azero = false;

	measure.sense_zcorrect_aquire = 0.0f;
	measure.sense_zcorrect = false;

	measure.sense_average = 100;

	measure.sense_measurement = false;
	measure.sense_mode_idvg = false;
	measure.sense_mode_transient = false;
	measure.sense_measure_time = 10;
	measure.sense_sample_rate = 1000;
	measure.sense_points = 10000;

	measure.stress_type = STRESS_BTI;
	measure.stress_mode = STRESS_STATIC;
	measure.stress_voltage = 0.0f;
	measure.stress_drain_voltage = 0.0f;
	measure.stress_on_time = 0;
	measure.stress_off_time = 0;
	measure.stress_time = 0;
	measure.stress_cycles = 0;
	measure.stress_output = false;
	measure.stress_after_idvg = false;
	measure.stress_after_transient = false;

	measure.temp_equilibrium_wait = false;


	/* ==========================================
	   HAUPTSCHLEIFE
	   ========================================== */
	
	while(1)
	{
		if(uart_string_received())
		{
			get_Decode_Parameter(uart_get_string(), &measure);
		}
		if(measure.sense_mode_idvg == true)
		{
			IDVG(&measure);
			uart_put_string("IDVG\r\n");
		}
		if(measure.sense_mode_transient == true)
		{
			transient(&measure);
			uart_put_string("Transient\r\n");
			measure.sense_mode_transient = false;
		}
		if(measure.stress_output == true)
		{
			stress(&measure);
			uart_put_string("Stress\r\n");
		}
		if(measure.temp_equilibrium_wait == true)
		{
			wait_temp_equi(&measure);
			uart_put_string("Tempmeasure\r\n");
		}
		if(measure.sense_sample_rate == 12)
		{
			uart_put_string("SHESAIDSHEWAS12\r\n");
			return 0;
		}
	}
}//SENSE start noch in funktion schreiben