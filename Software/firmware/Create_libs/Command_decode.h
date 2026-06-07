#include <stm32f10x.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

//==========KANÄLE==========

#define drain_voltage 									"SOURce1"
#define gate_voltage 										"SOURce2"
#define TIA 														"SENSe1"

//==========FUNKTIONEN==========

#define voltage 												"VOLTage"
#define current 												"CURRent"

//==========RANGE==========

#define messure_range 									"RANGe"
#define Feadback_resisitor_10MEG 				"RANGe 100e-9"
#define Feadback_resisitor_100k 				"RANGe 10e-6"
#define range_mode_Auto_on 							"AUTO ON"
#define range_mode_Auto_off 						"AUTO OFF"

//==========BORDER==========

#define COMPLIANCE_LIMIT 								"PROTection"

//==========SWEEP==========

#define start_value 										"START"
#define step_size 											"STOP"
#define end_value 											"STEP"
#define mode_sweep 											"MODE SWEep"

//==========MODI_CALL==========

#define mode_GND 												"MODE GND"
#define mode_Auto_zero 									"AZEro"
#define mode_zero_call 									"ZCORrect"
#define AZEro_state_on 									"STATe ON"
#define AZEro_state_off 								"STATe OFF"
#define aquire_zero 										"ACQuire"

//==========MITTELUNG_FILTER==========

#define mode_average 										"AVERage"
#define count_of_middel_messurements		"COUNt"

//==========OUTPUTS==========

#define output_akt 											"OUTPut ON"
#define output_deakt										"OUTPut OFF"

//==========COMMANDS==========

#define command_init 										"INITiate"
#define command_reset 									"*CLS"
#define COMMAND_FETCH 									"FETCh?"
#define COMMAND_READ 										"READ?"
#define COMMAND_MEASURE_CURR 						"MEASure:CURRent?"


/*
===================================================================================================
                                   SCPI BEFEHLS-REFIRENZ (MOSFET MESSUNG)
===================================================================================================

 KANÄLE:
  - drain_voltage               : Kanal 1 (SMU), der die Drain-Spannung liefert.
  - gate_voltage                : Kanal 2 (SMU), der die Gate-Spannung steuert.
  - TIA                         : Messkanal 1 (Transimpedanzverstärker) für die Strommessung.

 FUNKTIONEN:
  - voltage / current           : Schaltet Kanäle auf Spannungs- oder Strommodus.

 RANGE (Messbereiche / TIA-Feedback-Widerstände):
  - messure_range               : Allgemeiner Befehl zur Bereichsauswahl.
  - Feadback_resisitor_10MEG    : Aktiviert den 10M-Ohm-Pfad (optimiert für nA-Messungen bis 100 nA).
  - Feadback_resisitor_100k     : Aktiviert den 100k-Ohm-Pfad (für größere Ströme bis 10 µA).
  - range_mode_Auto_on / _off   : Schaltet die automatische Bereichswahl ein oder aus.

 BORDER (Sicherheit):
  - COMPLIANCE_LIMIT            : Setzt das Strom-/Spannungslimit zum Schutz des MOSFETs vor Zerstörung.

 SWEEP (Kennlinienmessung):
  - start_value                 : Startwert der Spannungs-Rampenfunktion.
  - step_size                   : Endwert der Spannungs-Rampenfunktion (Achtung: laut SCPI-Standard "STOP").
  - end_value                   : Schrittweite zwischen den Messpunkten (Achtung: laut SCPI-Standard "STEP").
  - mode_sweep                  : Schaltet den Quellkanal in den automatischen Rampen-Modus.

 MODI_CALL (Masse & Kalibrierung):
  - mode_GND                    : Schaltet den Ausgang direkt und niederohmig auf Masse-Potenzial (GND).
  - mode_Auto_zero              : Aktiviert den automatischen internen Nullabgleich im Hintergrund.
  - mode_zero_call              : Ruft das Subsystem für die manuelle Offset-Korrektur auf.
  - AZEro_state_on / _off       : Schaltet die permanente Autozero-Funktion ein oder aus.
  - aquire_zero                 : Misst den aktuellen Offset-Fehler und speichert ihn als Nullreferenz.

 MITTELUNG_FILTER (Rauschunterdrückung):
  - mode_average                : Aktiviert das digitale Filter-Subsystem zur Messwertglättung.
  - count_of_middel_messurements: Definiert, aus wie vielen Einzelwerten der Mittelwert gebildet wird.

 OUTPUTS (Ausgangsstufe):
  - output_akt / _deakt         : Schaltet die physikalischen Ausgänge (Spannung am MOSFET) ein oder aus.

 COMMANDS (System & Datenabfrage):
  - command_init                : Startet die Messung oder den Sweep-Vorgang im Gerät.
  - command_reset               : Löscht den Status- und Fehlerregister-Speicher (*CLS).
  - COMMAND_FETCH               : Holt bereits gemessene Daten aus dem internen Gerätespeicher ab.
  - COMMAND_READ                : Startet eine Messung und überträgt die Daten sofort in einem Schritt.
  - COMMAND_MEASURE_CURR        : Führt eine direkte, unkonfigurierte Einzelstrommessung durch.
===================================================================================================
*/
