#ifndef SCPI_DEFINES_H
#define SCPI_DEFINES_H

#include <stdio.h>
#include <stdbool.h>
/*

<n>       Platzhalter
<value>   numerischer Wert
{A|B}     Auswahl
[]        optional

:SOURce<n>:VOLTage <value>
:SOURce<n>:VOLTage?
:SOURce<n>:VOLTage:SWEep:STARt <value>
:SOURce<n>:VOLTage:SWEep:STOP <value>
:SOURce<n>:VOLTage:SWEep:STEP <value>
:SOURce<n>:OUTput {ON/OFF}
:SOURce<n>:PROT?
:SOURce<n>:PROT <value>
:SOURce<n>:RANGE {25/50/?}
:SOURce<n>:AUTORANGE {ON/OFF}

:SENSE<n>:CURRENT?
:SENSE<n>:CURRENT <value>
:SENSE<n>:PROT?
:SENSE<n>:PROT <value>
:SENSE<n>:RANGE {100n/10u/?}
:SENSE<n>:AUTORANGE {ON/OFF/?}
:SENSE<n>:MODE:GND {ON/OFF/?}
:SENSE<n>:MODE:AZERO {ON/OFF/?}
:SENSE<n>:MODE:ZCORRECT {AQUIRRE/?}
:SENSE<n>:MODE:ZCORRECT:AQUIRRE <value>
:SENSE<n>:MODE:ZCORRECT:AQUIRRE?
:SENSE<n>:MODE:AVERAGE <value>
:SENSE<n>:MODE:AVERAGE?

:SENSE<n>:MESSURMENT {START/STOP}

:STATUS:?
:STATUS:SYSTEM?
:STATUS:SENSE<n>?
:STATUS:SOURCE<n>?
:STATUS:CAL?

:SYSTEM:?
:SYSTEM:DATE {x(date)/?}
:SYSTEM:LAST_UPDATE {x(date)/?}
:SYSTEM:VERSION {x/?}
:SYSTEM:RESI_HS {ja/?}

:SYSTEM:COMMAND {RESET/?}

:CAL:SENSE<n>:CURRENT {CAL_1nA/CAL_10nA/CAL_100nA}
:CAL:SENSE<n>:CURRENT <value>
:CAL:SENSE<n>:CURRENT?
:CAL:SENSE<n>:RANGE {100n/10u}
:CAL:SENSE<n>:RANGE?
:CAL:SENSE<n>:OFFSET {ACQUIRE}
:CAL:SENSE<n>:OFFSET <value>
:CAL:SENSE<n>:OFFSET?

:CAL:SENSE<n>:CURRENT START
:CAL:SENSE<n>:OFFSET START

:CAL:SOURCE<n>:VOLTAGE {CAL_2048/CAL_2500}
:CAL:SOURCE<n>:VOLTAGE <value>
:CAL:SOURCE<n>:VOLTAGE?
:CAL:SOURCE<n>:RANGE {25/50}
:CAL:SOURCE<n>:RANGE <value>
:CAL:SOURCE<n>:RANGE?
:CAL:SOURCE<n>:OFFSET {ACQUIRE}
:CAL:SOURCE<n>:OFFSET <value>
:CAL:SOURCE<n>:OFFSET?

:CAL:SENSE<n>:VOLTAGE START
:CAL:SENSE<n>:OFFSET START

:CAL:GLOBAL:TEMP {SAVE/LOAD}
:CAL:GLOBAL:FACTORY {SAVE/LOAD}

*/

/* Enums */
typedef enum {
    SOURce_RANGE_25 = 25,
    SOURce_RANGE_50 = 50
} SOURce_RangeTyp;

typedef enum {
    SENSE_RANGE_100n,
    SENSE_RANGE_10u
} SENSE_RangeTyp;

typedef enum {
    CAL_1nA,
    CAL_10nA,
    CAL_100nA
} CURRENT_RangeTyp;

