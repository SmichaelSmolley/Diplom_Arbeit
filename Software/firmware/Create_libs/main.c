#include <stm32f10x.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#include "Pin_def_lib.h"
#include "UART1_com.h"
#include "SPI.h"
#include "ads8681_lib.h"

int main()
{
	set_up_uart1();
	spi1_init();
	
	ADC_SPI_NCS = 0;
	
	while(1)
	{
		uint32_t adc_wert = ADS8681_send_Command_blocking(ADS868X_SPI_COMMAND_NOP, ADS868X_REGISTER_ADDRESS_DEVICE_ID, 0x00);
		
		char temp_buffer[20];
	
		sprintf(temp_buffer, "adc_wert:%u\r\n", adc_wert);
	
		uart_put_string(temp_buffer);
	}
}