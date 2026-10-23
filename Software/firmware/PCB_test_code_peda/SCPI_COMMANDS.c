/**
 * @file scpi_commands.c
 * @brief SCPI Treiber gekoppelt an die UART.c Treiberschnittstelle
 */

#include "scpi_commands.h"
#include "UART.h"
#include <stm32f10x.h>
#include <stdint.h>
#include <stdbool.h>

/* ====================== UART HILFSFUNKTIONEN ====================== */

// Initialisiert die UART1-Schnittstelle
void uart1_init(void)
{
    set_up_uart1();
}

// Sendet ein einzelnes Zeichen über UART
void uart1_put_char(char c)
{
    uart_put_char(c);
}

// Sendet einen Text (String) über UART
void uart1_put_string(const char *s)
{
    uart_put_string((char*)s);
}

// Wandelt eine Ganzzahl in Text um und sendet sie über UART
void uart1_put_int(int value)
{
    char buffer[12];
    int i = 0;

    // Sonderfall: Wert ist 0
    if (value == 0)
    {
        uart_put_char('0');
        return;
    }

    // Vorzeichen bei negativen Zahlen ausgeben
    if (value < 0)
    {
        uart_put_char('-');
        value = -value;
    }

    // Ziffern rückwärts in den Buffer schreiben
    while (value > 0)
    {
        buffer[i++] = (value % 10) + '0';
        value /= 10;
    }

    // Ziffern in der richtigen Reihenfolge ausgeben
    while (i > 0)
    {
        uart_put_char(buffer[--i]);
    }
}

// Wandelt eine Kommazahl (Float) mit gewünschten Nachkommastellen um und sendet sie
void uart1_put_float(float value, int decimals)
{
    // Vorkommastelle ausgeben
    int int_part = (int)value;

    float frac = value - int_part;
    if (frac < 0)
        frac = -frac;

    uart1_put_int(int_part);
    uart_put_char('.');

    // Nachkommastellen einzeln berechnen und ausgeben
    int i;
    for (i = 0; i < decimals; i++)
    {
        frac *= 10;
        int digit = (int)frac;
        uart_put_char(digit + '0');
        frac -= digit;
    }
}

/* ====================== SCPI COMMAND IMPLEMENTIERUNGEN ====================== */

// Sendet den SCPI-Reset-Befehl (*RST)
void scpi_reset(void)
{
    uart_put_string("*RST");
    uart_put_string("\r\n");
}

// Setzt den Mess-/Quellenbereich für einen bestimmten Kanal
void scpi_set_source_range(uint8_t channel, const char *range)
{
    uart_put_string("SOURce");
    uart1_put_int(channel);
    uart_put_string(":RANGe ");
    uart_put_string((char*)range);
    uart_put_string("\r\n");
}

// Setzt den Überspannungsschutz (Protection) für einen Kanal
void scpi_set_source_prot(uint8_t channel, float voltage)
{
    uart_put_string("SOURce");
    uart1_put_int(channel);
    uart_put_string(":PROT ");
    uart1_put_float(voltage, 2);
    uart_put_string("\r\n");
}

// Setzt die Ausgangsspannung für einen bestimmten Kanal
void scpi_set_source_voltage(uint8_t channel, float voltage)
{
    uart_put_string("SOURce");
    uart1_put_int(channel);
    uart_put_string(":VOLTage ");
    uart1_put_float(voltage, 2);
    uart_put_string("\r\n");
}

// Schaltet den Ausgang eines Kanals ein (ON) oder aus (OFF)
void scpi_set_source_output(uint8_t channel, bool state)
{
    uart_put_string("SOURce");
    uart1_put_int(channel);
    uart_put_string(":OUTPut ");
    if (state) {
        uart_put_string("ON");
    } else {
        uart_put_string("OFF");
    }
    uart_put_string("\r\n");
}

// Setzt den Messbereich für Sensoren/Eingänge
void scpi_set_sense_range(const char *range)
{
    uart_put_string("SENSe:RANGe ");
    uart_put_string((char*)range);
    uart_put_string("\r\n");
}

// Schaltet die automatische Messbereichswahl (Autorange) ein oder aus
void scpi_set_sense_autorange(bool state)
{
    uart_put_string("SENSe:AUTOrange ");
    if (state) {
        uart_put_string("ON");
    } else {
        uart_put_string("OFF");
    }
    uart_put_string("\r\n");
}

// Startet die Messung
void scpi_start_measurement(void)
{
    uart_put_string("SENSe:STATe START");
    uart_put_string("\r\n");
}

// Stoppt die Messung
void scpi_stop_measurement(void)
{
    uart_put_string("SENSe:STATe STOP");
    uart_put_string("\r\n");
}