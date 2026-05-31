/******************************************************************************/
/*   (C) Copyright HTL - HOLLABRUNN  2009-2020 All rights reserved. AUSTRIA   */ 
/*                                                                            */ 
/* File Name: armv40_std.h                                                    */
/* Autor: 		Josef Reisinger/ Günter Frasl                                   */
/* Version: 	V40.00                                                          */
/* Date: 		  16/05/2023                                                      */
/* Description: Standard Library für ARM Cortex M3                            */
/******************************************************************************/
/* History: V1.00  creation										              									*/
/* 			V1.01  09.06.2010 REJ:                                            		*/
/*                 Add Bit banding Adresses for LED/Switsches Board           */
/*      V2.0   19.02.2011 REJ:                                                */
/*                 - dil_taster_init, dil_led_init hinzugefügt                */
/*                 - lcd_setcursor auf 4 zelige anzeige erweiterst            */
/*                 - Bitbanding Definitiones von Pointer (Adresse der 		  	*/
/*                   Speicherzelle auf Inhalt der Speicherzelle umgestellt    */
/*				         - Fehler bei Portmodi Settings in Init_led Switsches 	  	*/ 
/*                   korrigiert												  											*/
/*      V3.0   21.09.2020                                                     */
/*                 - convert to MMDS Rev9                        							*/
/*                   (Elimination DIL Schalter /DIL LEd's, adapt to           */ 
/*                   LED/Switches to new port lines, Elimination LCD Display  */
/*                   Elimination von ton Funktion                             */
/*			V30.0  06.04.2021																											*/
/*								 - MDDS library adapt UART2 and UART3												*/
/*			V40.0  16.05.2023																											*/
/*								 - MDDS library adapt UART2 and UART3												*/
/******************************************************************************/
/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __ARMV30_STD_H
#define __ARMV30_STD_H

/* ----------------------------Includes ---------------------------------------*/
#include <stm32f10x.h>
#include <stdio.h>

/*----------------------------- Define Pins for LED and Swistches--------------*/
/* ------------------------  Einzel-Portpins im Bitbandbereich festlegen       */

#define GPIOA_IDR GPIOA_BASE + 2*sizeof(uint32_t)    // Calc peripheral address GPIOA IDR
#define GPIOA_ODR GPIOA_BASE + 3*sizeof(uint32_t)
#define GPIOB_IDR GPIOB_BASE + 2*sizeof(uint32_t)
#define GPIOB_ODR GPIOB_BASE + 3*sizeof(uint32_t)	 // Calc peripheral address GPIOB ODR
#define GPIOC_IDR GPIOC_BASE + 2*sizeof(uint32_t)
#define GPIOC_ODR GPIOC_BASE + 3*sizeof(uint32_t)

// Calc Bit Band Adress from peripheral address: a = peripheral address b = Bit number
#define BITBAND_PERI(a,b) ((PERIPH_BB_BASE + (a-PERIPH_BASE)*32 + (b*4)))  

#define SW0  *((volatile unsigned long *)(BITBAND_PERI(GPIOC_IDR,0)))		// PC0
#define SW1  *((volatile unsigned long *)(BITBAND_PERI(GPIOC_IDR,1)))	 	// PC1
#define SW2  *((volatile unsigned long *)(BITBAND_PERI(GPIOC_IDR,2)))		// PC2
#define SW3  *((volatile unsigned long *)(BITBAND_PERI(GPIOC_IDR,3)))	 	// PC3
#define SW4  *((volatile unsigned long *)(BITBAND_PERI(GPIOC_IDR,12))) 	// PC12
#define SW5  *((volatile unsigned long *)(BITBAND_PERI(GPIOC_IDR,13)))	// PC13
#define SW6  *((volatile unsigned long *)(BITBAND_PERI(GPIOB_IDR,6)))	 	// PB6
#define SW7  *((volatile unsigned long *)(BITBAND_PERI(GPIOB_IDR,7))) 	// PB7
	
#define PIEZO *((volatile unsigned long *)(BITBAND_PERI(GPIOA_ODR,4)))	//Portleitung des Piezo-Summers (PA4)

