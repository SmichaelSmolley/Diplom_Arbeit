#ifndef RELAI_H
#define RELAI_H

#include <stm32f10x.h>
#include <stdbool.h>

void set_range_10meg();
void set_range_100k();

void set_GND_Relai(bool sate);
void reset_GND_Relai(bool sate);
#endif