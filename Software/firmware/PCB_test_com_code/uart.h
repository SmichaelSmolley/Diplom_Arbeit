#ifndef UART_H
#define UART_H

#include <stm32f10x.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

#define UART_RX_BUFFER_SIZE 128

void set_up_uart1();
void uart_put_char(char zeichen);
void uart_put_string(char *string);
void uart1_set_baud(uint32_t baud);

bool uart_string_received(void);
char* uart_get_string(void);

#endif