#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include "ads8681.h"
#include "SPI.h"
#include "PINs.h"
#include "TIMER.h"

#include "relai.h"

#define VREF        2.5
#define RF_100N     10.0e6      // Rf im 100-nA-Bereich (Relais "100n")
#define RF_10U      100.0e3     // Rf im 10-µA-Bereich
#define STAGE_GAIN  (10.0/30.0) // Betrag der Stufe nach dem TIA (-10k/30k)

void ADS8866_inti()
{
	ADC_SPI_NCS = 1;
}

uint16_t ADS8866_GET_CONV()
{
	
	spi1_mode(SPI_DEV_ADC);
	
	uint16_t rx1;
	
	int i;
	
	ADC_SPI_NCS = 0;
	wait_us(10);
	ADC_SPI_NCS = 1;
	wait_us(10);
	ADC_SPI_NCS = 0;
	
	rx1 = spi1_transfer16(0x00);

	ADC_SPI_NCS = 1;

	return rx1;
}

double ADS8866_GET_VOLT()
{
	uint16_t ADC_CON = ADS8866_GET_CONV();
	
	return (double)ADC_CON * VREF / 65536.0;
}