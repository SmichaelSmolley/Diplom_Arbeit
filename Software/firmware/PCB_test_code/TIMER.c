#include "TIMER.h"
#include <stdint.h>
#include <stm32f10x.h>

uint8_t spi_dummy = 0x00;

void TIM2_IRQHandler(void)
{
    // Update Event?
    if (TIM2->SR & TIM_SR_UIF)
    {
        // Update Flag löschen
        TIM2->SR &= ~TIM_SR_UIF;

        // 0x00 über SPI1 senden
        spi1_tx_dma(&spi_dummy, 2);
    }
}

void wait_ms(int ms)
{
	int j;
	for(j = 0; j < 7987*ms; j++){}
} 

void init_tim2(uint8_t clk_div, uint16_t period_ticks)
{
	// Timer 2 Clock einschalten
	RCC->APB1ENR |= RCC_APB1ENR_TIM2EN;

	// Timer stoppen
	TIM2->CR1 &= ~TIM_CR1_CEN;

	// Counter zurücksetzen
	TIM2->CNT = 0;

	// Clock Division CKD[1:0]
	TIM2->CR1 &= ~(3 << 8);
	TIM2->CR1 |= ((clk_div & 0x03) << 8);

	// Upcounter
	TIM2->CR1 &= ~TIM_CR1_DIR;

	// Edge-aligned
	TIM2->CR1 &= ~TIM_CR1_CMS;

	// Auto-reload preload enable
	TIM2->CR1 |= TIM_CR1_ARPE;

	// Prescaler
	TIM2->PSC = 0;

	// Periodendauer
	TIM2->ARR = period_ticks;

	// Update Interrupt aktivieren
	TIM2->DIER |= TIM_DIER_UIE;

	// TIM2 Interrupt im NVIC aktivieren
	NVIC_EnableIRQ(TIM2_IRQn);
}

void tim2_enable()
{
	// Counter starten
	TIM2->CR1 |= TIM_CR1_CEN;
}
	
void tim2_disable()
{
	// Counter stopen
	TIM2->CR1 &= ~TIM_CR1_CEN;
}
