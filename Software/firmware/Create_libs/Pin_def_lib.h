#ifndef PIN_DEF_LIB_H
#define PIN_DEF_LIB_H

#define BITBAND_PERI(a,b) ((PERIPH_BB_BASE + (a-PERIPH_BASE)*32 + (b*4)))
#define GPIOA_ODR GPIOA_BASE + 3*sizeof(uint32_t)
#define GPIOA_IDR GPIOA_BASE + 2*sizeof(uint32_t)

#define ADC_SPI_NCS *((volatile unsigned long *)(BITBAND_PERI(GPIOA_ODR,4)))
#define DAC_SPI_NCS *((volatile unsigned long *)(BITBAND_PERI(GPIOA_ODR,4)))

#endif
