#include "TIMER.h"
#include <stdint.h>
#include <stm32f10x.h>
#include "PINs.h"
#include <stdbool.h>
uint8_t spi_dummy[2] = {0x00, 0x00};

void TIM2_IRQHandler(void)
{
    if (TIM2->SR & TIM_SR_UIF)
    {
        TIM2->SR &= ~TIM_SR_UIF;
				
				static bool status = 0;
        LED_GREEN = status;
				status =! status;
    }
}


void wait_ms(int ms)
{
	int j;
	for(j = 0; j < 7987*ms; j++){}
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