typedef enum {
    CAL_2048,
    CAL_2500
} CAL_SOURCE_VoltTyp;

typedef enum {
    Range_25 = 25,
    Range_50 = 50
} CAL_SOURCE_RangeTyp;

/*----- SOURce Define-Section -----*/
#define SOURce_VOLTage_Last(source)               "SOURce" #source "_VOLTage?"
#define SOURce_VOLTage(source, value)              "SOURce" #source "_VOLTage= " #value
#define SOURce_VOLTage_Sweep_Start(source, value) "SOURce" #source "_Sweep_Start= " #value
#define SOURce_VOLTage_Sweep_Stop(source, value)  "SOURce" #source "_Sweep_Stop= " #value
#define SOURce_VOLTage_Sweep_Step(source, value)  "SOURce" #source "_Sweep_Step= " #value
#define SOURce_VOLTage_Sweep_Time(source, value)  "SOURce" #source "_Sweep_TIme= " #value
#define SOURce_OUTput(source, ON_OFF)             "SOURce" #source "_OUTput= " #ON_OFF
#define SOURce_PROT_currently(source)             "SOURce" #source "_PROT?"
#define SOURce_PROT(source, value)                "SOURce" #source "_PROT= " #value
#define SOURce_RANGE(source, range_enum)          "SOURce" #source "_RANGE= " #range_enum
#define SOURce_RANge_STATE(source)                "SOURce" #source "_RANGE_STATE?"
#define AUTOrange(source, ON_OFF)                 "SOURce" #source "_AUTOrange= " #ON_OFF

/*----- SENSE Define-Section -----*/
#define SENSE_CURRENT_STATE()                     "SENSE_CURRENT_STATE?"
#define SENSE_CURRENT(value)                      "SENSE_CURRENT= " #value
#define SENSE_PROT_currently()                    "SENSE_PROT_currently?"
#define SENSE_RANGE(range_enum)                   "SENSE_RANGE= " #range_enum
#define SENSE_RANge_STATE()                       "SENSE_RANGE_STATE?"
#define SENSE_AUTORANGE(ON_OFF)                   "SENSE_AUTORANGE= " #ON_OFF
#define SENSE_AUTORANGE_currently()               "SENSE_AUTORANGE?"
#define SENSE_MODE_GND(ON_OFF)                    "SENSE_MODE_GND= " #ON_OFF
#define SENSE_MODE_GND_STATE()                    "SENSE_MODE_GND_STATE?"
#define SENSE_MODE_AZERO(ON_OFF)                  "SENSE_MODE_AZERO= " #ON_OFF
#define SENSE_MODE_AZERO_STATE()                  "SENSE_MODE_AZERO_STATE?"
#define SENSE_MODE_ZCORRECT(AQUIRE, STATE)        "SENSE_MODE_ZCORRECT= " #AQUIRE "," #STATE
#define SENSE_MODE_ZCORRECT_AQUIRE(value)        "SENSE_MODE_ZCORRECT_AQUIRE= " #value
#define SENSE_MODE_ZCORRECT_AQUIRE_STATE()       "SENSE_MODE_ZCORRECT_AQUIRE_STATE?"
#define SENSE_MODE_AVERAGE(value)                 "SENSE_MODE_AVERAGE= " #value
#define SENSE_MODE_AVERAGE_STATE()                "SENSE_MODE_AVERAGE_STATE?"
#define SENSE_MODE_MEASUREMENT(START_STOP)        "SENSE_MODE_MEASUREMENT= " #START_STOP

/*----- STATUS Define-Section -----*/
#define STATUS_STATE()                            "STATUS_STATE?"
#define STATUS_SYSTEM()                           "STATUS_SYSTEM?"
#define STATUS_SENSE()                            "STATUS_SENSE?"
#define STATUS_SOURCE()                           "STATUS_SOURCE?"
#define STATUS_CAL()                              "STATUS_CAL?"

