"""Dateinamen für Messdateien (.h5) – Schema "Präfix_Device_…" (Stil Reisinger-Software).

Festgelegt in Dateinamen_Messungen.md. Verwendet in gui.py (_handle_block).

Beispiele:
    iv_BS170-01_I10u_20261112-1430.h5                     ID-VG einzeln
    tr_BS170-01_I100n_VG1V5_20261112-1430.h5              Transient einzeln
    iv_BS170-01_I10u_BTI5V0_TS60s_20261112-1430.h5        Stress -> Nachmessung ID-VG
    tr_BS170-01_I100n_BTI5V0_ref_c00_20261112-1430.h5     MSM Referenz
    tr_BS170-01_I100n_BTI5V0_TS11s_c02_20261112-1430.h5   MSM Zyklus 2 (gesamt 11 s Stress)
"""

import re
from datetime import datetime
from pathlib import Path

PREFIX = {
    "IDVG": "iv", "MSM_IDVG": "iv",
    "TRANSIENT": "tr", "MSM_TRANSIENT": "tr",
    "SPOT": "sp",
}

# Strombereich aus der GUI-Einstellung (SENSE_RANGE= 0/1, kommt NICHT aus dem MCU-Header)
RANGE = {0: "I100n", 1: "I10u"}


def clean(text):
    """Nur A–Z, a–z, 0–9, '-' erlaubt; alles andere wird '-'."""
    text = re.sub(r"[^A-Za-z0-9-]+", "-", text.strip()).strip("-")
    return text or "unbenannt"


def volt(value):
    """5.0 -> '5V0', 1.25 -> '1V25', -2.4 -> 'm2V4' (Dezimalpunkt als 'V')."""
    sign = "m" if value < 0 else ""
    text = f"{abs(value):.3f}".rstrip("0")
    whole, _, frac = text.partition(".")
    return f"{sign}{whole}V{frac or '0'}"


def stress_time(ms):
    """Gesamte Stresszeit: <1 s in ms, sonst ganze Sekunden: 'TS500ms', 'TS11s'."""
    return f"TS{ms}ms" if ms < 1000 else f"TS{round(ms / 1000)}s"


def make_name(kind, device, start, sense_range, stress_type=None, stress_v=None,
              t_stress_ms=None, cycle=None, read_vg=None):
    """Dateiname ohne Ordner.

    kind        Header-TYPE (IDVG, TRANSIENT, SPOT, MSM_IDVG, MSM_TRANSIENT)
    sense_range gesendeter SENSE_RANGE aus der GUI (0 = 100 nA, 1 = 10 µA)
    start       Startzeit der Messung bzw. des ganzen MSM-Laufs (datetime)
    stress_*    nur bei Stress/MSM
    cycle       nur bei MSM (0 = Referenz)
    read_vg     optional: Gate-Spannung bei Transient einzeln
    """
    parts = [PREFIX[kind], clean(device), RANGE[sense_range]]
    if stress_type is not None and stress_v is not None:
        parts.append(f"{stress_type}{volt(stress_v)}")
    elif read_vg is not None:
        parts.append(f"VG{volt(read_vg)}")
    if cycle is not None:
        parts.append("ref" if cycle == 0 else stress_time(t_stress_ms or 0))
        parts.append(f"c{cycle:02d}")
    elif t_stress_ms is not None:
        parts.append(stress_time(t_stress_ms))
    parts.append(start.strftime("%Y%m%d-%H%M"))
    return "_".join(parts) + ".h5"


def make_path(base_dir, device, name):
    """messungen/<Device>/<name>; hängt _2, _3 … an, falls die Datei schon existiert."""
    folder = Path(base_dir) / clean(device)
    path = folder / name
    n = 2
    while path.exists():
        path = folder / f"{Path(name).stem}_{n}.h5"
        n += 1
    return path