#define LED0  *((volatile unsigned long *)(BITBAND_PERI(GPIOA_ODR,0)))	// PA0
#define LED1  *((volatile unsigned long *)(BITBAND_PERI(GPIOA_ODR,1)))	// PA1
#define LED2  *((volatile unsigned long *)(BITBAND_PERI(GPIOA_ODR,2)))	// PA2
#define LED3  *((volatile unsigned long *)(BITBAND_PERI(GPIOA_ODR,3)))	// PA3
#define LED4  *((volatile unsigned long *)(BITBAND_PERI(GPIOA_ODR,4)))	// PA4
#define LED5  *((volatile unsigned long *)(BITBAND_PERI(GPIOA_ODR,5)))	// PA5
#define LED6  *((volatile unsigned long *)(BITBAND_PERI(GPIOA_ODR,6)))	// PA6
#define LED7  *((volatile unsigned long *)(BITBAND_PERI(GPIOA_ODR,7)))	// PA7

#ifdef ARMV30_STD_MOD
#define EXPORT
#else
#define EXPORT extern
#endif 

/* ----------------------------Exported functions ---------------------------- */

/* ------------------------- Reset and Clock Control    -----------------------*/
/******************************************************************************/
/*            U N T E R P R O G R A M M:                                      */
/*                                                                            */
/* Aufgabe: Set System Clock to 72MHz                                         */
/* Input:   none                                                              */
/* return:	none                                                              */
/******************************************************************************/
EXPORT void set_clock_72MHz(void); 

/* ------------------------- LED/ Switches Board Funktions -------------------*/

/******************************************************************************/
/*            U N T E R P R O G R A M M:    init_leds_switches                */
/*                                                                            */
/* Aufgabe:   Initialisiert Portleitungen für LED / Schalterplatine           */
/* Input:                                                                     */
/* return:	                                                                  */
/******************************************************************************/
EXPORT void init_leds_switches(void); 

/*******************************************************************************/
/*            U N T E R P R O G R A M M:    set_leds                          */
/*                                                                            */
/* Aufgabe:  gibt hexadezimalen Wert in auf 8 Leds aus                        */
/*           (an Port 0 angeschlossen)                                        */
/* Input:    value = Wert auf den LEDS gesetzt werden sollen                  */                                                               
/* return:	                                                                  */
/******************************************************************************/
EXPORT void set_leds (char value);

/******************************************************************************/
/*            U N T E R P R O G R A M M:    get_switches                      */
/*                                                                            */
/* Aufgabe:   liest aktuelle Schalterstellung ein                             */
/* Input:                                                                     */
/* return:	  aktuelle Schalterstellung                                       */
/******************************************************************************/
EXPORT char get_switches(void); 

/* ------------------------- Miscellaneous Funktions --------------------------*/


/******************************************************************************/
/*            U N T E R P R O G R A M M:    WAIT_MS                           */
/*                                                                            */
/* Aufgabe:   Wartet die angegebene Anzahl an Millisekunden                   */
/* Input:     ms = Anzahl der zu wartenden Millisekunden                      */
/* return:	 	                                                              */
/******************************************************************************/
EXPORT void wait_ms(int ms);

/******************************************************************************/
/*            U N T E R P R O G R A M M:    wait_10us                         */
/*                                                                            */
/* Aufgabe:   Wartet 10µs                                                     */
/* Input:                                                                     */
/* return:	 	                                                              */
/******************************************************************************/
EXPORT void wait_10us(void);

/******************************************************************************/
/*            U N T E R P R O G R A M M:                                      */
/*                                                                            */
/* Aufgabe: Function converts a Nibble(0-F) to an ASCII ('0'-'F')             */
/* Input:   nib: Nibble to convert                                            */
/* Output:  nib: Converted Nibble                                             */ 
/* return:	-                                                                 */
/******************************************************************************/
EXPORT void nib2asc(char *nib);

/******************************************************************************/
/*            U N T E R P R O G R A M M:                                      */
/*                                                                            */
/* Aufgabe: Function converts an ASCII('0'-'F') to a Nibble(0-F)              */
/* Input:   asc: ASCII Code                                                   */
/* Output:  asc: Hex Value                                                    */ 
/* return:	- 	                                                              */
/******************************************************************************/
EXPORT void asc2nib(char *asc);

/******************************************************************************/
/*            U N T E R P R O G R A M M:                                      */
/*                                                                            */
/* Aufgabe: Function converts a Hex-Code (00-FF) to an BCD (0-255)            */
/* Input:   hex: Hex Value                                                    */
/* return:	BCD Value                                                         */
/******************************************************************************/
EXPORT int hex2bcd(char hex);


/* ------------------------- UART Funktionen ----------------------------------*/


/******************************************************************************/
/*            U N T E R P R O G R A M M:                                      */
/*                                                                            */
/* Aufgabe: Initialisiert UART2                                               */
/* Input:   Baudrate                                                          */
/* return:	 	                                                              */
/******************************************************************************/
EXPORT void uart2_init(unsigned long baudrate);

