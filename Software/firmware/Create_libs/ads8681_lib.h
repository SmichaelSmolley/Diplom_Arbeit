#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include "Pin_def_lib.h"
#include "SPI.h"
#include "Timer_DMA.h"

enum ads868x_register_address
{
    ADS868X_REGISTER_ADDRESS_DEVICE_ID      = 0x00,
    ADS868X_REGISTER_ADDRESS_RST_PWRCTL     = 0x04,
    ADS868X_REGISTER_ADDRESS_SDI_CTL        = 0x08,
    ADS868X_REGISTER_ADDRESS_SDO_CTL        = 0x0C,
    ADS868X_REGISTER_ADDRESS_DATAOUT_CTL    = 0x10,
    ADS868X_REGISTER_ADDRESS_RANGE_SEL      = 0x14,
    ADS868X_REGISTER_ADDRESS_ALARM          = 0x20,
    ADS868X_REGISTER_ADDRESS_ALARM_H_TH     = 0x24,
    ADS868X_REGISTER_ADDRESS_ALARM_L_TH     = 0x28
};

enum ads868x_spi_command
{
    ADS868X_SPI_COMMAND_NOP                 = 0b0000000,
    ADS868X_SPI_COMMAND_CLEAR_HWORD         = 0b1100000,
    ADS868X_SPI_COMMAND_READ_HWORD          = 0b1100100,
    ADS868X_SPI_COMMAND_READ                = 0b0100100,
    ADS868X_SPI_COMMAND_WRITE_FULL          = 0b1101000,
    ADS868X_SPI_COMMAND_WRITE_MS            = 0b1101001,
    ADS868X_SPI_COMMAND_WRITE_LS            = 0b1101010,
    ADS868X_SPI_COMMAND_SET_HWORD           = 0b1101100
};

/* DEVICE_ID_REG */
#define ADS8681_DEVICE_ADDR_SHIFT           16
#define ADS8681_DEVICE_ADDR_MASK            0xF

/* RST_PWRCTL_REG */
#define ADS8681_WKEY_SHIFT                  8
#define ADS8681_WKEY_MASK                   0xFF
#define ADS8681_VDD_AL_DIS_SHIFT            5
#define ADS8681_VDD_AL_DIS_MASK             0b1
#define ADS8681_IN_AL_DIS_SHIFT             4
#define ADS8681_IN_AL_DIS_MASK              0b1
#define ADS8681_RSTn_APP_SHIFT              2
#define ADS8681_RSTn_APP_MASK               0b1
#define ADS8681_NAP_EN_SHIFT                1
#define ADS8681_NAP_EN_MASK                 0b1
#define ADS8681_PWRDN_SHIFT                 0
#define ADS8681_PWRDN_MASK                  0b1

/* SDI_CTL_REG */
#define ADS8681_SDI_MODE_SHIFT              0
#define ADS8681_SDI_MODE_MASK               0b11

/* SDO_CTL_REG */
#define ADS8681_GPO_VAL_SHIFT               12
#define ADS8681_GPO_VAL_MASK                0b1
#define ADS8681_SDO1_CONFIG_SHIFT           8
#define ADS8681_SDO1_CONFIG_MASK            0b11
#define ADS8681_SSYNC_CLK_SHIFT             6
#define ADS8681_SSYNC_CLK_MASK              0b1
#define ADS8681_SDO_MODE_SHIFT              0
#define ADS8681_SDO_MODE_MASK               0b11

/* DATAOUT_CTL_REG */
#define ADS8681_DEVICE_ADDR_INCL_SHIFT      14
#define ADS8681_DEVICE_ADDR_INCL_MASK       0b1
#define ADS8681_VDD_ACTIVE_ALARM_INCL_SHIFT 12
#define ADS8681_VDD_ACTIVE_ALARM_INCL_MASK  0b11
#define ADS8681_IN_ACTIVE_ALARM_INCL_SHIFT  10
#define ADS8681_IN_ACTIVE_ALARM_INCL_MASK   0b11
#define ADS8681_RANGE_INCL_SHIFT            8
#define ADS8681_RANGE_INCL_MASK             0b1
#define ADS8681_PAR_EN_SHIFT                3
#define ADS8681_PAR_EN_MASK                 0b1
#define ADS8681_DATA_VAL_SHIFT              0
#define ADS8681_DATA_VAL_MASK               0b111

