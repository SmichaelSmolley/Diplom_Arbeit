#ifndef SPI_H
#define SPI_H

#include <stm32f10x.h>
#include <stdbool.h>

typedef enum { SPI_DEV_ADC, SPI_DEV_DAC } spi_dev;

void spi1_init();

void spi1_set_baud(uint8_t baut);

uint16_t spi1_transfer16(uint16_t tx_data);

uint8_t spi1_transfer8(uint8_t tx_data);

void spi1_mode(spi_dev SPI_device);

#endif