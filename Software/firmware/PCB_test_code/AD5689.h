#ifndef AD5689_H
#define AD5689_H

#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

enum ad5689_address
{
	AD5689_ADRESS_DAC_A = 									0b0001,
	AD5689_ADRESS_DAC_B = 									0b1000,
	AD5689_ADRESS_DAC_AB = 									0b1001
};

enum ad5689_command
{
	AD5689_COMMAND_NOP = 										0b0000,
	AD5689_COMMAND_WRITE_IN_REGISTER =			0b0001,
	AD5689_COMMAND_UPDATE_DAC_IN_REGISTER = 0b0010,
	AD5689_COMMAND_WRITE_UPDATE_DAC	=			  0b0011,
	AD5689_COMMAND_POWER_DO_UP_DAC =				0b0100,
	AD5689_COMMAND_HARDWARE_NLDAC =					0b0101,
	AD5689_COMMAND_SOFT_RESET =							0b0110,
	AD5689_COMMAND_DC_EN =  								0b1000,
	AD5689_COMMAND_READBACK_EN =						0b1001
};

#define AD5689_OP_MODE_NORMAL 								0b00
#define AD5689_OP_MODE_1K_GND 								0b01
#define AD5689_OP_MODE_100K_GND 							0b10
#define AD5689_OP_MODE_TRISTATE 							0b11

uint32_t AD5689_SEND_COMMAND_BLOCKING (	
	enum ad5689_command command,
	enum ad5689_address reg,
	uint16_t data);
	
uint32_t AD5689_transfer_frame(uint32_t tx_frame);
#endif