#include "TIMER.h"
#include <stdint.h>
#include <stm32f10x.h>
#include "PINs.h"
#include <stdbool.h>

#include "UART.h"

uint8_t spi_dummy[2] = {0x00, 0x00};

void TIM2_IRQHandler(void)
{
    if (TIM2->SR & TIM_SR_UIF)
    {
      TIM2->SR &= ~TIM_SR_UIF;
			ADC_SPI_NCS = 0;
		  spi1_tx_dma(spi_dummy, 2);
			ADC_SPI_NCS = 1;
		}
}


void wait_ms(int ms)
{
	int j;
	for(j = 0; j < 7987*ms; j++){}
} 

void wait_us(int us)
{
	int j;
	for(j = 0; j < 7*us; j++){}
} 

bool delay_ms_abortable(uint32_t ms)      // true = abgebrochen
{
    while (ms--) {
        if (abort_requested) return true;
        wait_ms(1);
    }
    return false;
}

void init_tim2(uint32_t freq)
{
    if (freq == 0) return; // Schutz vor Division durch Null

    // 1. Takt für TIM2 aktivieren
    RCC->APB1ENR |= RCC_APB1ENR_TIM2EN;

    // 2. Timer stoppen & Zähler zurücksetzen
    TIM2->CR1 &= ~TIM_CR1_CEN;
    TIM2->CNT = 0;

    // 3. Nötigen Gesamtteiler berechnen: Total_Divider = SystemCoreClock / freq
    uint32_t total_divider = SystemCoreClock / freq;

    // 4. Prescaler (PSC) so berechnen, dass ARR in das 16-Bit-Register passt (<= 65536)
    uint32_t psc = (total_divider / 65536);
    
    // ARR berechnen basierend auf dem gewählten Prescaler
    uint32_t arr = (total_divider / (psc + 1)) - 1;

    // Grenzen auf 16 Bit absichern (max 65535)
    if (psc > 65535) psc = 65535;
    if (arr > 65535) arr = 65535;

    // 5. Hardware-Register beschreiben
    TIM2->PSC = (uint16_t)psc;
    TIM2->ARR = (uint16_t)arr;

    // 6. Update-Event erzeugen, um PSC & ARR in die Shadow-Register zu übernehmen
    TIM2->EGR |= TIM_EGR_UG;
    
    // 7. Das durch EGR_UG ungewollt gesetzte UIF-Flag sofort wieder löschen!
    TIM2->SR &= ~TIM_SR_UIF;

    // 8. Interrupt im Timer & NVIC aktivieren
    TIM2->DIER |= TIM_DIER_UIE;
    NVIC_SetPriority(TIM2_IRQn, 1);
    NVIC_EnableIRQ(TIM2_IRQn);
}
void tim2_enable()
{
	// Counter starten
	TIM2->CR1 |= TIM_CR1_CEN;
}
	
void tim2_disable()
{
	// Counter stopen
	TIM2->CR1 &= ~TIM_CR1_CEN;
}

// ==========TIM3==========

void tim3_init(void)
{
	RCC->APB1ENR |= RCC_APB1ENR_TIM3EN;
	TIM3->CR1  = 0;              /* aus, aufwärts zählen */
	TIM3->CR2  = 0;
	TIM3->SMCR = 0;              /* interner Takt */
	TIM3->DIER = 0;              /* kein Interrupt, kein DMA */
	TIM3->SR   = 0;
}

uint32_t tim3_set_period(uint32_t dt_us)
{
	uint32_t tick_us, psc;

	if (dt_us < 2u)
		dt_us = 2u;

	if (dt_us <= 65535u) {            /* bis 65 ms:  1 us Auflösung   */
		tick_us = 1u;    psc = 71u;
	} else if (dt_us <= 6553500u) {   /* bis 6,5 s:  100 us Auflösung */
		tick_us = 100u;  psc = 7199u;
	} else {                          /* bis 32,7 s: 500 us Auflösung */
		tick_us = 500u;  psc = 35999u;
		if (dt_us > 32767500u)
			dt_us = 32767500u;
	}

	TIM3->PSC = (uint16_t)psc;
	TIM3->ARR = (uint16_t)(dt_us / tick_us - 1u);

	return (dt_us / tick_us) * tick_us;
}

void tim3_start(void)
{
	TIM3->CNT  = 0;
	TIM3->EGR  = TIM_EGR_UG;     /* PSC/ARR übernehmen */
	TIM3->SR   = 0;              /* von UG gesetztes UIF löschen */
	TIM3->CR1 |= TIM_CR1_CEN;
}

void tim3_stop(void)
{
	TIM3->CR1 &= ~TIM_CR1_CEN;
}

bool tim3_wait(void)
{
	while (!(TIM3->SR & TIM_SR_UIF))
	{
		if (abort_requested)
			return true;
	}
	TIM3->SR = (uint16_t)~TIM_SR_UIF;   /* nur UIF löschen (rc_w0) */
	return false;
}