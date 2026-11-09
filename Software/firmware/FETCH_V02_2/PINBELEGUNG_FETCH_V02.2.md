# Pinbelegung FETCH V02.2 – Vorlage für PINs.h / PINs.c

MCU: STM32F103RBT6 (LQFP64), Blatt `CORTEX` (U2), Digitalkarte.
Quelle: Schaltplan-Export vom 15./16.10.2026, CORTEX-Blatt zusätzlich mit dem neuen Screenshot abgeglichen.
Hintergrund und nötige Code-Änderungen: siehe `DOKUMENTATION_Pinbelegung_V02.2.md`.

## 1. Belegte Pins

| Pin | LQFP | Makro in PINs.h | Netz | Richtung | CNF/MODE | Ruhepegel | Backplane | TP | Funktion |
|---|---|---|---|---|---|---|---|---|---|
| PA1 | 15 | `DAC_SPI_NCS` | SPI1_SYNC_DAC | Out PP | 0x3 | High | A14/B14 (diff.) | – | AD5689R SYNC#, Pull-up R13 |
| PA2 | 16 | `DAC_GAIN` | DAC_GAIN | Out PP | 0x3 | Low | A10 | – | L = 0…2,5 V, H = 0…5 V |
| PA3 | 17 | `SPI1_EN_SEND` | SPI1_EN | Out PP | 0x3 | Low, nach SPI-Init High | – | TP15 | Enable M-LVDS-Sender U12, Pull-down R12 |
| PA4 | 20 | `ADC_SPI_NCS` | SPI1_SYNC_ADC | Out PP | 0x3 | High | A20/B20 (diff.) | – | ADS8866 CONVST, Pull-up R14 |
| PA5 | 21 | – | SPI1_CLK | AF PP | 0xB | – | A16/B16 (diff.) | – | SPI1 SCK |
| PA6 | 22 | – | SPI1_MISO | In floating | 0x4 | – | A18/B18 (diff.) | – | SPI1 MISO, von Empfänger U11 |
| PA7 | 23 | – | SPI1_MOSI | AF PP | 0xB | – | A12/B12 (diff.) | – | SPI1 MOSI |
| PA9 | 42 | – | TGT_TX | AF PP | 0xB | – | – | – | USART1 TX, Init in `set_up_uart1()` |
| PA10 | 43 | – | TGT_RX | In floating | 0x4 | – | – | – | USART1 RX, Init in `set_up_uart1()` |
| PA13 | 46 | – | TGT_SWDIO | SWD | nicht anfassen | – | – | – | Debug |
| PA14 | 49 | – | TGT_SWCLK | SWD | nicht anfassen | – | – | – | Debug |
| PB2 | 28 | – | BOOT1 | In floating | 0x4 | – | – | – | Boot-Jumper |
| PB5 | 57 | `DAC_NRESET` | DAC_nRESET | Out PP | 0x3 | High | B10 | – | AD5689R RESET#, Pull-up R4 auf Analogkarte |
| PB9 | 62 | `OW1_MASTER_OUT` / `OW1_MASTER_IN` | OW Master 01 | Out OD | 0x7 | High (losgelassen) | – | TP8 | 1-Wire Klemme U5, Pull-up R15 4,7 kΩ |
| PB12 | 33 | `SPI_ANALOG_EN` | SPI1_ANALOG_EN | Out PP | 0x3 | Low, nach SPI-Init High | A32 | – | Enable MISO-Sender U27 (Analogkarte), Pull-down R33 |
| PB14 | 35 | `PRE_KALIB_CARD` | Pre_Kalibration_card | In floating | 0x4 | – | A23 | TP10 | Kartenerkennung Kalibrierkarte, Pull-up R34 |
| PB15 | 36 | `PRE_ANALOG_CARD` | Pre_Analog_card | In floating | 0x4 | – | A22 | TP9, TP3 | Low = Analogkarte gesteckt, Pull-up R35 |
| PC0 | 8 | `cal_Select_Reset` | GND_Relai_reset | Out PP | 0x3 | Low | B26 | TP7 | Puls auf Reset-Spule U23 |
| PC1 | 9 | `Range_Select_Reset` | Range_Relai_reset | Out PP | 0x3 | Low | A26 | TP6 | Puls auf Reset-Spule U14 (100 kΩ) |
| PC2 | 10 | `cal_Select_set` | GND_Relai_set | Out PP | 0x3 | Low | B25 | TP4 | Puls auf Set-Spule U23 |
| PC3 | 11 | `Range_Select_set` | Range_Relai_set | Out PP | 0x3 | Low | A25 | TP5 | Puls auf Set-Spule U14 (10 MΩ) |
| PC5 | 25 | `OW2_MASTER_OUT` / `OW2_MASTER_IN` | OW Master 02 | Out OD | 0x7 | High (losgelassen) | B32 | – | 1-Wire DS18B20 Analogkarte, Pull-up R18 dort |
| PC8 | 39 | `LED_STATUS` | – | Out PP | 0x3 | Low | – | TP14 | LED D1, High = an |
| PC9 | 40 | `LED_MEASURE` | – | Out PP | 0x3 | Low | – | TP13 | LED D2 „Measure_active“ |
| PC10 | 51 | `LED_ERROR` | – | Out PP | 0x3 | Low | – | TP12 | LED D3 „Error“ |
| PC11 | 52 | `LED_DATA` | – | Out PP | 0x3 | Low | – | TP11 | LED D4 „Data_tran“ |

