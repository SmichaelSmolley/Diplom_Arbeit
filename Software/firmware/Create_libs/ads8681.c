#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include "Pin_def_lib.h"
#include "SPI.h"
#include "Timer_DMA.h"
#include "ads8681_lib.h"

void TIM2_IRQHandler(void)
{
    if (TIM2->SR & TIM_SR_UIF)
    {
        TIM2->SR = ~TIM_SR_UIF;

        // Start SPI Transfer
        SPI1->DR = 0x0000;
    }
}

void DMA1_Channel2_IRQHandler(void)
{
    // Transfer Complete Flag prüfen
    if (DMA1->ISR & DMA_ISR_TCIF2)
    {
        // 1. Flag löschen
        DMA1->IFCR = DMA_IFCR_CTCIF2;

        // 2. DMA stoppen (RX)
        DMA1_Channel2->CCR &= ~DMA_CCR1_EN;

        // 3. optional auch TX DMA stoppen (falls aktiv)
        //DMA1_Channel3->CCR &= ~DMA_CCR1_EN;

        // 4. TIM2 stoppen (Sampling aus)
        TIM2->CR1 &= ~TIM_CR1_CEN;

        // 5. optional: CS high (ADS8681 deaktivieren)
        ADC_SPI_NCS = 1;
    }
}

uint32_t ADS8681_transfer_frame(uint32_t tx_frame){
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
	uint16_t data){
	uint32_t frame;

	frame  = ((uint32_t)((command << 1) | ((reg >> 8) & 1))) << 24;
	frame |= ((uint32_t)(reg & 0xFF)) << 16;
	frame |= data;

	ADS8681_transfer_frame(frame);
	frame = ADS8681_transfer_frame(0x00000000); //NOP to del send buffer ADS8681

	return frame;
}
	
void ADS8681_beginn_read_tramsmit(uint16_t* buffer,
	uint32_t numm_of_messurements,
	uint16_t messurement_frequenz){
	
	Tim2_setup(messurement_frequenz);
	DMA_rx_setup_SPI1_to_Mem(buffer, numm_of_messurements);	
	Tim2_enable();
	DMA_rx_enable();
	DMA_tx_enable();
}

