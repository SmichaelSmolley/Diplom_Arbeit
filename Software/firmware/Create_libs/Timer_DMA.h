#include <stm32f10x.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

void Tim2_setup(uint16_t int_frequ)
{
	RCC->APB1ENR |= RCC_APB1ENR_TIM2EN; // TIM2 CLK EN
	TIM2->SMCR |= 0x0000; // Slave mode disabled
	TIM2->CR1 |= 0x0000; // TIM4 Upcounter
	TIM2->CR1 |= 0x0080; // ARPE Bit set Autoreload register
	
	TIM2->PSC = 8 - 1;     // 8 MHz / 8 = 1 MHz
	
	if(int_frequ)
	{
		TIM2->ARR = (1000000UL / (int_frequ)) - 1;
	}
	else{TIM2->ARR = 9;}
	
	TIM2->CNT = 0; // timer zurück auf 0 setzten
	TIM2->SR = 0; // löscht pending bits

	TIM2->DIER |= TIM_DIER_UIE; // interrupt aktivieren

	NVIC_init(TIM2_IRQn, 1); // interrupt priosetzten im nvic

	TIM2->CR1 |= TIM_CR1_CEN; // Timer aktivieren
}

void Tim2_enable()
{

}
	
void Tim2_diable()
{

}

void DMA_rx_setup_SPI1_to_Mem(uint16_t* buffer, uint32_t numm_of_words)
{
	RCC->AHBENR |= RCC_AHBENR_DMA1EN; //clock für dma
	
	DMA1_Channel2->CPAR = (uint32_t)&SPI1->DR; //Peripheral address DR-Register SPI1
	
	DMA1_Channel2->CMAR = (uint32_t)buffer; // Memory address
	
	DMA1_Channel2->CNDTR = numm_of_words;
	
	DMA1_Channel2->CCR = DMA_CCR1_MSIZE_0 // Memory 16 bit
		| DMA_CCR1_PSIZE_0 // Peripheral 16 bit
		| DMA_CCR1_PL_1 // Priority high
		| DMA_CCR1_TCIE; // interrupt after end
	
	DMA1_Channel2->CCR |= DMA_CCR1_EN;// DMA enable
}

void DMA_tx_setup_SPI1_to_Mem(uint16_t* buffer, uint32_t numm_of_words)
{
	RCC->AHBENR |= RCC_AHBENR_DMA1EN; //clock für dma
	
	DMA1_Channel2->CPAR = (uint32_t)&SPI1->DR; //Peripheral address DR-Register SPI1
	
	DMA1_Channel2->CMAR = (uint32_t)buffer; // Memory address
	
	DMA1_Channel2->CNDTR = numm_of_words;
	
	DMA1_Channel2->CCR = DMA_CCR1_MSIZE_0 // Memory 16 bit
		| DMA_CCR1_PSIZE_0 // Peripheral 16 bit
		| DMA_CCR1_PL_1 // Priority high
		| DMA_CCR1_EN// DMA enable
		| DMA_CCR1_TCIE; // interrupt after end
	
}

void DMA_tx_disable()
{
	DMA1_Channel2->CCR = ~DMA_CCR1_EN; // DMA enable
}

void DMA_tx_enable()
{
	DMA1_Channel2->CCR = DMA_CCR1_EN; // DMA enable
}