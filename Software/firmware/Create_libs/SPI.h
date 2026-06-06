#include <stm32f10x.h>

typedef enum {
    SPI_BR_DIV2   = 0,
    SPI_BR_DIV4   = 1,
    SPI_BR_DIV8   = 2,
    SPI_BR_DIV16  = 3,
    SPI_BR_DIV32  = 4,
    SPI_BR_DIV64  = 5,
    SPI_BR_DIV128 = 6,
    SPI_BR_DIV256 = 7
} spi_baud_t;

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

void spi1_send_blocking(uint16_t data)
{
    // warten bis TXE (Transmit buffer empty)
    while (!(SPI1->SR & (1 << 1)));

    // Daten ins Data Register schreiben
    SPI1->DR = data;

    // warten bis Übertragung fertig ist
    while (!(SPI1->SR & (1 << 7)));
}