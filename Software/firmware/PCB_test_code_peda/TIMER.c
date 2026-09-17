#include "TIMER.h"

void wait_ms(int ms)
{
	int j;
	for(j = 0; j < 7987*ms; j++){}
} 