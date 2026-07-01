#ifndef UART1_COM_H
#define UART1_COM_H

#include <stm32f10x.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

extern volatile char rx_buffer[128];
extern volatile uint16_t rx_index;
extern volatile bool command_ready;

void set_up_uart1();
void uart1_Interupt_en();
void uart1_Interupt_disen();
void uart_put_char(char zeichen);
void uart_put_string(char *string);
void USART1_IRQHandler(void);

#endif
