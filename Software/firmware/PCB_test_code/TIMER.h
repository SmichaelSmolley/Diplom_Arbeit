#ifndef TIMER_H
#define TIMER_H

#include <stm32f10x.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>

void TIM2_IRQHandler(void);

void wait_ms(int ms);

void init_tim2(uint32_t freq);

void tim2_enable();
void tim2_disable();

#endif