#include <stm32f10x.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include "NVIC.h"
//NVIC INIT
void NVIC_init (char position, char priority)
{
	NVIC->IP[position]=(priority<<4); // setzt interrupt priorität
	NVIC->ICPR[position / 32] = (1UL << (position % 32));
  NVIC->ISER[position / 32] = (1UL << (position % 32));
}