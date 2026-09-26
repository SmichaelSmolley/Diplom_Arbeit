#ifndef NVIC_H
#define NVIC_H

#include <stm32f10x.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

//NVIC INIT
void NVIC_init (char position, char priority);

#endif