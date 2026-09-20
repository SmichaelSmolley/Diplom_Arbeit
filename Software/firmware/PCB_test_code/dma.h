#ifndef DMA_H
#define DMA_H

#include <stm32f10x.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>

void spi1_rx_dma_init(void);
	
void spi1_rx_dma(uint8_t* buffer, uint16_t num_rx);

void spi1_tx_dma_init();

void spi1_tx_dma(uint8_t* buffer, uint16_t num_tx);

#endif