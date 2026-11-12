//==========<std_libs>==========
#include <stm32f10x.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>

//==========<drivers>==========
#include "SPI.h"
#include "UART.h"
#include "PINs.h"
#include "TIMER.h"
#include "dma.h"
#include "clock.h"
#include "relai.h"

//==========<device_libs>==========
#include "ADS8866.h"
#include "AD5689.h"

//==========<scpi_lib>==========
#include "scpi_commands.h"
#include "COMMAND_DECODE.h"

//==========<firmware>==========
#include "measure.h"

uint8_t dummy_buffer[2] = {0x00,0x00};

/* ==========================================
   STANDARDWERTE
   ========================================== */
static void set_default_params(Measure_Param *m)
{
	memset(m, 0, sizeof(*m));

	/* ---------- SOURCE 1 (Gate) ---------- */
	m->source1_voltage     = 0.0f;
	m->source1_sweep_start = 0.0f;
	m->source1_sweep_stop  = 0.0f;
	m->source1_sweep_step  = 0.0f;
	m->source1_sweep_time  = 0.0f;

	m->source1_output    = false;
	m->source1_prot      = 0.0f;
	m->source1_range     = SOURce_RANGE_25;
	m->source1_autorange = false;

	/* ---------- SOURCE 2 (Drain) ---------- */
	m->source2_voltage     = 0.0f;
	m->source2_sweep_start = 0.0f;
	m->source2_sweep_stop  = 0.0f;
	m->source2_sweep_step  = 0.0f;
	m->source2_sweep_time  = 0.0f;

	m->source2_output    = false;
	m->source2_prot      = 0.0f;
	m->source2_range     = SOURce_RANGE_25;
	m->source2_autorange = false;

	/* ---------- SENSE ---------- */
	m->sense_current   = 0.0f;
	m->sense_range     = SENSE_RANGE_10u;   /* passt zu set_range_100k() in main */
	m->sense_autorange = false;

	m->sense_mode_gnd   = false;             /* passt zu Reset_GND_Relai() in main */
	m->sense_mode_azero = false;

	m->sense_zcorrect_aquire = 0.0f;
	m->sense_zcorrect        = false;

	m->sense_average = 100;

	m->sense_measurement    = false;
	m->sense_mode_idvg      = false;
	m->sense_mode_transient = false;

	/* ---------- STRESS ---------- */
	m->stress_type            = STRESS_BTI;
	m->stress_mode            = STRESS_STATIC;
	m->stress_voltage         = 0.0f;
	m->stress_drain_voltage   = 0.0f;
	m->stress_on_time         = 0;
	m->stress_off_time        = 0;
	m->stress_time            = 0;
	m->stress_cycles          = 0;
	m->stress_output          = false;
	m->stress_after_idvg      = false;
	m->stress_after_transient = false;

	/* ---------- TEMP ---------- */
	m->temp_equilibrium_wait = false;

	/* ---------- MSM ---------- */
	m->sense_mode_msm           = false;
	m->msm_cycles               = 5;
	m->msm_start_time           = 1000;     /* 1 s */
	m->msm_time_factor          = 10.0f;
	m->msm_meas_type            = MSM_SPOT;
	m->msm_meas_delay           = 1;        /* 1 ms */
	m->msm_recovery_stress_time = true;
	m->msm_recovery_time        = 0;
	m->msm_initial_measure      = true;
	m->msm_max_points           = 5000;
}

/* ==========================================
   Init
   ========================================== */

void init_all()
{
	PIN_init();
	
	cal_Select_Reset   = 0;     /* Relais-Spulen stromlos */
	cal_Select_set     = 0;
	Range_Select_Reset = 0;
	Range_Select_set   = 0;

	DAC_GAIN      = 0;          /* DAC 0 ... 2,5 V (Gain 1) */
	DAC_SPI_NCS   = 1;          /* Chip-Selects inaktiv */
	ADC_SPI_NCS   = 1;
	SPI_EN_SEND   = 1;
	SPI_ANALOG_EN = 1;

	LED_STATUS  = 0;
	LED_MEASURE = 0;
	LED_ERROR   = 0;
	LED_DATA    = 0;

	/* ---- 3. UART (RX-Interrupt erst ganz am Ende) ---- */
	set_up_uart1();
	uart1_set_baud(115200);

	/* ---- 4. SPI ---- */
	spi1_init();
	spi1_set_baud(5);           /* fPCLK/64 -> 72 MHz/64 = 1,125 MHz */

	/* ---- 5. DMA-Kanäle nur konfigurieren (noch nicht starten) ---- */
	spi1_rx_dma_init();
	spi1_tx_dma_init();

	/* ---- 6. Bausteine ---- */
	AD5689_init();              /* Reset-Puls, Normalbetrieb, beide Kanäle 0 */
	AD5689_set_Voltage(0.0f, AD5689_ADDR_DAC_AB);   /* sicher: Gate + Drain 0 V */
	ADS8866_inti();             /* CS inaktiv */

}

/* ==========================================
   Hauptprogramme
   ========================================== */

int main()
{
	static Measure_Param measure;
	set_default_params(&measure);
	init_all();
	

	set_range_100k();
	reset_GND_Relai();
	
	wait_ms(10000);
	
	uart_put_string("FETCH READY\r\n");
		
	uart1_Rx_Interupt(true);
	
	/* ==========================================
	   HAUPTSCHLEIFE
	   ========================================== */
	
	while(1)
	{
		if(uart_string_received())
		{
			LED_DATA = 1;
			get_Decode_Parameter(uart_get_string(), &measure);
			LED_DATA = 0;
		}
		if(measure.sense_mode_idvg == true)
		{
			IDVG(&measure);
		}
		if(measure.sense_mode_transient == true)
		{
			transient(&measure);
		}
		if(measure.stress_output == true)
		{
			stress(&measure);
		}
		if(measure.temp_equilibrium_wait == true)
		{
			wait_temp_equi(&measure);
		}
		if(measure.sense_mode_msm == true)
		{
			MSM(&measure);
		}
	}
}