#include <stm32f10x.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include "UART.h"
#include "sys_hard_settings.h"

static volatile char uart_rx_buffer[UART_RX_BUFFER_SIZE];
static volatile uint8_t uart_rx_index = 0;
static volatile bool uart_rx_complete = false;

void USART1_IRQHandler()
{
	if (USART1->SR & 0x20)     // RXNE
	{
		char zeichen;

		zeichen = USART1->DR;

		if (!uart_rx_complete)
		{
			if (zeichen == '\n' || zeichen == '\r')
			{
				uart_rx_buffer[uart_rx_index] = '\0';
				uart_rx_index = 0;

				uart_rx_complete = true;
			}
			else
			{
				if (uart_rx_index < UART_RX_BUFFER_SIZE - 1)
				{
					uart_rx_buffer[uart_rx_index] = zeichen;
					uart_rx_index++;
				}
				else
				{
					// Buffer voll -> String abschließen
					uart_rx_buffer[UART_RX_BUFFER_SIZE - 1] = '\0';
					uart_rx_index = 0;

					uart_rx_complete = true;
				}
			}
		}
	}
}

void set_up_uart1()
{
	RCC->APB2ENR |= 0x4; //GPIOA mit einem Takt versorgen
  
  GPIOA->CRH &= 0xFFFFFF0F;     // reset  PA.9 configuration-bits 
  GPIOA->CRH |= 0xB0;           //Tx (PA9) - alt. out push-pull

  GPIOA->CRH &= 0xFFFFF0FF;     //reset PA.10 configuration-bits 
  GPIOA->CRH |= 0x400;          //Rx (PA10) - floating
	
  RCC->APB2ENR |= 0x4000;       //USART1 mit einem Takt versrogen

	USART1->CR1 &= ~0x1000;       // M: Word length:0 --> Start bit, 8 Data bits, n Stop bit
	USART1->CR1 &= ~0x0400;       // PCE (Parity control enable):0 --> No Parity
	
	USART1->CR2 &= ~0x3000;       // STOP:00 --> 1 Stop bit
	
  //USART1->BRR = 0x341;        // set Baudrate to 9600 Baud (SysClk 72Mhz)

	USART1->BRR = 0x0341; // baud 9600
	
	NVIC_init(USART1_IRQn, 2); //NVIC INT priorität 2
	
  USART1->CR1 |= 0x0C;          // enable  Receiver and Transmitter
	
  USART1->CR1 |= 0x2000;        // Set USART Enable Bit
}

void uart1_Rx_Interupt(bool setting)
{
	setting
		? (USART1->CR1 |= USART_CR1_RXNEIE)
		: (USART1->CR1 &= ~USART_CR1_RXNEIE);
}

void uart_put_char(char zeichen)	
{
	while (!(USART1->SR & 0x80)); //warten, bis die letzten Daten gesendet wurden
	USART1->DR = zeichen;				//Daten in Senderegister schreiben
}

void uart_put_string(char *string)
{
  while (*string)  {
    uart_put_char (*string++);
  }
}

void uart1_set_baud(uint32_t baud)
{
	uint32_t usartdiv;

	usartdiv = (SystemCoreClock + (baud / 2)) / baud;

	USART1->BRR = usartdiv;
}

bool uart_string_received(void)
{
    return uart_rx_complete;
}

/* ============================================================
   String holen
   ============================================================ */

char* uart_get_string(void)
{
    if (uart_rx_complete)
    {
        uart_rx_complete = false;

        return (char*)uart_rx_buffer;
    }

    return NULL;
}