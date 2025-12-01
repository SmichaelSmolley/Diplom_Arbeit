#include <iostream>
#include <stdint.h>

//=====enum's=====
enum class return_data_mode: uint8_t {
    raw_16_bit = 0x00,
    raw_with_range = 0x01,
    raw_with_alarms = 0x02,
    raw_range_alarms = 0x03,
    test_pattern = 0x04,
    shorted_input = 0x05
};

enum class input_range: uint8_t {
        BP_3Vref,
        BP_2_5Vref,
        BP_1_5Vref,
        BP_1_25Vref,
        BP_0_625Vref,
        UP_3Vref,
        UP_2_5Vref,
        UP_1_5Vref,
        UP_1_25Vref
    };

class source_ADC_config{
public:

    //=====Konstruktoren=====

    source_ADC_config():
        internal_ref(true),
        input_range_settings(input_range::BP_3Vref),
        return_data_mode_settings(return_data_mode::raw_with_range),
        include_range_in_data(false),
        include_alarms_in_data(false),
        vdd_alarm_enabled(false),
        input_alarm_enabled(false),
        spi_clock_hz(16000000),
        sample_rate(1000),
        continuous_mode(false),
        measure_average(false),
        middle_fact(1){}


    source_ADC_config(  const bool internal_ref,
                        const input_range input_range,
                        const return_data_mode return_data_mode):
        internal_ref(internal_ref),
        input_range_settings(input_range),
        return_data_mode_settings(return_data_mode),
        include_range_in_data(false),
        include_alarms_in_data(false),
        vdd_alarm_enabled(false),
        input_alarm_enabled(false),
        spi_clock_hz(16000000),
        sample_rate(1000),
        continuous_mode(false),
        measure_average(false),
        middle_fact(1){}
    //=====set_fuc=====


    void set_input_range(input_range input_range);
    void set_return_data_mode(return_data_mode return_data_mode);
    void set_internal_ref(bool internal_ref);
    void set_include_alarms_in_data(bool include_alarms_in_data);
    void set_include_range_in_data(bool include_range_in_data);
    void set_vdd_alarm_enable(bool vdd_alarm_enable);
    void set_input_alarm_enable(bool input_alarm_enable);
    void set_spi_clock_hz(uint32_t hz);
    void set_sample_rate(uint32_t sample_rate);
    void set_continuous_mode(bool continuous_mode);

    //=====anderes=====
    void calibrate();

private:
    bool internal_ref;
    input_range input_range_settings;
    return_data_mode return_data_mode_settings;
    bool include_range_in_data;
    bool include_alarms_in_data;
    bool vdd_alarm_enabled;
    bool input_alarm_enabled;
    uint32_t spi_clock_hz;
    uint32_t sample_rate;
    uint32_t continuous_mode;
    uint32_t measure_average;
    uint32_t middle_fact;

};

