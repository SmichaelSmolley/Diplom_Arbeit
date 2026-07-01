#ifndef Timer_DMA_H
#define Timer_DMA_H

#include <stm32f10x.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

void Tim2_setup(uint16_t int_frequ);
void Tim2_enable();
void Tim2_diable();
void DMA_rx_setup_SPI1_to_Mem(uint16_t* buffer, uint32_t numm_of_words);
void DMA_rx_disable();
void DMA_rx_enable();
void DMA_tx_setup_SPI1_to_Mem(uint16_t* buffer, uint32_t numm_of_words);
void DMA_tx_disable();
void DMA_tx_enable();

#endif
