#include <stm32f10x.h>
#include "PINs.h"

void PIN_init()
{
	 int temp;

	RCC->APB2ENR |= 0x1C; // GPIOA, GPIOB, GPIOC

	//PA1, PA2, PA4 = Output PushPull 50MHz (0x3)
	temp = GPIOA->CRL;
	temp &= 0xFFF0F00F;
	temp |= 0x00030300;
	GPIOC->CRL = temp;
	
	//PB1, PB4, PB7 = Output PushPull 50MHz (0x3)
	//PB0 = Output OpenDrain 50MHz (0x7)
	temp = GPIOB->CRL;
	temp &= 0x0FF0FF00;
	temp |= 0x30030037;
	GPIOB->CRL = temp;
	
	//PB8, PB9, PB11 = Output PushPull 50MHz (0x3)
	temp = GPIOB->CRH;
	temp &= 0xFFFF0F00;
	temp |= 0x00003033;
	GPIOB->CRH = temp;
	
	//PC0, PC1, PC2, PC3 = Output PushPull 50MHz (0x3)
	temp = GPIOC->CRL;
	temp &= 0xFFFF0000;
	temp |= 0x00003333;
	GPIOC->CRL = temp;
	
	//PC12 = Input Pull-Up (0x8)
  //PC13 = Output PushPull (0x3)
	temp = GPIOC->CRH;
	temp &= 0xFF00FFFF;
	temp |= 0x00380000;
	GPIOC->CRH = temp;
	
	GPIOC->BSRR = 0x300F;    // PC13, PC12, PC3..PC0 High
	GPIOB->BSRR = 0x0082;    // PB7 und PB1 High
}