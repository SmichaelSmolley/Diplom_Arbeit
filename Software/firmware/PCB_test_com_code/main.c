#include "uart.h"
#include "test_data.h"
#include <stdio.h>
#include <string.h>

int main(void)
{
    set_up_uart1();

    char buffer[128];

    while (1)
    {
        if (uart_string_received())
        {
            char* string = uart_get_string();

            if (strcmp(string, "START") == 0)
            {
                uint16_t i = 0;

                for (i = 0; i < 1000; i++)
                {
                    sprintf(buffer, "%i, %.6f\n", i, messwerte[i]);
                    uart_put_string(buffer);
                }
            }
        }
    }
}