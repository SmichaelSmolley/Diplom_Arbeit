#ifndef ADS8866_H
#define ADS8866_H

#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

void ADS8866_inti();

uint16_t ADS8866_GET_CONV();

double ADS8866_GET_VOLT();

#endif