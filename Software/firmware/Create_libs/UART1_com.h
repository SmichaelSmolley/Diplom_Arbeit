#include <stm32f10x.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include "NVIC.h"

volatile char rx_buffer[128];
volatile uint16_t rx_index = 0;
volatile bool command_ready = false;

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
	
  USART1->BRR = 0x341;        // set Baudrate to 9600 Baud (SysClk 72Mhz)
  
  USART1->CR1 |= 0x0C;          // enable  Receiver and Transmitter
  USART1->CR1 |= 0x2000;        // Set USART Enable Bit
}

void uart1_Interupt_en()
{
	NVIC_init(USART1_IRQn, 1);
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

void USART1_IRQHandler(void)
{
    if(USART1->SR & USART_SR_RXNE)
    {
        char c = USART1->DR;

        if(c == '\n')
        {
            rx_buffer[rx_index] = '\0';
            command_ready = true;
            rx_index = 0;
        }
        else
        {
            if(rx_index < sizeof(rx_buffer)-1)
            {
                rx_buffer[rx_index++] = c;
            }
        }
    }
}