/*----- SYSTEM Define-Section -----*/
#define SYSTEM()                                  "SYSTEM?"
#define SYSTEM_DATE(date)                         "SYSTEM_DATE= " #date
#define SYSTEM_DATE_STATE()                       "SYSTEM_DATE_STATE?"
#define SYSTEM_LASTUPDATE()                       "SYSTEM_LASTUPDATe?"
#define SYSTEM_VERSION()                          "SYSTEM_VERSION?"
#define SYSTEM_RESI_HS()                          "SYSTEM_RESI_HS?"
#define SYSTEM_COMMAND(RESET, STATE)              "SYSTEM_COMMAND_RESET=" #RESET #STATE

/*----- CAL Define-Section -----*/
#define CAL_SENSE(range_enum)                     "CAL_SENSE= " #range_enum
#define CAL_SENSE_CURRENT(value)                  "CAL_SENSE_CURRENT= " #value
#define CAL_SENSE_CURRENT_STATE                   "CAL_SENSE_CURRENT?"
#define CAL_SENSE_RANGE(range_enum)               "CAL_SENSE_RANGE= " #range_enum
#define CAL_SENSE_RANGE_STATE()                   "CAL_SENSE_RANGE?"
#define CAL_SENSE_OFFSET_AQUIRE(AQUIRE)           "CAL_SENSE_OFFSET= " #AQUIRE
#define CAL_SENSE_OFFSET(value)                   "CAL_SENSE_OFFSET= " #value
#define CAL_SENSE_OFFSET_STATE()                  "CAL_SEMSE_OFFSET_STATE?"
#define CAL_SENSE_CURRENT_START()                 "CAL_SENSE_CURRENT_START?"
#define CAL_SENSE_OFFSET_START()                  "CAL_SENSE_OFFSET_START?"
#define CAL_SENSE_VOLTAGE_START()                 "CAL_SENSE_VOLTAGE_START?"
#define CAL_SENSE_VoltOFFSET_START()              "CAL_S_VoltOFFSET_START?"

#define CAL_SOURCE_VOLTAGE(voltage_enum)          "CAL_SOURCE_VOLTAGE= " #voltage_enum
#define CAL_SOURCE_VOLTage(value)                 "CAL_SOURCE_VOLTage= "
#define CAL_SOURCE_VOLTAGE_STATE()                "CAL_SOURCE_VOLTAGE_STATE?"
#define CAL_SOURCE_RANGE(range_enum)              "CAL_SOURCE_RANGE= " #range_enum
#define CAL_SOURCE_RANGE_STATE()                  "CAL_SOURCE_RANGE_STATE?"
#define CAL_SOURCE_OFFSET_AQUIRE(AQUIRE)          "CAL_SOURCE_OFFSET_AQUIRE= " #AQUIRE
#define CAL_SOURCE_OFFSET(value)                  "CAL_SOURCE_OFFSET= " #value
#define CAL_SOURCE_OFFSET_STATE()                 "CAL_SOURCE_OFFSET_STATE?"

#define CAL_GLOBAL_TEMP(SAVE_LOAD)                "CAL_GLOBAL_TEMP= " #SAVE_LOAD
#define CAL_GLOBAL_FACTORY(SAVE_LOAD)             "CAL_GLOBAL_FACTORY= " #SAVE_LOAD

/* Prototypen für C-Funktionen */
const char* SCPI_GetSourceRangeString(SOURce_RangeTyp range);
const char* SCPI_GetSenseRangeString(SENSE_RangeTyp range);
const char* SCPI_GetCalCurrentRangeString(CURRENT_RangeTyp range);

int SCPI_Build_SourceVoltage(char *buf, size_t buf_len, int channel, double voltage_val);
int SCPI_Build_SourceOutput(char *buf, size_t buf_len, int channel, bool state);
int SCPI_Build_SenseMeasurement(char *buf, size_t buf_len, bool start);

#endif /* SCPI_DEFINES_H */