#include <Arduino.h>
#include <SPI.h>
#include <stdint.h>
#include "ADS8681.h"
#define baud 9600
#define ADS8681_CS_PIN 2
#define DAC_pin 4
#define Rf 100000
ADS8681 adc(ADS8681_CS_PIN);

String inputString = "";
bool stringComplete = false;

bool readSerial();

void setup() {
  pinMode(DAC_pin, OUTPUT);
  analogWrite(DAC_pin, 255/2);
  Serial.begin(baud);
  uint32_t range_sel_reg = 0;
  range_sel_reg |= (uint32_t)
        ADS8681_RANGE_SEL_UP_1_25_VREF
        & ADS8681_RANGE_SEL_MASK
        << ADS8681_RANGE_SEL_SHIFT;
  adc.spiSend(
        ADS868X_SPI_COMMAND_WRITE_FULL,
        ADS868X_REGISTER_ADDRESS_RANGE_SEL,
        range_sel_reg);
}

void loop() {
  for(float i = 0; i <= 2.5; i=i+0.1){

      int DAC_internal = ((i + 5.0) / 10.0) * 255;

      analogWrite(DAC_pin, DAC_internal);
      uint16_t ret = adc.adcRead();
      Serial.printf("%#08x \t", ret);
      Serial.printf("%d \t", ret);
      Serial.printf("%lf \t", ((4.096*1.25)/65536)*ret);
      float volt = ((4.096*1.25)/65536)*ret;
      Serial.printf("%lf ma\n", ((volt*0.30303)/Rf)*1000);
      delay(100);
  }
  /*if(readSerial()){
    uint16_t ret = adc.adcRead();
    Serial.printf("%#08x \t", ret);
    Serial.printf("%d \t", ret);
    Serial.printf("%lf \t", ((4.096*1.25)/65536)*ret);
    float volt = ((4.096*1.25)/65536)*ret;
    Serial.printf("%lf ma\n", ((volt*0.30303)/10000)*1000);
    delay(100);
  }*/
}

bool readSerial() {
  while (Serial.available()) {
    char c = Serial.read();
    if(c == '\n'){
      stringComplete = true;
      break;
    }
    inputString += c;
  }
  if (stringComplete) {
    if(inputString == "start"){
      return 1;
    }
    else{
      float DAC_external = inputString.toFloat();

      if (DAC_external > 5) DAC_external = 5;
      if (DAC_external < -5) DAC_external = -5;

      int DAC_internal = ((DAC_external + 5.0) / 10.0) * 255;

      analogWrite(DAC_pin, DAC_internal);

      Serial.printf("DAC: %d\n", DAC_internal);

      stringComplete = false;
      inputString = "";
      return 0;
    }
  }
  return 0;
}
