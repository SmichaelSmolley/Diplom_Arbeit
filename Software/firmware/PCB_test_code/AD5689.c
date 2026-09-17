#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include "AD5689.h"
#include "SPI.h"
#include "PINs.h"

bool AD5689_DAC_OUTPUT_GAIN = 0;

void AD5689_init()
{
	DAC_NRESET = 0;
	wait_ms(100);
	DAC_NRESET = 1;
	wait_ms(100);
	
	DAC_GAIN = 0;
	
	AD5689_send_command(0x4, AD5689_ADDR_DAC_AB, 0xFF3C);
	
	AD5689_send_command(AD5689_CMD_WRITE_DAC, AD5689_ADDR_DAC_AB, 0x0000);
	
}

void AD5689_send_command(AD5689_cmd command,
                         AD5689_addr address,
                         uint16_t data)
{
    DAC_SPI_NCS = 0;

    spi1_transfer8((uint8_t)((command << 4) | address));
    spi1_transfer8((uint8_t)(data >> 8));
    spi1_transfer8((uint8_t)data);

    DAC_SPI_NCS = 1;
}

void AD5689_set_Voltage(float Volt, AD5689_addr address)
{
	int16_t data;
	{
		if (Volt < 0.0f)
			Volt = 0.0f;

    if (Volt > 2.5f)
			Volt = 2.5f;

		data = (uint16_t)((Volt / 2.5f) * 65535.0f);
	}
    AD5689_send_command(
        AD5689_CMD_WRITE_DAC,
        address,
        data
    );
}