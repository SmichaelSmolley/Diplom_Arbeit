#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include "AD5689.h"
#include "SPI.h"
#include "PINs.h"

uint32_t AD5689_SEND_COMMAND_BLOCKING (	
	enum ad5689_command command,
	enum ad5689_address reg,
	uint16_t data)
{
	spi1_set_8bit();
	uint8_t tx_data[3];
	tx_data[0] = (uint8_t)(command << 4) | (reg);
	tx_data[1] = (uint8_t)(data >> 8);
	tx_data[2] = (uint8_t)(data);
	
	DAC_SPI_NCS = 0;
	
	spi1_transfer8(tx_data[0]);
	spi1_transfer8(tx_data[1]);
  spi1_transfer8(tx_data[2]);
	
	DAC_SPI_NCS = 1;
	
	uint32_t rx_data = 0;
	
	DAC_SPI_NCS = 0;
	
	rx_data = AD5689_transfer_frame(0x0000);
	
	DAC_SPI_NCS = 1;
	
	spi1_set_16bit();
	
	return rx_data;
}

uint32_t AD5689_transfer_frame(uint32_t tx_frame)
{
	uint8_t tx_data[3];
	tx_data[0] = (uint8_t)(tx_frame >> 16);
	tx_data[1] = (uint8_t)(tx_frame >> 8);
	tx_data[2] = (uint8_t)(tx_frame);
	
	uint8_t rx_data[3];
	rx_data[0] = spi1_transfer8(tx_data[0]);
	rx_data[1] = spi1_transfer8(tx_data[1]);
	rx_data[2] = spi1_transfer8(tx_data[2]);
	
	return (uint32_t)(rx_data[0] << 16) | (rx_data[1] << 8) | (rx_data[2] << 0);
}