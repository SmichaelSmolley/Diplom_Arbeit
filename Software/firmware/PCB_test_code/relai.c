#include <stm32f10x.h>
#include <stdbool.h>
#include "PINs.h"
#include "TIMER.h"

void set_range_10meg()
{
	Range_Select_set = 1;
	wait_ms(100);
	Range_Select_set = 0;
}

void set_range_100k()
{
	Range_Select_Reset = 1;
	wait_ms(100);
	Range_Select_Reset = 0;
}