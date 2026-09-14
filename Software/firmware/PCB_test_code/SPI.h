#ifndef SPI_H
#define SPI_H

#include <stm32f10x.h>
#include <stdbool.h>

void spi1_init();

void spi1_set_baud(uint8_t baut);

void spi1_rx_dma(bool setting);

uint8_t spi1_transfer8(uint8_t tx_data);

uint16_t spi1_transfer16(uint16_t tx_data);

void spi1_tx_dma_init(uint8_t* buffer, uint16_t buffer_size);
void spi1_rx_dma_init(uint8_t* buffer, uint16_t buffer_size);

#endif