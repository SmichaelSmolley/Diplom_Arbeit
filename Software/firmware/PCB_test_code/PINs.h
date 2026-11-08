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
#define SPI_EN_SEND *((volatile unsigned long *)(BITBAND_PERI(GPIOA_ODR,3)))
#define SPI_ANALOG_EN *((volatile unsigned long *)(BITBAND_PERI(GPIOB_ODR,12)))

#define OW_DIGITAL_BM_OUT *((volatile unsigned long *)(BITBAND_PERI(GPIOB_ODR,9)))
#define OW_DIGITAL_BM_IN *((volatile unsigned long *)(BITBAND_PERI(GPIOB_IDR,9)))
#define OW_ANALOG_BM_OUT *((volatile unsigned long *)(BITBAND_PERI(GPIOC_ODR,5)))
#define OW_ANALOG_BM_IN *((volatile unsigned long *)(BITBAND_PERI(GPIOC_IDR,5)))

#define cal_Select_set *((volatile unsigned long *)(BITBAND_PERI(GPIOC_ODR,2)))
#define cal_Select_Reset *((volatile unsigned long *)(BITBAND_PERI(GPIOC_ODR,0)))
#define Range_Select_set *((volatile unsigned long *)(BITBAND_PERI(GPIOC_ODR,3)))
#define Range_Select_Reset *((volatile unsigned long *)(BITBAND_PERI(GPIOC_ODR,1)))

#define PRE_ANALOG_CARD *((volatile unsigned long *)(BITBAND_PERI(GPIOB_IDR,15)))
#define PRE_KALIB_CARD *((volatile unsigned long *)(BITBAND_PERI(GPIOB_IDR,14)))

#define DAC_GAIN *((volatile unsigned long *)(BITBAND_PERI(GPIOA_ODR,2)))
#define DAC_NRESET *((volatile unsigned long *)(BITBAND_PERI(GPIOB_ODR,5)))
	
#define LED_STATUS *((volatile unsigned long *)(BITBAND_PERI(GPIOC_ODR,8)))
#define LED_MEASURE *((volatile unsigned long *)(BITBAND_PERI(GPIOC_ODR,9)))
#define LED_ERROR *((volatile unsigned long *)(BITBAND_PERI(GPIOC_ODR,10)))
#define LED_DATA *((volatile unsigned long *)(BITBAND_PERI(GPIOC_ODR,11)))

void PIN_init();

#endif
