#include <stm32f10x.h>
#include <stdbool.h>
#include "SPI.h"

void spi1_init()
{
	RCC->APB2ENR |= RCC_APB2ENR_SPI1EN;
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
	 
	SPI1->CR1 &= ~SPI_CR1_DFF; // isnd 16 bit !!!! ///to do : ändern und alles auf 8 bit ändern.
	
	//SPI1->CR2 |= SPI_CR2_RXDMAEN;   // RX DMA aktivieren
	
	SPI1->CR1 |= (1 << 6);   // SPE = SPI enable
}
  
void spi1_set_baud(uint8_t baut)
{
	// 1. SPI deaktivieren
	SPI1->CR1 &= ~(1 << 6);   // SPE = 0

	// 2. sicherstellen dass nichts mehr läuft
	while (SPI1->SR & (1 << 7)); // BSY warten

	// 3. Baudrate setzen (BR[2:0])
	SPI1->CR1 &= ~(0x7 << 3);   // alte Bits löschen
	SPI1->CR1 |= (baut << 3);     // neue setzen

	// 4. SPI wieder aktivieren
	SPI1->CR1 |= (1 << 6);     // SPE = 1
}

void spi1_rx_dma_init(uint8_t* buffer, uint16_t buffer_size)
{
	// DMA1 Clock aktivieren
	RCC->AHBENR |= RCC_AHBENR_DMA1EN;

	// DMA Channel 2 deaktivieren
	DMA1_Channel2->CCR &= ~DMA_CCR1_EN;

	// Warten bis DMA wirklich deaktiviert ist
	while (DMA1_Channel2->CCR & DMA_CCR1_EN);

	// Alte Konfiguration löschen
	DMA1_Channel2->CCR = 0;
	
	// Anzahl der Transfers
	DMA1_Channel2->CNDTR = buffer_size;

	// Peripherieadresse = SPI1 Datenregister
	DMA1_Channel2->CPAR = (uint32_t)&SPI1->DR;

	// Speicheradresse = Buffer
	DMA1_Channel2->CMAR = (uint32_t)buffer;
	
	/*
	 * Konfiguration:
	 *
	 * DIR  = 0  -> Peripheral -> Memory
	 * CIRC = 0  -> kein Circular Mode
	 * PINC = 0  -> SPI1->DR Adresse bleibt gleich
	 * MINC = 1  -> Buffer-Adresse wird erhöht
	 *
	 * PSIZE = 00 -> 8 Bit Peripheral
	 * MSIZE = 00 -> 8 Bit Memory
	 *
	 * TCIE = 0 -> zunächst kein Transfer-Complete-Interrupt
	 */
	DMA1_Channel2->CCR |= DMA_CCR1_MINC;

	// DMA aktivieren
	DMA1_Channel2->CCR |= DMA_CCR1_EN;

	// SPI1 soll DMA-Requests für RX erzeugen
	SPI1->CR2 |= SPI_CR2_RXDMAEN;
}

void spi1_tx_dma_init(uint8_t* buffer, uint16_t buffer_size)
{
	// DMA1 Clock aktivieren
	RCC->AHBENR |= RCC_AHBENR_DMA1EN;

	// DMA Channel 2 deaktivieren
	DMA1_Channel3->CCR &= ~DMA_CCR1_EN;

	// Warten bis DMA wirklich deaktiviert ist
	while (DMA1_Channel3->CCR & DMA_CCR1_EN);

	// Alte Konfiguration löschen
	DMA1_Channel3->CCR = 0;
	
	// Anzahl der Transfers
	DMA1_Channel3->CNDTR = buffer_size;

	// Peripherieadresse = SPI1 Datenregister
	DMA1_Channel3->CPAR = (uint32_t)&SPI1->DR;

	// Speicheradresse = Buffer
	DMA1_Channel2->CMAR = (uint32_t)buffer;
	
	// Peripheral -> Memory? NEIN
	// DIR = 1 bedeutet Memory -> Peripheral
	DMA1_Channel3->CCR |= DMA_CCR1_DIR;
	
	// MINC bleibt 0!
	// Dadurch wird data nicht erhöht.

	// DMA aktivieren
	DMA1_Channel3->CCR |= DMA_CCR1_EN;

	// SPI1 soll DMA-Requests für RX erzeugen
	SPI1->CR2 |= SPI_CR2_TXDMAEN;
}

void spi1_rx_dma(bool setting)
{
	setting
		? (SPI1->CR2 |= SPI_CR2_RXDMAEN)
		: (SPI1->CR2 &= ~SPI_CR2_RXDMAEN);
}

uint8_t spi1_transfer8(uint8_t tx_data)
{
	// Warten bis TX-Register leer
	while (!(SPI1->SR & SPI_SR_TXE));

	// Daten senden
	SPI1->DR = tx_data;

	// Warten bis Daten empfangen wurden
	while (!(SPI1->SR & SPI_SR_RXNE));

	// Empfangene Daten lesen
	uint8_t rx_data = (uint8_t)SPI1->DR;

	// Warten bis SPI nicht mehr beschäftigt ist
	while (SPI1->SR & SPI_SR_BSY);

	return rx_data;
}

/*
 * Komfortfunktion für 16 Bit
 *
 * SPI bleibt trotzdem im 8-Bit-Modus.
 *
 * TX:
 *
 *   MSB        LSB
 *   15 .... 8  7 .... 0
 *   [ Byte 1 ] [ Byte 2 ]
 */
uint16_t spi1_transfer16(uint16_t tx_data)
{
    uint16_t rx_data;

    uint8_t rx_high;
    uint8_t rx_low;

    rx_high = spi1_transfer8(
        (uint8_t)(tx_data >> 8)
    );

    rx_low = spi1_transfer8(
        (uint8_t)(tx_data & 0xFFU)
    );

    rx_data = ((uint16_t)rx_high << 8) | rx_low;

    return rx_data;
}

