#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include "measure.h"
#include "ADS8866.h"
#include "AD5689.h"
#include "TIMER.h"
#include "UART.h"        
#include "PINs.h"        
#include "settings.h"
#include "SEND_DATA.h"

#include "temp.h"

/* __disable_irq(); disablet alle interrupt bis __enable_irq();*/

static void ow_out(ow_bus b, uint32_t level)   /* 0 = Leitung auf GND, 1 = loslassen */
{
	if (b == OW_ANALOG) OW_ANALOG_BM_OUT = level;
	else                OW_DIGITAL_BM_OUT = level;
}
static uint32_t ow_in(ow_bus b)
{
	return (b == OW_ANALOG) ? OW_ANALOG_BM_IN : OW_DIGITAL_BM_IN;
}

static bool ow_reset(ow_bus b)
{
	bool present;
	
	ow_out(b, 0); 
	ow_delay_us(480);
	
	__disable_irq();
	
	ow_out(b, 1); 
	ow_delay_us(70);
	
	present = (ow_in(b) == 0);
	
	__enable_irq();
	
	ow_delay_us(410);
	return present;
}

static void ow_write_bit(ow_bus b, uint8_t bit)
{
	__disable_irq();            
	
	ow_out(b, 0);
	ow_delay_us(bit ? 6 : 60);
	ow_out(b, 1);
	ow_delay_us(bit ? 64 : 10);
	
	__enable_irq();
}

static uint8_t ow_read_bit(ow_bus b)
{
	uint8_t bit;
	
	__disable_irq();
	
	ow_out(b, 0); 
	ow_delay_us(6);
	ow_out(b, 1); 
	ow_delay_us(9);
	bit = (uint8_t)(ow_in(b) & 1u);
	
	__enable_irq();
	
	ow_delay_us(55);
	
	return bit;
}

void ow_write_byte(ow_bus b, uint8_t byte)
{
	int i = 0;
	for(i = 0; i < 8; i++)
	{
		ow_write_bit(b, (byte >> i) & 1);
	}
}

uint8_t ow_read_byte(ow_bus b)
{
	uint8_t return_byte = 0;
	int i;

	for (i = 0; i < 8; i++)
	{
		return_byte |= (uint8_t)(ow_read_bit(b) << i);   // LSB zuerst
	}
	return return_byte;
}

float get_temp(ow_bus b)
{
	ow_reset(b);
	ow_write_byte(b, 0xCC);
	ow_write_byte(b, 0x44);
	wait_ms(800);
	ow_reset(b);
	ow_write_byte(b, 0xCC);
	ow_write_byte(b, 0xBE);
	
	uint8_t temp_buffer[9];
	
	int i = 0;
	for(i = 0; i < 9; i++)
	{
		temp_buffer[i] = ow_read_byte(b);
	}
	int16_t raw = (int16_t)((temp_buffer[1] << 8) | temp_buffer[0]);
	return (float) raw / 16;
}