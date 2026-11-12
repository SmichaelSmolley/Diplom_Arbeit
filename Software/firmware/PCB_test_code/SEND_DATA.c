#include <stm32f10x.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#include "COMMAND_DECODE.h"
#include "SEND_DATA.h"
#include "UART.h"

static const char *const type_names[] = {
    "IDVG", "TRANSIENT", "SPOT", "MSM_IDVG", "MSM_TRANSIENT"
};

void send_measure_header(const Data_Header *hdr)
{
	static char buf[200];
	int len;
	len = sprintf(buf,
	"#HDR TYPE=%s N=%lu RANGE=%lu AVG=%lu DT_US=%lu DT_MIN_US=%lu "
	"LOG_Q24=%lu T_START_US=%lu T_STOP_US=%lu CYCLE=%lu T_STRESS_MS=%lu\r\n",
	type_names[hdr->type],
	(unsigned long)hdr->n,
	(unsigned long)hdr->range,
	(unsigned long)hdr->avg,
	(unsigned long)hdr->dt_us,
	(unsigned long)hdr->dt_min_us,
	(unsigned long)hdr->log_q24,
	(unsigned long)hdr->t_start_us,
	(unsigned long)hdr->t_stop_us,
	(unsigned long)hdr->cycle,
	(unsigned long)hdr->t_stress_ms);

	if (len > 0 && len < (int)sizeof(buf))
	{
			uart_put_string(buf);
	}
}

void send_measure_buffer(const Data_Header *hdr, const uint16_t *buffer)
{
	uint16_t sum = 0;
	int i;
	for (i = 0; i < hdr->n; i++)
	{
		uint16_t v = buffer[i];
		uart_put_char((char)(v & 0xFF));   // Low-Byte zuerst
		uart_put_char((char)(v >> 8));     // High-Byte
		sum += v;                          // checksum
	}
}