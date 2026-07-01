#ifndef SPI_H
#define SPI_H


#include <stm32f10x.h>

typedef enum {
    SPI_BR_DIV2   = 0,
    SPI_BR_DIV4   = 1,
    SPI_BR_DIV8   = 2,
    SPI_BR_DIV16  = 3,
    SPI_BR_DIV32  = 4,
    SPI_BR_DIV64  = 5,
    SPI_BR_DIV128 = 6,
    SPI_BR_DIV256 = 7
} spi_baud_t;

void spi1_init();
void spi1_set_baud(uint8_t br);
uint16_t spi1_transfer16(uint16_t tx_data);

#endif
