from enum import Enum, IntEnum
from dataclasses import dataclass


# ================================
#   ENUMS
# ================================
class InputRange(IntEnum):
    BP_3VREF      = 0
    BP_2_5VREF    = 1
    BP_1_5VREF    = 2
    BP_1_25VREF   = 3
    BP_0_625VREF  = 4
    UP_3VREF      = 5
    UP_2_5VREF    = 6
    UP_1_5VREF    = 7
    UP_1_25VREF   = 8


class ReturnDataMode(IntEnum):
    RAW_16_BIT         = 0x00
    RAW_WITH_RANGE     = 0x01
    RAW_WITH_ALARMS    = 0x02
    RAW_RANGE_ALARMS   = 0x03
    TEST_PATTERN       = 0x04
    SHORTED_INPUT      = 0x05


# ================================
#   DATACLASS
# ================================
@dataclass
class SourceADCConfig:
    
    # Standardwerte
    internal_ref: bool = True
    include_range_in_data: bool = False
    include_alarms_in_data: bool = False
    vdd_alarm_enabled: bool = False
    input_alarm_enabled: bool = False

    spi_clock_hz: int = 16_000_000
    sample_rate: int = 1000

    continuous_mode: bool = False

    measure_average: bool = False
    average_factor: int = 1

    input_range_setting: InputRange = InputRange.BP_3VREF
    return_data_mode_setting: ReturnDataMode = ReturnDataMode.RAW_16_BIT

    data_value_mode: int = 0

    
    # ==========================================
    #   Setter
    # ==========================================
    def set_input_range(self, rng: InputRange):
        self.input_range_setting = rng

    def set_return_data_mode(self, mode: ReturnDataMode):
        self.return_data_mode_setting = mode
        self.data_value_mode = int(mode)

    def set_internal_ref(self, value: bool):
        self.internal_ref = value

    def set_include_range_in_data(self, value: bool):
        self.include_range_in_data = value

    def set_include_alarms_in_data(self, value: bool):
        self.include_alarms_in_data = value

    def set_vdd_alarm_enable(self, value: bool):
        self.vdd_alarm_enabled = value

    def set_input_alarm_enable(self, value: bool):
        self.input_alarm_enabled = value

    def set_spi_clock_hz(self, hz: int):
        self.spi_clock_hz = hz

    def set_sample_rate(self, sr: int):
        self.sample_rate = sr

    def set_continuous_mode(self, mode: bool):
        self.continuous_mode = mode


    # ==========================================
    #   Dummy Kalibrierung (wie in C++)
    # ==========================================
    def calibrate(self):
        print("Starting ADS8681 calibration…")

        # 1) Shorted Input Mode aktivieren
        self.set_return_data_mode(ReturnDataMode.SHORTED_INPUT)
        print("Shorted input mode enabled.")

        # 2) Dummy Offset Messung
        print("Reading offset with shorted input… (dummy)")

        offset = 0  # Placeholder
        print(f"Calibration finished. Offset = {offset}")

        return offset
