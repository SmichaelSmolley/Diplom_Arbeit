#define BITBAND_PERI(a,b) ((PERIPH_BB_BASE + (a-PERIPH_BASE)*32 + (b*4)))
#define GPIOA_ODR GPIOA_BASE + 3*sizeof(uint32_t)
#define GPIOA_IDR GPIOA_BASE + 2*sizeof(uint32_t)

#define D_out *((volatile unsigned long *)(BITBAND_PERI(GPIOA_ODR,0)))
