#ifndef AD5689_H
#define AD5689_H

#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

typedef enum
{
    AD5689_CMD_NOP             = 0x00,
    AD5689_CMD_WRITE_INPUT     = 0x01,
    AD5689_CMD_UPDATE_DAC      = 0x02,
    AD5689_CMD_WRITE_DAC       = 0x03,
    AD5689_CMD_POWER_DOWN      = 0x04,
    AD5689_CMD_LDAC_MASK       = 0x05,
    AD5689_CMD_SOFTWARE_RESET  = 0x06,
    AD5689_CMD_DCEN            = 0x08,
    AD5689_CMD_READBACK        = 0x09,
    AD5689_CMD_NOP_DAISY       = 0x0F,

} AD5689_cmd;

typedef enum
{
    AD5689_ADDR_DAC_A   = 0b0001,  // DAC B=0, Address=001 -> DAC A
    AD5689_ADDR_DAC_B   = 0b1000,  // DAC B=1, Address=000 -> DAC B
    AD5689_ADDR_DAC_AB  = 0b1001,  // DAC B=1, Address=001 -> DAC A and DAC B

} AD5689_addr;

void AD5689_init();
void AD5689_send_command(AD5689_cmd command, AD5689_addr address, uint16_t);
void AD5689_set_Voltage(float Volt, AD5689_addr address);

#endif