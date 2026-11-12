"""Befehlsliste für die serielle Konsole (Autofill).

Quelle: Software/firmware/PCB_test_code/COMMAND_DECODE.c und
Befehlsreferenz_Python_PC.md (Kapitel 3). Format: "NAME= wert".
"""

ON_OFF = ["ON", "OFF"]
TRUE_FALSE = ["TRUE", "FALSE"]

# Name -> (mögliche Werte oder [] für freie Zahl, Kurzbeschreibung)
SCPI_COMMANDS = {}

for n, role in (("1", "Gate"), ("2", "Drain")):
    SCPI_COMMANDS.update({
        f"SOURce{n}_VOLTage": ([], f"[V] fixe Spannung {role}"),
        f"SOURce{n}_Sweep_Start": ([], f"[V] Sweep-Start {role}"),
        f"SOURce{n}_Sweep_Stop": ([], f"[V] Sweep-Ende {role}"),
        f"SOURce{n}_Sweep_Step": ([], f"[V] Schrittweite {role}"),
        f"SOURce{n}_Sweep_TIme": ([], "[ms] Einschwingzeit pro Schritt"),
        f"SOURce{n}_PROT": ([], f"[V] Spannungsgrenze {role}"),
        f"SOURce{n}_RANGE": (["25", "50"], "Ausgangsbereich"),
        f"SOURce{n}_OUTput": (ON_OFF, f"Ausgang {role} ein/aus"),
        f"SOURce{n}_AUTOrange": (ON_OFF, "Autorange Quelle"),
    })

SCPI_COMMANDS.update({
    "SENSE_CURRENT": ([], "Stromziel"),
    "SENSE_RANGE": (["0", "1"], "0 = 100 nA, 1 = 10 µA"),
    "SENSE_AUTORANGE": (ON_OFF, "Autorange Strombereich"),
    "SENSE_MODE_GND": (ON_OFF, "TIA-Eingang auf GND"),
    "SENSE_MODE_AZERO": (ON_OFF, "Auto-Zero"),
    "SENSE_MODE_ZCORRECT_AQUIRE": ([], "Offset-Korrekturwert"),
    "SENSE_MODE_AVERAGE": ([], "Mittelungen pro Punkt"),
    "SENSE_MODE_MEASUREMENT": (["START", "STOP"], "derzeit nicht ausgewertet"),
    "SENSE_MODE_IDVG": (TRUE_FALSE, "START ID-VG"),
    "SENSE_MODE_TRANSIENT": (TRUE_FALSE, "START Transient"),
    "STRESS_TYPE": (["BTI", "HCD"], "Stressart"),
    "STRESS_MODE": (["STATIC", "DYNAMIC"], "Dauer / gepulst"),
    "STRESS_VOLTage": ([], "[V] Gate-Stressspannung"),
    "STRESS_DRAIN_VOLTage": ([], "[V] Drain-Stressspannung (HCD)"),
    "STRESS_TIME": ([], "[ms] Gesamtdauer (STATIC)"),
    "STRESS_ON_TIME": ([], "[ms] Stress pro Puls"),
    "STRESS_OFF_TIME": ([], "[ms] Pause pro Puls"),
    "STRESS_CYCLES": ([], "Anzahl Pulse"),
    "STRESS_AFTER_IDVG": (TRUE_FALSE, "nach Stress ID-VG"),
    "STRESS_AFTER_TRANSIENT": (TRUE_FALSE, "nach Stress Transient"),
    "STRESS_OUTput": (ON_OFF, "START Stress"),
    "Temp_equilibrium_wait": (TRUE_FALSE, "START Temperatur-Wartezeit"),
    "MSM_CYCLES": ([], "Anzahl Zyklen"),
    "MSM_START_TIME": ([], "[ms] erste Stressdauer"),
    "MSM_TIME_FACTOR": ([], "Faktor Stresszeit pro Zyklus"),
    "MSM_MEAS_TYPE": (["SPOT", "IDVG", "TRANSIENT"], "Messart in MSM"),
    "MSM_MEAS_DELAY": ([], "[ms] Stress aus → Messwert"),
    "MSM_RECOVERY_STRESS_TIME": (TRUE_FALSE, "Recovery = Stresszeit"),
    "MSM_RECOVERY_TIME": ([], "[ms] feste Recovery-Zeit"),
    "MSM_INITIAL_MEASURE": (TRUE_FALSE, "Referenzmessung vorher"),
    "MSM_MAX_POINTS": ([], "max. Punkte pro Messung"),
    "SENSE_MODE_MSM": (TRUE_FALSE, "START MSM"),
})

# Befehle ohne "= wert"
NO_ARGUMENT = {
    "ABORT": "bricht Messung/Stress sofort ab",
}


def suggestions(text, limit=8):
    """Vorschläge für die Eingabe: Liste von (Ergebnistext, Beschreibung)."""
    if "=" in text:
        name, _, value = text.partition("=")
        name, value = name.strip(), value.strip()
        values, hint = SCPI_COMMANDS.get(name, ([], ""))
        return [
            (f"{name}= {v}", hint)
            for v in values
            if v.upper().startswith(value.upper()) and v != value
        ][:limit]

    typed = text.strip().upper()
    if not typed:
        return []
    names = list(SCPI_COMMANDS) + list(NO_ARGUMENT)
    starts = [n for n in names if n.upper().startswith(typed)]
    contains = [n for n in names if typed in n.upper() and n not in starts]
    # unscharf: alle Teile (getrennt durch _ oder Leerzeichen) kommen im Namen vor,
    # z. B. "sour1 volt" -> SOURce1_VOLTage, "msm time" -> MSM_START_TIME …
    parts = [t for t in typed.replace("_", " ").split() if t]
    fuzzy = [
        n for n in names
        if n not in starts and n not in contains and all(t in n.upper() for t in parts)
    ]
    result = []
    for n in starts + contains + fuzzy:
        if n.upper() == typed:
            continue
        if n in NO_ARGUMENT:
            result.append((n, NO_ARGUMENT[n]))
        else:
            result.append((f"{n}= ", SCPI_COMMANDS[n][1]))
    return result[:limit]


def is_known(command):
    name = command.partition("=")[0].strip()
    return name in SCPI_COMMANDS or name in NO_ARGUMENT or command.strip() == "ABOR"
