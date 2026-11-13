#ifndef RELAI_H
#define RELAI_H

#include <stm32f10x.h>
#include <stdbool.h>

extern bool range_100n;      // true = Rf 10 MOhm (100-nA-Bereich)

void set_range_10meg(void);
void set_range_100k(void);

void set_GND_Relai(void);
void reset_GND_Relai(void);
#endif