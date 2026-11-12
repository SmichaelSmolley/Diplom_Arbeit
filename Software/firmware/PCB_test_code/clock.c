#include <stm32f10x.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>

void clock_init()
{	
	// APB1 = HCLK / 1
	RCC->CFGR &= ~RCC_CFGR_PPRE1;
	RCC->CFGR |= RCC_CFGR_PPRE1_DIV1;

	// APB2 = HCLK / 1
	RCC->CFGR &= ~RCC_CFGR_PPRE2;
	RCC->CFGR |= RCC_CFGR_PPRE2_DIV1;
	
	// PLL ausschalten
	RCC->CR &= ~RCC_CR_PLLON;
}
