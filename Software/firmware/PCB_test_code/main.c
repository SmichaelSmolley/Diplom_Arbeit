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

	uart1_set_baud(9600);
	
	{
		uint16_t i;
		for( i = 0; i < 10000; i++);
	}
	
	spi1_set_baud(2);

	set_range_100k();
	reset_GND_Relai();
	
	AD5689_set_Voltage(0,AD5689_ADDR_DAC_AB);
	
	wait_ms(1000);
	
	uart_put_string("SAFDAT READY\r\n");
	
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


	/* ==========================================
	   HAUPTSCHLEIFE
	   ========================================== */
	
	while(1)
	{
		if(uart_string_received())
		{
			get_Decode_Parameter(uart_get_string(), &measure);
		}
		if(measure.sense_measurement == true)
		{
			//die messung starten;
		}
	}
}