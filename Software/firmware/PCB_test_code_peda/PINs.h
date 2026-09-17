#ifndef PIN_DEF_LIB_H
#define PIN_DEF_LIB_H

#define BITBAND_PERI(a,b) ((PERIPH_BB_BASE + (a-PERIPH_BASE)*32 + (b*4)))
#define GPIOA_ODR GPIOA_BASE + 3*sizeof(uint32_t)
#define GPIOA_IDR GPIOA_BASE + 2*sizeof(uint32_t)

#define GPIOB_ODR GPIOB_BASE + 3*sizeof(uint32_t)
#define GPIOB_IDR GPIOB_BASE + 2*sizeof(uint32_t)
	
#define GPIOC_ODR GPIOC_BASE + 3*sizeof(uint32_t)
#define GPIOC_IDR GPIOC_BASE + 2*sizeof(uint32_t)

#define ADC_SPI_NCS *((volatile unsigned long *)(BITBAND_PERI(GPIOA_ODR,4)))
#define DAC_SPI_NCS *((volatile unsigned long *)(BITBAND_PERI(GPIOA_ODR,1)))
#define OW_BUS_MASTER_OUT *((volatile unsigned long *)(BITBAND_PERI(GPIOB_ODR,0)))
#define OW_BUS_MASTER_IN *((volatile unsigned long *)(BITBAND_PERI(GPIOB_IDR,0)))

#define PER_33V_PSU_EN *((volatile unsigned long *)(BITBAND_PERI(GPIOB_ODR,11)))
#define OPV_PSU_EN *((volatile unsigned long *)(BITBAND_PERI(GPIOB_ODR,7)))
#define ANALOG_5V_PSU_EN *((volatile unsigned long *)(BITBAND_PERI(GPIOB_ODR,1)))

#define cal_Select_set *((volatile unsigned long *)(BITBAND_PERI(GPIOC_ODR,0)))
#define cal_Select_Reset *((volatile unsigned long *)(BITBAND_PERI(GPIOC_ODR,1)))
#define Range_Select_set *((volatile unsigned long *)(BITBAND_PERI(GPIOC_ODR,2)))
#define Range_Select_Reset *((volatile unsigned long *)(BITBAND_PERI(GPIOC_ODR,3)))
	
#define DAC_GAIN *((volatile unsigned long *)(BITBAND_PERI(GPIOA_ODR,2)))
#define DAC_NRESET *((volatile unsigned long *)(BITBAND_PERI(GPIOB_ODR,4)))
#define ADC_NALARM *((volatile unsigned long *)(BITBAND_PERI(GPIOC_IDR,12)))
#define ADC_NRESET *((volatile unsigned long *)(BITBAND_PERI(GPIOC_ODR,13)))
	
#define LED_GREEN *((volatile unsigned long *)(BITBAND_PERI(GPIOB_ODR,9)))
#define LED_RED *((volatile unsigned long *)(BITBAND_PERI(GPIOB_ODR,8)))
	
void PIN_init();

#endif
