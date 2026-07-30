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
	OPV_PSU_EN = 1;
	
	cal_Select_Reset = 0;
	cal_Select_set = 0;
	Range_Select_Reset = 0;
	Range_Select_set = 0;

	DAC_SPI_NCS = 1;
	ADC_SPI_NCS = 1;
	spi1_set_baud(6);
	
	char buffer[128];
	
	sprintf(buffer, "hallo, DAUMEN, Defektanalyse- und Mess-Einheit mit Nutzerschnittstelle\n\r");
	uart_put_string(buffer);
	
	//==DAC test==
	
	AD5689_SEND_COMMAND_BLOCKING(AD5689_COMMAND_POWER_DO_UP_DAC, 0x00, 
	((AD5689_OP_MODE_NORMAL<<6) | (0xF << 2) | (AD5689_OP_MODE_NORMAL))); //status normal
	wait_ms(100);
	AD5689_SEND_COMMAND_BLOCKING(AD5689_COMMAND_WRITE_IN_REGISTER, AD5689_ADRESS_DAC_AB, 0x8000); //set voltage midrange = 1,25V
	
/*	testcode range select funktioniert nicht	
	// Nutzung von uint16_t anstelle von uint32_t
	uint16_t data = (uint16_t)((ADS8681_RANGE_SEL_UP_1_25_VREF & ADS8681_RANGE_SEL_MASK) << ADS8681_RANGE_SEL_SHIFT);
		
	// Befehl und Adresse direkt in einen uint16_t Wert kombinieren (statt uint8_t bytes[2])
	uint16_t cmd = (uint16_t)(((ADS868X_SPI_COMMAND_SET_HWORD << 1) | ((ADS868X_REGISTER_ADDRESS_RANGE_SEL >> 8) & 0x01)) << 8) 
	             | (ADS868X_REGISTER_ADDRESS_RANGE_SEL & 0xFF);
	
	uint16_t ret = 0;
	
	ADC_SPI_NCS = 0;
	
	// Übertragung der 16-Bit Werte
	ret = spi1_transfer16(cmd);
	ret = spi1_transfer16(data);
	
	ADC_SPI_NCS = 1;

	ADC_SPI_NCS = 0;

	ret = spi1_transfer16(ADS868X_SPI_COMMAND_NOP);
	ret = spi1_transfer16(ADS868X_SPI_COMMAND_NOP);
	
	ADC_SPI_NCS = 1;
	
	ADC_SPI_NCS = 0;

	ret = spi1_transfer16(ADS868X_SPI_COMMAND_NOP);
	ret = spi1_transfer16(ADS868X_SPI_COMMAND_NOP);
	
	ADC_SPI_NCS = 1;
	
	ADC_SPI_NCS = 0;

	ret = spi1_transfer16(ADS868X_SPI_COMMAND_NOP);
	ret = spi1_transfer16(ADS868X_SPI_COMMAND_NOP);
	*/
	
	//set_range_100k();
	
	
/*	ADC_SPI_NCS = 1;
	
	while(1){
	  ADC_SPI_NCS = 0;
	  uint16_t raw = spi1_transfer16(0x00);
	  double volt = ADS8681_get_VOLT(raw);
	  ADC_SPI_NCS = 1;
	  sprintf(buffer, "volt = %.6f\r\n", volt);
		uart_put_string(buffer);
	}
*/	
}