Fest belegt ohne GPIO-Funktion: PD0/PD1 (HSE 8 MHz), PC14/PC15 (LSE 32,768 kHz), NRST, BOOT0.

## 2. Frei

| Pins | Hinweis |
|---|---|
| PA0, PA8, PB0, PB1, PB8, PB10, PB11, PB13, PC4, PC6, PC7, PC12, PC13, PD2 | nicht beschaltet |
| PA11, PA12 | nur Label `USB_DM`/`USB_DP`, nicht mit dem USB-Port verbunden |
| PB6, PB7 | I²C1 SCL/SDA, auf der Digitalkarte offen |
| PA15, PB3, PB4 | nicht beschaltet, JTAG-Reset-Default bleibt unverändert |

## 3. PINs.h

```c
#ifndef PIN_DEF_LIB_H
#define PIN_DEF_LIB_H

#include <stm32f10x.h>

#define BITBAND_PERI(a,b) ((PERIPH_BB_BASE + (a-PERIPH_BASE)*32 + (b*4)))
#define GPIOA_ODR GPIOA_BASE + 3*sizeof(uint32_t)
#define GPIOA_IDR GPIOA_BASE + 2*sizeof(uint32_t)

#define GPIOB_ODR GPIOB_BASE + 3*sizeof(uint32_t)
#define GPIOB_IDR GPIOB_BASE + 2*sizeof(uint32_t)

#define GPIOC_ODR GPIOC_BASE + 3*sizeof(uint32_t)
#define GPIOC_IDR GPIOC_BASE + 2*sizeof(uint32_t)

/* SPI1 Chip-Selects und Treiber-Enable */
#define ADC_SPI_NCS *((volatile unsigned long *)(BITBAND_PERI(GPIOA_ODR,4)))      /* ADS8866 CONVST */
#define DAC_SPI_NCS *((volatile unsigned long *)(BITBAND_PERI(GPIOA_ODR,1)))
#define SPI1_EN_SEND *((volatile unsigned long *)(BITBAND_PERI(GPIOA_ODR,3)))     /* U12 CLK/MOSI/SYNC */
#define SPI_ANALOG_EN *((volatile unsigned long *)(BITBAND_PERI(GPIOB_ODR,12)))   /* U27 MISO */

/* DAC */
#define DAC_GAIN *((volatile unsigned long *)(BITBAND_PERI(GPIOA_ODR,2)))
#define DAC_NRESET *((volatile unsigned long *)(BITBAND_PERI(GPIOB_ODR,5)))

/* 1-Wire */
#define OW1_MASTER_OUT *((volatile unsigned long *)(BITBAND_PERI(GPIOB_ODR,9)))
#define OW1_MASTER_IN *((volatile unsigned long *)(BITBAND_PERI(GPIOB_IDR,9)))
#define OW2_MASTER_OUT *((volatile unsigned long *)(BITBAND_PERI(GPIOC_ODR,5)))
#define OW2_MASTER_IN *((volatile unsigned long *)(BITBAND_PERI(GPIOC_IDR,5)))

/* Kartenerkennung: 0 = Karte gesteckt */
#define PRE_ANALOG_CARD *((volatile unsigned long *)(BITBAND_PERI(GPIOB_IDR,15)))
#define PRE_KALIB_CARD *((volatile unsigned long *)(BITBAND_PERI(GPIOB_IDR,14)))

/* Latch-Relais: 1 = Spule bestromt, nur als Puls verwenden */
#define cal_Select_set *((volatile unsigned long *)(BITBAND_PERI(GPIOC_ODR,2)))
#define cal_Select_Reset *((volatile unsigned long *)(BITBAND_PERI(GPIOC_ODR,0)))
#define Range_Select_set *((volatile unsigned long *)(BITBAND_PERI(GPIOC_ODR,3)))
#define Range_Select_Reset *((volatile unsigned long *)(BITBAND_PERI(GPIOC_ODR,1)))

/* LEDs: 1 = an */
#define LED_STATUS *((volatile unsigned long *)(BITBAND_PERI(GPIOC_ODR,8)))
#define LED_MEASURE *((volatile unsigned long *)(BITBAND_PERI(GPIOC_ODR,9)))
#define LED_ERROR *((volatile unsigned long *)(BITBAND_PERI(GPIOC_ODR,10)))
#define LED_DATA *((volatile unsigned long *)(BITBAND_PERI(GPIOC_ODR,11)))

void PIN_init();

#endif
```

