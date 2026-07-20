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

	
	
	DAC_SPI_NCS = 1;
	
	spi1_set_baud(32);
	
	char buffer[128];
	
	sprintf(buffer, "hallo, DAUMEN, Defektanalyse- und Mess-Einheit mit Nutzerschnittstelle\n\r");
	uart_put_string(buffer);
		
	
	while(1){
	ADC_SPI_NCS = 0;
	uint16_t raw = spi1_transfer16(0x00);
	double volt = ADS8681_get_VOLT(raw);
	ADC_SPI_NCS = 1;
  sprintf(buffer, "volt = %.6f\r\n", volt);
	}
}