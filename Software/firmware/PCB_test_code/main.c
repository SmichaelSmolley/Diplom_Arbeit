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
	
	spi1_set_baud(7);
	
	uart_put_string("UART TEST\r\n");

	set_range_10meg();
	reset_GND_Relai();
	AD5689_set_Voltage(0,AD5689_ADDR_DAC_AB);
	
	wait_ms(1000);
	
	static double buffer[1000];
	char uart_buffer[64];
	AD5689_set_Voltage(1.0, AD5689_ADDR_DAC_A);
	wait_ms(2000);
	LED_RED = 1;
	int i = 0;

	for(i = 0; i < 100; i++)
	{
		int j;

		for(j = 0; j < 10; j++)
		{
			ADC_SPI_NCS = 0;

			uint16_t raw = spi1_transfer16(0x0000);
			double volt = ADS8681_get_VOLT(raw);

			buffer[(i * 10) + j] = volt;

			ADC_SPI_NCS = 1;
		}

		DAC_SPI_NCS = 0;

		AD5689_set_Voltage(
			(i*0.02),
			AD5689_ADDR_DAC_B
		);
		wait_ms(100);
		DAC_SPI_NCS = 1;
		
	}
	


for(i = 0; i < 1000; i++) 
	{
		sprintf( 
		uart_buffer, 
		"%i,%.9f\r\n", 
		i, 
		buffer[i] 
		);
		uart_put_string(uart_buffer);
	}


	while(1)
	{
	}
	
	
	/*
	spi1_set_baud(2);
	
	uart1_set_baud(9600);
		
	
	init_tim2(1,79); //uint8_t clk_div, uint16_t period_ticks
	
	spi1_rx_dma_init();
	
	uint8_t Adc_data_buffer [1000];
	
	spi1_rx_dma(Adc_data_buffer,1000);
	
	spi1_tx_dma_init();
	
	tim2_enable();
*/
/*	
	
	// Nutzung von uint16_t anstelle von uint32_t
	//uint16_t data = (uint16_t)((ADS8681_RANGE_SEL_UP_1_25_VREF & ADS8681_RANGE_SEL_MASK) << ADS8681_RANGE_SEL_SHIFT);
		
	// Befehl und Adresse direkt in einen uint16_t Wert kombinieren (statt uint8_t bytes[2])
	//uint16_t cmd = (uint16_t)(((ADS868X_SPI_COMMAND_WRITE_FULL << 1) | ((ADS868X_REGISTER_ADDRESS_RANGE_SEL >> 8) & 0x01)) << 8) 
	//             | (ADS868X_REGISTER_ADDRESS_RANGE_SEL & 0xFF);
	
	
	//AD5689_init();
	//AD5689_set_Voltage(3, AD5689_ADDR_DAC_AB);
	
	//AD5689_send_command(AD5689_CMD_WRITE_DAC, AD5689_ADDR_DAC_AB, 0xFFFF);


	reset_GND_Relai();
	
	//set_range_100k();
	wait_ms(1000);
	//set_range_10meg();
	
	
	//TO-DO: test dac
	
	
	spi1_transfer16(0x0000);// das kein befehl mer in wait ist;
	while(1)
	{
		uint16_t raw = spi1_transfer16(0x0000);
		uart_put_char(raw >> 8);
		uart_put_char(raw & 0x00ff);
	}
	
	uint8_t ADC_SPI1_BUFF [100];
	uint8_t ADC_SPI1_DUMMY = 0x00;
	
	spi1_tx_dma_init(&ADC_SPI1_DUMMY, 100);
	spi1_rx_dma_init(ADC_SPI1_BUFF, 100);
	
	uint8_t i = 0;
	for(i = 0; i < 100; i++)
	{
		uart_put_char(ADC_SPI1_BUFF[i]);
	}
	
	uart_put_string("EOS");
	
	
	char buffer[64];
	while(1){
	ADC_SPI_NCS = 0;
	uint16_t raw = spi1_transfer16(0x0000);
	double volt = ADS8681_get_VOLT(raw);
	ADC_SPI_NCS = 1;
	sprintf(buffer, "%.3f\r\n", volt);
	uart_put_string(buffer);
	}
	*/
	
}