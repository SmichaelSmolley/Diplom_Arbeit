#include <stm32f10x.h>
#include "PINs.h"

void PIN_init()
{
	int temp;

	RCC->APB2ENR |= 0x1C; // GPIOA, GPIOB, GPIOC

	temp = GPIOA->CRL;
	temp &= 0x0000000F;
	temp |= 0xB4B33330;
	GPIOA->CRL = temp;
	
	temp = GPIOB->CRL;
	temp &= 0xFF0FFFFF;
	temp |= 0x00300000;
	GPIOB->CRL = temp;
	
	temp = GPIOB->CRH;
	temp &= 0x00F0FF0F;
	temp |= 0x44030070;
	GPIOB->CRH = temp;
	
	temp = GPIOC->CRL;
	temp &= 0xFF0F0000;
	temp |= 0x00703333;
	GPIOC->CRL = temp;
	
	temp = GPIOC->CRH;
	temp &= 0xFFFF0000;
	temp |= 0x00003333;
	GPIOC->CRH = temp;
	
	GPIOA->BSRR = 0x000C0012;    // PA1, PA4 High (CS inaktiv); PA2, PA3 Low
	GPIOB->BSRR = 0x10000220;    // PB5, PB9 High; PB12 Low
	GPIOC->BSRR = 0x0F0F0020;    // PC5 High; PC0-PC3, PC8-PC11 Low
}