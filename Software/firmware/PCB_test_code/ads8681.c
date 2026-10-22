#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include "ads8681.h"
#include "SPI.h"
#include "PINs.h"

#include "relai.h"

#define VREF        4.096
#define RF_100N     10.0e6      // Rf im 100-nA-Bereich (Relais "100n")
#define RF_10U      100.0e3     // Rf im 10-µA-Bereich
#define STAGE_GAIN  (10.0/30.0) // Betrag der Stufe nach dem TIA (-10k/30k)

// muss zum Wert im RANGE_SEL-Register passen! (Reset-Default: ±3·VREF)
#define ADC_FSR_HALF (3.0 * VREF)   // ±12.288 V

uint32_t ADS8681_transfer_frame(uint32_t tx_frame)
{
	uint16_t rx1;
	uint16_t rx2;

	ADC_SPI_NCS = 0;

	rx1 = spi1_transfer16(tx_frame >> 16);
	rx2 = spi1_transfer16(tx_frame);

	ADC_SPI_NCS = 1;

	return ((uint32_t)rx1 << 16) | rx2;
}

uint32_t ADS8681_send_Command_blocking(
	enum ads868x_spi_command command,
	enum ads868x_register_address reg,
	uint16_t data)
{
	uint32_t frame;

	frame  = ((uint32_t)((command << 1) | ((reg >> 8) & 1))) << 24;
	frame |= ((uint32_t)(reg & 0xFF)) << 16;
	frame |= data;

	ADS8681_transfer_frame(frame);
	frame = ADS8681_transfer_frame(0x00000000); //NOP to del send buffer ADS8681

	return frame;
}

void ADS8681_init()
{
	ADC_NRESET = 0;
	volatile int i;
	for(i=0;i<10000;i++);
	ADC_NRESET = 1;
	ADC_SPI_NCS = 1;
	
	ADC_SPI_NCS = 0;
	uint32_t range_sel_reg = 0;
	/*
	range_sel_reg |= (uint32_t)
			ADS8681_RANGE_SEL_UP_1_25_VREF
			& ADS8681_RANGE_SEL_MASK
			<< ADS8681_RANGE_SEL_SHIFT;
	ADS8681_send_Command_blocking(ADS868X_SPI_COMMAND_WRITE_FULL, ADS868X_REGISTER_ADDRESS_RANGE_SEL, range_sel_reg);
	*/
	spi1_transfer16(ADS868X_SPI_COMMAND_NOP);
	ADC_SPI_NCS = 1;
}

double ADS8681_get_voltage(uint16_t raw)
{
    // Straight-Binary: 0x0000 = -FS, 0x8000 = 0 V, 0xFFFF = +FS - 1 LSB
    return ((double)raw - 32768.0) * (2.0 * ADC_FSR_HALF / 65536.0);
}

double ADS8681_get_current(uint16_t raw)   // Rückgabe in µA
{
    double u_adc = ADS8681_get_voltage(raw);
    double rf    = range_100n ? RF_100N : RF_10U;

    // U_TIA = -I·Rf ;  U_ADC = -U_TIA·(10/30) = I·Rf/3   ->   I = U_ADC·3/Rf
    return (u_adc / (STAGE_GAIN * rf)) * 1.0e6;
}