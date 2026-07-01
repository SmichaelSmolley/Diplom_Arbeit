#include <stm32f10x.h>
#include "SPI.h"

void spi1_init()
{
	SPI1->CR1 = 0;  // reset config
	SPI1->CR1 |= (1 << 2);      // MSTR = Master mode
	SPI1->CR1 &= ~(1 << 7);     // MSB first (LSBFIRST = 0)
	// CPOL = 0, CPHA = 1
	SPI1->CR1 &= ~(1 << 1);     // CPOL = 0
	SPI1->CR1 |=  (1 << 0);     // CPHA = 1
	
	// fPCLK / 16 oder /32 typisch
	SPI1->CR1 |= (1 << 3);   // BR[0]
	SPI1->CR1 &= ~(1 << 4);  // BR[1]
	SPI1->CR1 &= ~(1 << 5);  // BR[2]
	// => /16 (Beispiel)
	/*
	
	000: fPCLK/2
	001: fPCLK/4
	010: fPCLK/8
	011: fPCLK/16
	100: fPCLK/32
	101: fPCLK/64
	110: fPCLK/128
	111: fPCLK/256
	
	*/
	// SSM + SSI aktivieren
	SPI1->CR1 |= (1 << 9);   // SSM = 1
	SPI1->CR1 |= (1 << 8);   // SSI = 1
	
	SPI1->CR1 |= (1 << 11);  // DFF = 1 (8-bit mode)
	
	SPI1->CR2 |= SPI_CR2_RXDMAEN;   // RX DMA aktivieren
	
	SPI1->CR1 |= (1 << 6);   // SPE = SPI enable
}

void spi1_set_baud(uint8_t br)
{
	// 1. SPI deaktivieren
	SPI1->CR1 &= ~(1 << 6);   // SPE = 0

	// 2. sicherstellen dass nichts mehr läuft
	while (SPI1->SR & (1 << 7)); // BSY warten

	// 3. Baudrate setzen (BR[2:0])
	SPI1->CR1 &= ~(0x7 << 3);   // alte Bits löschen
	SPI1->CR1 |= (br << 3);     // neue setzen

	// 4. SPI wieder aktivieren
	SPI1->CR1 |= (1 << 6);     // SPE = 1
}

uint16_t spi1_transfer16(uint16_t tx_data)
{
    // Warten bis TX-Register leer
    while (!(SPI1->SR & SPI_SR_TXE));

    // Daten senden
    SPI1->DR = tx_data;

    // Warten bis Daten empfangen wurden
    while (!(SPI1->SR & SPI_SR_RXNE));

    // Empfangene Daten lesen
    uint16_t rx_data = (uint16_t)SPI1->DR;

    // Warten bis SPI nicht mehr beschäftigt ist
    while (SPI1->SR & SPI_SR_BSY);

    return rx_data;
}