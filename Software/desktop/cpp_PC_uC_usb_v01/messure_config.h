//
// Created by micha on 25.11.2025.
//
#include <stdio.h>
#include <stdlib.h>
#include "messure_config_class.h"

#ifndef MESSURE_CONFIG_H
#define MESSURE_CONFIG_H

void source_ADC_config::set_input_range(input_range input_range){
    this->input_range_settings = input_range;
};
void source_ADC_config::set_return_data_mode(return_data_mode return_data_mode){
    this->return_data_mode_settings = return_data_mode;
};
void source_ADC_config::set_internal_ref(bool internal_ref){
    this->internal_ref = internal_ref;
};
void source_ADC_config::set_include_alarms_in_data(bool include_alarms_in_data){
    this->include_alarms_in_data = include_alarms_in_data;
};
void source_ADC_config::set_include_range_in_data(bool include_range_in_data){
    this->include_range_in_data = include_range_in_data;
};
void source_ADC_config::set_vdd_alarm_enable(bool vdd_alarm_enable){
    this->vdd_alarm_enabled = vdd_alarm_enable;
};
void source_ADC_config::set_input_alarm_enable(bool input_alarm_enable){
    this->input_alarm_enabled = input_alarm_enable;
};
void source_ADC_config::set_spi_clock_hz(uint32_t hz){
    this->spi_clock_hz = hz;
};
void source_ADC_config::set_sample_rate(uint32_t sample_rate){
    this->sample_rate = sample_rate;
};
void source_ADC_config::set_continuous_mode(bool continuous_mode){
    this->continuous_mode = continuous_mode;
};

void source_ADC_config::calibrate(){
    //TODO implementieren
    //noch keine ahnung wie
    //kann sein das einfach normal alles übertragen wird
    //oder ganz eigener header
};

#endif //MESSURE_CONFIG_H