/******************************************************************************/
/*            U N T E R P R O G R A M M:                                      */
/*                                                                            */
/* Aufgabe: Initialisiert UART3                                               */
/* Input:   Baudrate                                                          */
/* return:	 	                                                              */
/******************************************************************************/
EXPORT void uart3_init(unsigned long baudrate);

/******************************************************************************/
/*            U N T E R P R O G R A M M:                                      */
/*                                                                            */
/* Aufgabe: liest ein Zeichen von UART2 ein                                   */
/* Input:                                                                     */
/* return:	eingelesens Zeichen                                               */
/******************************************************************************/
EXPORT char uart2_get_char(void); 

/******************************************************************************/
/*            U N T E R P R O G R A M M:                                      */
/*                                                                            */
/* Aufgabe: Ausgabe eines Zeichens auf UART2                                  */
/* Input:   ch: Zeichen in ASCII Code                                         */
/* return:	 	                                                              */
/******************************************************************************/

EXPORT char uart3_get_char(void); 

/******************************************************************************/
/*            U N T E R P R O G R A M M:                                      */
/*                                                                            */
/* Aufgabe: Ausgabe eines Zeichens auf UART3                                  */
/* Input:   ch: Zeichen in ASCII Code                                         */
/* return:	 	                                                              */
/******************************************************************************/
EXPORT void uart2_put_char(char ch);

/******************************************************************************/
/*            U N T E R P R O G R A M M:                                      */
/*                                                                            */
/* Aufgabe: Ausgabe eines 8 Bit Hex Wertes als ASCII String auf UART2         */
/* Input:                                                                     */
/* return:	 	                                                              */
/******************************************************************************/

EXPORT void uart3_put_char(char ch);

/******************************************************************************/
/*            U N T E R P R O G R A M M:                                      */
/*                                                                            */
/* Aufgabe: Ausgabe eines 8 Bit Hex Wertes als ASCII String auf UART3         */
/* Input:                                                                     */
/* return:	 	                                                              */
/******************************************************************************/

EXPORT void uart2_put_hex(char c); 

/******************************************************************************/
/*            U N T E R P R O G R A M M:                                      */
/*                                                                            */
/* Aufgabe: Ausgabe eines Strings auf UART2                                   */
/* Input:   string: C- String der aud UART2 ausgegeben werden soll            */
/* return:	 	                                                              */
/******************************************************************************/

EXPORT void uart3_put_hex(char c); 

/******************************************************************************/
/*            U N T E R P R O G R A M M:                                      */
/*                                                                            */
/* Aufgabe: Ausgabe eines Strings auf UART3                                   */
/* Input:   string: C- String der aud UART3 ausgegeben werden soll            */
/* return:	 	                                                              */
/******************************************************************************/
EXPORT void uart2_put_string(char *string);

/******************************************************************************/
/*            U N T E R P R O G R A M M:                                      */
/*                                                                            */
/* Aufgabe: Ausgabe eines Strings auf UART2                                   */
/* Input:   string: C- String der aud UART2 ausgegeben werden soll            */
/* return:	 	                                                              */
/******************************************************************************/

EXPORT void uart3_put_string(char *string);

/******************************************************************************/
/*            U N T E R P R O G R A M M:                                      */
/*                                                                            */
/* Aufgabe: Ausgabe eines Strings auf UART3                                   */
/* Input:   string: C- String der aud UART3 ausgegeben werden soll            */
/* return:	 	                                                              */
/******************************************************************************/

EXPORT void uart2_clear(void);

/******************************************************************************/
/*            U N T E R P R O G R A M M:                                      */
/*                                                                            */
/* Aufgabe:  sendet Positionierungsstring auf VT100 Terminal "ESC[y;xH"       */
/* Input:                                                                     */
/* return:	 	                                                              */
/******************************************************************************/
EXPORT void uart2_setpos(char x,char y);


/* ------------------------- ADC Funktionen ----------------------------------*/

/******************************************************************************/
/*            U N T E R P R O G R A M M:    adc1_convert                      */
/*                                                                            */
/* Aufgabe:  liefert aktuellen Wert von ADC1 für Kanal channel                */
/*                                                                            */
/* Input:  channel to convert                                                 */                                                               
/* return:	converted value (12Bit right aligned)                             */
/******************************************************************************/
EXPORT unsigned short int adc1_convert(unsigned char channel);

#undef  EXPORT
#endif /* __ARMV10_STD_H */

/******************* (C) HTL - HOLLABRUNN  2009-2010 *****END OF FILE****/
