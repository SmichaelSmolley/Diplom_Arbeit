#ifndef TEMP_H
#define TEMP_H

#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

typedef enum { OW_DIGITAL, OW_ANALOG } ow_bus;

float get_temp(ow_bus b);
void ow_write_byte(ow_bus b, uint8_t byte);
uint8_t ow_read_byte(ow_bus b);

#endif