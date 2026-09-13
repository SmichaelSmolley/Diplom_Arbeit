//==========<std_libs>==========
#include <stm32f10x.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>

//==========<drivers>==========
#include "SPI.h"
#include "UART.h"
#include "PINs.h"
//==========<device_libs>==========
#include "ads8681.h"
#include "AD5689.h"

int main()
{
	PIN_init();
	set_up_uart1();
	spi1_init();
	
	PER_33V_PSU_EN = 1;
	ANALOG_5V_PSU_EN = 1;
	
	cal_Select_Reset = 0;
	cal_Select_set = 0;
	Range_Select_Reset = 0;
	Range_Select_set = 0;
	uint16_t i;
	DAC_SPI_NCS = 1;
	ADC_SPI_NCS = 1;
	
	for( i = 0; i < 10000; i++){}
	spi1_set_baud(7);
	
	DAC_GAIN=0;
	
	// Nutzung von uint16_t anstelle von uint32_t
	//uint16_t data = (uint16_t)((ADS8681_RANGE_SEL_UP_1_25_VREF & ADS8681_RANGE_SEL_MASK) << ADS8681_RANGE_SEL_SHIFT);
		
	// Befehl und Adresse direkt in einen uint16_t Wert kombinieren (statt uint8_t bytes[2])
	//uint16_t cmd = (uint16_t)(((ADS868X_SPI_COMMAND_WRITE_FULL << 1) | ((ADS868X_REGISTER_ADDRESS_RANGE_SEL >> 8) & 0x01)) << 8) 
	//             | (ADS868X_REGISTER_ADDRESS_RANGE_SEL & 0xFF);
		
	AD5689_init();
	//AD5689_set_Voltage(3, AD5689_ADDR_DAC_AB);
	
	AD5689_send_command(0x3, AD5689_ADDR_DAC_AB, 0xFFFF);
	
	/*
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