## 4. PINs.c

Die Ruhepegel werden vor dem Umschalten auf Ausgang gesetzt, damit beim Start kein Relais-Puls und kein Glitch entsteht.
Freie Pins werden auf Input Pull-down (0x8) gelegt. PA9/PA10 setzt weiterhin `set_up_uart1()`, PA13/PA14 (SWD) bleiben unberührt.

```c
#include <stm32f10x.h>
#include "PINs.h"

void PIN_init()
{
	uint32_t temp;

	RCC->APB2ENR |= 0x1C; // GPIOA, GPIOB, GPIOC

	// Ruhepegel VOR der Pin-Konfiguration setzen
	GPIOA->BSRR = (1u << 1) | (1u << 4)                  // PA1, PA4 High (CS inaktiv)
	            | ((1u << 2) | (1u << 3)) << 16;         // PA2, PA3 Low
	GPIOB->BSRR = (1u << 5) | (1u << 9)                  // PB5 High, PB9 losgelassen
	            | (1u << 12) << 16;                      // PB12 Low
	GPIOC->BSRR = (1u << 5)                              // PC5 losgelassen
	            | (0x0F0Fu << 16);                       // PC0-3 (Relais), PC8-11 (LEDs) Low

	// PA7=AF PP, PA6=Input, PA5=AF PP, PA4-PA1=Out PP, PA0=frei
	GPIOA->CRL = 0xB4B33338;

	// PA8, PA11, PA12 = frei; PA9/PA10 = UART, PA13-PA15 unveraendert
	temp = GPIOA->CRH;
	temp &= 0xFFF00FF0;
	temp |= 0x00088008;
	GPIOA->CRH = temp;

	// PB7, PB6=frei, PB5=Out PP, PB4, PB3, PB2=Reset-Default, PB1, PB0=frei
	GPIOB->CRL = 0x88344488;

	// PB15, PB14=Input, PB13=frei, PB12=Out PP, PB11, PB10=frei, PB9=Out OD, PB8=frei
	GPIOB->CRH = 0x44838878;

	// PC7, PC6=frei, PC5=Out OD, PC4=frei, PC3-PC0=Out PP
	GPIOC->CRL = 0x88783333;

	// PC15, PC14=LSE, PC13, PC12=frei, PC11-PC8=Out PP
	GPIOC->CRH = 0x44883333;
}
```
