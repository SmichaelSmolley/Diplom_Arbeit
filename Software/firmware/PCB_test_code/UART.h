#ifndef UART1_COM_H
#define UART1_COM_H

#include <stm32f10x.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

void set_up_uart1();
void uart1_Rx_Interupt(bool setting);
void uart_put_char(char zeichen);
void uart_put_string(char *string);

#endif