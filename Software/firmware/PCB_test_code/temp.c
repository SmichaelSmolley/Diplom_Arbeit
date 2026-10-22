#include <stm32f10x.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

#include "temp.h"

#include "PINs.h"
#include "TIMER.h"

int ow_reset(void)
{
    int presence;
    OW_LOW();
    delay_us(480);       // Reset-Pulse Länge
    OW_RELEASE();
    delay_us(70);        // Warte, bis DS2438 Presence zieht
		presence = !OW_READ();
    delay_us(410);       // Slot-Ende
    return presence;
}

void send_1()
{
    OW_LOW();
    delay_us(6);
    OW_RELEASE();
    delay_us(64);
}

void send_0()
{
    OW_LOW();
    delay_us(60);
    OW_RELEASE();
    delay_us(10);
}

int read_bit(void)
{
    int bit;

    OW_LOW();          // Start Read Slot
    delay_us(6);
    
    OW_RELEASE();      // Leitung freigeben
    delay_us(9);       // Warten bis Sample-Zeit (~15µs gesamt)

    bit = OW_READ();   // Jetzt lesen!

    delay_us(55);      // Slot fertig machen

    return bit;
}

uint8_t read_byte(void)
{
    uint8_t value = 0;
		int i;
    for( i = 0; i < 8; i++)
    {
        if(read_bit())
        {
            value |= (1 << i);   // LSB first!
        }
    }

    return value;
}

void send_hex(uint8_t num)
{
	int i;
	for(i = 0; i < 8; i++)
	{
    ((num >> i) & 1) ? send_1() : send_0();
	}
}


float ds18b20_read_temp(void)
{
    uint8_t lsb, msb;
    int16_t raw;

    if (!ow_reset()) return -1000.0f;   // kein Presence-Puls -> Fehler
    send_hex(0xCC);                     // Skip ROM
    send_hex(0x44);                     // Convert T starten

    while (!read_bit());                // fertig, wenn Sensor 1 liefert (max. 750 ms bei 12 Bit)

    ow_reset();
    send_hex(0xCC);                     // Skip ROM
    send_hex(0xBE);                     // Read Scratchpad
    lsb = read_byte();
    msb = read_byte();

    raw = (int16_t)((msb << 8) | lsb);
    return raw * 0.0625f;               // 1 LSB = 0,0625 °C bei 12 Bit
}