#ifndef SPI_H
#define SPI_H

#include <stm32f10x.h>
#include <stdbool.h>

void spi1_init();

void spi1_set_baud(uint8_t baut);

void spi1_rx_dma(bool setting);

uint16_t spi1_transfer16(uint16_t tx_data);

uint8_t spi1_transfer8(uint8_t tx_data);

void spi1_set_8bit(void);

void spi1_set_16bit(void);

#endif