/* RANGE_SEL_REG */
#define ADS8681_INTREF_DIS_SHIFT            6
#define ADS8681_INTREF_DIS_MASK             0b1
#define ADS8681_RANGE_SEL_SHIFT             0
#define ADS8681_RANGE_SEL_MASK              0xF

#define ADS8681_RANGE_SEL_BP_3_VREF         0b0000  /* = ±3 × VREF */
#define ADS8681_RANGE_SEL_BP_2_5_VREF       0b0001  /* = ±2.5 × VREF */
#define ADS8681_RANGE_SEL_BP_1_5_VREF       0b0010  /* = ±1.5 × VREF */
#define ADS8681_RANGE_SEL_BP_1_25_VREF      0b0011  /* = ±1.25 × VREF */
#define ADS8681_RANGE_SEL_BP_0_625_VREF     0b0100  /* = ±0.625 × VREF */
#define ADS8681_RANGE_SEL_UP_3_VREF         0b1000  /* = 3 × VREF */
#define ADS8681_RANGE_SEL_UP_2_5_VREF       0b1001  /* = 2.5 × VREF */
#define ADS8681_RANGE_SEL_UP_1_5_VREF       0b1010  /* = 1.5 × VREF */
#define ADS8681_RANGE_SEL_UP_1_25_VREF      0b1011  /* = 1.25 × VREF */

/* ALARM_REG */
#define ADS8681_ACTIVE_VDD_L_FLAG_SHIFT     15
#define ADS8681_ACTIVE_VDD_L_FLAG_MASK      0b1
#define ADS8681_ACTIVE_VDD_H_FLAG_SHIFT     14
#define ADS8681_ACTIVE_VDD_H_FLAG_MASK      0b1
#define ADS8681_ACTIVE_IN_L_FLAG_SHIFT      11
#define ADS8681_ACTIVE_IN_L_FLAG_MASK       0b1
#define ADS8681_ACTIVE_IN_H_FLAG_SHIFT      10
#define ADS8681_ACTIVE_IN_H_FLAG_MASK       0b1
#define ADS8681_TRP_VDD_L_FLAG_SHIFT        7
#define ADS8681_TRP_VDD_L_FLAG_MASK         0b1
#define ADS8681_TRP_VDD_H_FLAG_SHIFT        6
#define ADS8681_TRP_VDD_H_FLAG_MASK         0b1
#define ADS8681_TRP_IN_L_FLAG_SHIFT         5
#define ADS8681_TRP_IN_L_FLAG_MASK          0b1
#define ADS8681_TRP_IN_H_FLAG_SHIFT         4
#define ADS8681_TRP_IN_H_FLAG_MASK          0b1
#define ADS8681_OVW_ALARM_SHIFT             0
#define ADS8681_OVW_ALARM_MASK              0b1

/* ALARM_H_TH_REG */
#define ADS8681_INP_ALRM_HYST_SHIFT         24
#define ADS8681_INP_ALRM_HYST_MASK          0xFF
#define ADS8681_INP_ALRM_HIGH_TH_SHIFT      0
#define ADS8681_INP_ALRM_HIGH_TH_MASK       0xFFFF

/* ALARM_L_TH_REG */
#define ADS8681_INP_ALRM_LOW_TH_SHIFT       0
#define ADS8681_INP_ALRM_LOW_TH_MASK        0xFFFF

// Interrupts

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

//funktionen

uint32_t ADS8681_transfer_frame(uint32_t tx_frame);
uint32_t ADS8681_send_Commad_blocking(enum ads868x_spi_command command, enum ads868x_register_address reg, uint16_t data, bool clear_send_buffer_ads8681);
void ADS8681_beginn_tramsmit(uint16_t* buffer, uint32_t numm_of_messurements, uint16_t messurement_frequenz);
uint16_t ADS8681_read();

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
	ADS8681_transfer_frame(0x00000000); //NOP to del send buffer ADS8681

	return frame;
}
	
void ADS8681_beginn_read_tramsmit(uint16_t* buffer,
	uint32_t numm_of_messurements,
	uint16_t messurement_frequenz){
	
	Tim2_setup(messurement_frequenz);
	DMA_rx_setup_SPI1_to_Mem(buffer, numm_of_messurements);	
}

