#ifndef TEMP_H
#define TEMP_H

#include <stm32f10x.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

#include "PINs.h"

#define OW_LOW()   (Temp_intern_out = 0)   // Leitung aktiv LOW ziehen
#define OW_RELEASE() (Temp_intern_out = 1) // Leitung freigeben (Pull-Up zieht HIGH)
#define OW_READ()  (Temp_intern_in)

int ow_reset(void);
void send_1();
void send_0();
int read_bit(void);
uint8_t read_byte(void);
void send_hex(uint8_t num);

float ds18b20_read_temp(void);

#endif