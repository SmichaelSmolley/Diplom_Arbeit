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


enum ads868x_register_address
{
    ADS868X_REGISTER_ADDRESS_DEVICE_ID      = 0x00,
    ADS868X_REGISTER_ADDRESS_RST_PWRCTL     = 0x04,
    ADS868X_REGISTER_ADDRESS_SDI_CTL        = 0x08,
    ADS868X_REGISTER_ADDRESS_SDO_CTL        = 0x0C,
    ADS868X_REGISTER_ADDRESS_DATAOUT_CTL    = 0x10,
    ADS868X_REGISTER_ADDRESS_RANGE_SEL      = 0x14,
    ADS868X_REGISTER_ADDRESS_ALARM          = 0x20,
    ADS868X_REGISTER_ADDRESS_ALARM_H_TH     = 0x24,
    ADS868X_REGISTER_ADDRESS_ALARM_L_TH     = 0x28
};

enum ads868x_spi_command
{
    ADS868X_SPI_COMMAND_NOP                 = 0b0000000,
    ADS868X_SPI_COMMAND_CLEAR_HWORD         = 0b1100000,
    ADS868X_SPI_COMMAND_READ_HWORD          = 0b1100100,
    ADS868X_SPI_COMMAND_READ                = 0b0100100,
    ADS868X_SPI_COMMAND_WRITE_FULL          = 0b1101000,
    ADS868X_SPI_COMMAND_WRITE_MS            = 0b1101001,
    ADS868X_SPI_COMMAND_WRITE_LS            = 0b1101010,
    ADS868X_SPI_COMMAND_SET_HWORD           = 0b1101100
};


int main()
{
	PIN_init();
	set_up_uart1();
	spi1_init();
	spi1_set_baud(16);
	
	char buffer[128];
	
	
	sprintf(buffer, "hallo, DAUMEN, Defektanalyse- und Mess-Einheit mit Nutzerschnittstelle\n\r");
	
	uart_put_string(buffer);
	
	ADC_SPI_NCS = 0;
	spi1_transfer16((ADS868X_SPI_COMMAND_READ << 9) | (ADS868X_REGISTER_ADDRESS_DEVICE_ID));
	uint16_t spi_test = spi1_transfer16(0x00);
	ADC_SPI_NCS = 1;
	
	if(spi_test == 


0){LED_GREEN = 1;}
}