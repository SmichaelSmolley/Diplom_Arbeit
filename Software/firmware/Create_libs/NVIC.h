#include <stm32f10x.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

//NVIC INIT
static void NVIC_init (char position, char priority)
{
	NVIC->IP[position]=(priority<<4); // setzt interrupt priorität
	NVIC->ICPR[position/32] |= (0x01<<(position%32)); // verhindert interupt wenn ausgelöst
	NVIC->ISER[position/32] |= (0x01<<(position%32)); // Enable Interrupt
}