#include <stm32f10x.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>

void spi1_rx_dma_init(void)
{
    // DMA1 Clock einschalten
    RCC->AHBENR |= RCC_AHBENR_DMA1EN;

    // DMA Channel deaktivieren
    DMA1_Channel2->CCR &= ~DMA_CCR1_EN;

    // SPI1 Data Register als Peripherie-Adresse
    DMA1_Channel2->CPAR = (uint32_t)&SPI1->DR;

    // Richtung: Peripherie -> Speicher
    DMA1_Channel2->CCR &= ~DMA_CCR1_DIR;

    // Peripherie-Adresse nicht erhöhen
    DMA1_Channel2->CCR &= ~DMA_CCR1_PINC;

    // Speicher-Adresse nach jedem Byte erhöhen
    DMA1_Channel2->CCR |= DMA_CCR1_MINC;

    // Peripherie-Datenbreite: 8 Bit
    DMA1_Channel2->CCR &= ~DMA_CCR1_PSIZE;

    // Speicher-Datenbreite: 8 Bit
    DMA1_Channel2->CCR &= ~DMA_CCR1_MSIZE;

    // Normaler Modus
    // DMA stoppt nach CNDTR Übertragungen
    DMA1_Channel2->CCR &= ~DMA_CCR1_CIRC;
}
	
void spi1_rx_dma(uint8_t* buffer, uint16_t num_rx)
{
	// DMA Channel deaktivieren
	DMA1_Channel2->CCR &= ~DMA_CCR1_EN;

	// Zieladresse setzen
	DMA1_Channel2->CMAR = (uint32_t)buffer;

	// Anzahl der zu übertragenden Bytes
	DMA1_Channel2->CNDTR = num_rx;

	// SPI1 RX DMA aktivieren
	SPI1->CR2 |= SPI_CR2_RXDMAEN;

	// DMA Channel starten
	DMA1_Channel2->CCR |= DMA_CCR1_EN;
}

void spi1_tx_dma_init()
{
	// DMA1 Clock einschalten
	RCC->AHBENR |= RCC_AHBENR_DMA1EN;

	// DMA1 Channel 3 deaktivieren
	DMA1_Channel3->CCR &= ~DMA_CCR1_EN;

	// SPI1 Data Register
	DMA1_Channel3->CPAR = (uint32_t)&SPI1->DR;

	// Speicher -> Peripherie
	DMA1_Channel3->CCR |= DMA_CCR1_DIR;

	// Peripherie-Adresse nicht erhöhen
	DMA1_Channel3->CCR &= ~DMA_CCR1_PINC;

	// Speicher-Adresse erhöhen
	DMA1_Channel3->CCR |= DMA_CCR1_MINC;

	// 8 Bit Peripherie
	DMA1_Channel3->CCR &= ~DMA_CCR1_PSIZE;

	// 8 Bit Speicher
	DMA1_Channel3->CCR &= ~DMA_CCR1_MSIZE;

	// Normale Übertragung
	DMA1_Channel3->CCR &= ~DMA_CCR1_CIRC;
}

void spi1_tx_dma(uint8_t* buffer, uint16_t num_tx)
{
	// DMA Channel deaktivieren
	DMA1_Channel3->CCR &= ~DMA_CCR1_EN;

	// Adresse des Sendewertes setzen
	DMA1_Channel3->CMAR = (uint32_t)buffer;

	// Anzahl der zu übertragenden Bytes
	DMA1_Channel3->CNDTR = num_tx;

	// SPI1 TX DMA aktivieren
	SPI1->CR2 |= SPI_CR2_TXDMAEN;

	// DMA Channel starten
	DMA1_Channel3->CCR |= DMA_CCR1_EN;
}	
