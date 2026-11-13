#ifndef TIMER_H
#define TIMER_H

#include <stm32f10x.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

// TIM2

void TIM2_IRQHandler(void);

void wait_ms(int ms);
bool delay_ms_abortable(uint32_t ms);
void wait_us(int us);

void init_tim2(uint32_t freq);

void tim2_enable();
void tim2_disable();

// TIM3

void     tim3_init(void);                 /* einmal in init_all() */
uint32_t tim3_set_period(uint32_t dt_us); /* Zeit setzen, gibt echten dt zurück */
void     tim3_start(void);
void     tim3_stop(void);
bool     tim3_wait(void);                 /* true = ABORT */

#endif