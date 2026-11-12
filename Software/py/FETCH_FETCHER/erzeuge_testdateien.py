"""Erzeugt künstliche Messungen zum Testen der Auswertung.

Aufruf im venv:   .venv\\Scripts\\python erzeuge_testdateien.py
Ergebnis:         messungen/TEST-A/…  MSM-IDVG (Messung,  max ΔVth ≈ +60 mV)
                  messungen/TEST-B/…  MSM-IDVG (Referenz, max ΔVth ≈ +45 mV)
                  messungen/TEST-C/…  MSM-TRANSIENT: Recovery-Transient nach jedem
                                      Stress (Recovery = Stresszeit), mit RTN
                  messungen/TEST-D/…  einzelner TRANSIENT, LINEARE Zeitachse (1 kHz, 10 s)
                                      mit RTN, Rauschen, 50 Hz und Spikes -> Filter testen
Die Dateien werden mit denselben Funktionen gespeichert wie echte Messungen
(messdaten.save_block, dateinamen.make_name). Modell: Unterschwellstrom
I = 50 nA · exp((VG − Vth) / (n·U_T)) mit Rauschen, ΔVth = A · t^0.2 (BTI-Potenzgesetz).
"""

import math
import random
from datetime import datetime
from pathlib import Path

import dateinamen
import messdaten

OUT = Path(__file__).resolve().parent / "messungen"
VTH0 = 1.20          # V bei I = 50 nA
N_UT = 1.5 * 0.02585 # Unterschwell-Steigung n·U_T
EXPONENT = 0.2       # ΔVth ∝ t^n

COMMANDS = [
    "SENSE_RANGE= 0", "SENSE_AUTORANGE= OFF", "SENSE_MODE_AVERAGE= 100", "SENSE_MODE_GND= OFF",
    "STRESS_TYPE= BTI", "STRESS_MODE= STATIC", "STRESS_VOLTage= 5", "STRESS_DRAIN_VOLTage= 0",
    "MSM_CYCLES= 5", "MSM_START_TIME= 1000", "MSM_TIME_FACTOR= 10", "MSM_MEAS_DELAY= 1",
    "MSM_INITIAL_MEASURE= TRUE", "MSM_MAX_POINTS= 5000",
    "SOURce2_VOLTage= 0.1", "SOURce1_Sweep_Start= 0.8", "SOURce1_Sweep_Stop= 1.6",
    "SOURce1_Sweep_Step= 0.01", "SOURce1_Sweep_TIme= 5", "MSM_MEAS_TYPE= IDVG",
    "SENSE_MODE_MSM= TRUE",
]


def make_run(device, a_mv, start, seed):
    rnd = random.Random(seed)
    params = messdaten.commands_to_params(COMMANDS)
    vg = messdaten.gate_axis(params, 81)
    amp_per_raw = messdaten.raw_to_current([1], 0)[0]       # A pro Rohwert-LSB
    ctx = {"tab": "MSM", "device": device, "start": start, "params": params,
           "run_id": f"{start:%Y%m%d-%H%M%S}_{device}"}

    t_total_ms, t_stress_ms = 0, 1000
    for cycle in range(6):                                  # c00 = Referenz, c01 … c05
        dvth = 0.0 if cycle == 0 else a_mv * 1e-3 * (t_total_ms / 1000) ** EXPONENT
        vth = VTH0 + dvth + rnd.gauss(0, 0.5e-3)            # 0,5 mV Messstreuung
        raw = []
        for v in vg:
            i = 50e-9 * math.exp((v - vth) / N_UT) * (1 + rnd.gauss(0, 0.01))
            raw.append(max(0, min(65535, round(i / amp_per_raw + rnd.gauss(0, 3)))))
        hdr = {"TYPE": "MSM_IDVG", "N": len(raw), "RANGE": 0, "AVG": 100, "DT_US": 0,
               "DT_MIN_US": 0, "LOG_Q24": 0, "T_START_US": 1000, "T_STOP_US": 0,
               "CYCLE": cycle, "T_STRESS_MS": t_total_ms}
        name = dateinamen.make_name("MSM_IDVG", device, start, 0, "BTI", 5.0, t_total_ms, cycle)
        path = dateinamen.make_path(OUT, device, name)
        messdaten.save_block(path, hdr, raw, ctx)
        print(f"  {path.relative_to(OUT.parent)}   ΔVth = {dvth*1e3:5.1f} mV")
        if cycle > 0:
            t_stress_ms *= 10
        t_total_ms += t_stress_ms if cycle > 0 else 1000
        if cycle == 0:
            t_stress_ms = 1000


# ---------------------------------------------------------------------------
# TEST-C: MSM mit Messart TRANSIENT (Recovery nach jedem Stress)
# ---------------------------------------------------------------------------
READ_VG = 1.25        # Lese-Gatespannung knapp über Vth -> Strom im 100-nA-Bereich
DT_MIN_US = 1000      # 100 Mittelungen bei 100 kSPS ≈ 1 ms pro Punkt
MAX_POINTS = 5000
RELAX_B, RELAX_BETA = 0.3, 0.2   # universelle Relaxation r(ξ) = 1 / (1 + B·ξ^β)

TRANSIENT_COMMANDS = [c for c in COMMANDS if not c.startswith(("SOURce1_Sweep", "MSM_MEAS_TYPE",
                                                               "SENSE_MODE_MSM"))] + [
    f"SOURce1_VOLTage= {READ_VG}", "MSM_MEAS_TYPE= TRANSIENT",
    "MSM_RECOVERY_STRESS_TIME= TRUE", "SENSE_MODE_MSM= TRUE",
]


def log_q24(t_start_us, t_stop_us, n_max):
    """Wie log_calc_q24() in der Firmware (Datenformat Kap. 5.2)."""
    r = (t_stop_us / t_start_us) ** (1.0 / (n_max - 1))
    return int((r - 1.0) * 16777216.0 + 0.5)


def make_transient_run(device, a_mv, start, seed):
    rnd = random.Random(seed)
    params = messdaten.commands_to_params(TRANSIENT_COMMANDS)
    amp_per_raw = messdaten.raw_to_current([1], 0)[0]
    ctx = {"tab": "MSM", "device": device, "start": start, "params": params,
           "run_id": f"{start:%Y%m%d-%H%M%S}_{device}"}

    t_total_ms = 0
    for cycle in range(6):
        stress_ms = 0 if cycle == 0 else 1000 * 10 ** (cycle - 1)    # 1 s, 10 s, 100 s …
        t_total_ms += stress_ms
        window_ms = stress_ms or 1000                               # Referenz: 1 s Fenster
        t_start, t_stop = 1000, window_ms * 1000                    # MSM_MEAS_DELAY = 1 ms
        q24 = log_q24(t_start, t_stop, MAX_POINTS)
        times = [t_start]                                           # Zeitpunkte wie Firmware
        while len(times) < MAX_POINTS:
            nxt = times[-1] + max(DT_MIN_US, (times[-1] * q24) >> 24)
            if nxt > t_stop:
                break
            times.append(nxt)

        dvth_stress = 0.0 if cycle == 0 else a_mv * 1e-3 * (t_total_ms / 1000) ** EXPONENT
        trap = rnd.random() < 0.5            # RTN: ein Trap, zwei Niveaus
        t_prev, raw = 0, []
        for t_us in times:
            # Trap wechselt zufällig (τ_c ≈ 20 ms, τ_e ≈ 50 ms)
            dt = (t_us - t_prev) * 1e-6
            tau = 0.020 if not trap else 0.050
            if rnd.random() < 1 - math.exp(-dt / tau):
                trap = not trap
            t_prev = t_us
            relax = 1.0 if cycle == 0 else 1 / (1 + RELAX_B * (t_us / 1000 / stress_ms) ** RELAX_BETA)
            vth = VTH0 + dvth_stress * relax + (1.5e-3 if trap else 0.0)   # RTN ≈ 1,5 mV
            i = 50e-9 * math.exp((READ_VG - vth) / N_UT) * (1 + rnd.gauss(0, 0.004))
            raw.append(max(0, min(65535, round(i / amp_per_raw + rnd.gauss(0, 3)))))

        hdr = {"TYPE": "MSM_TRANSIENT", "N": len(raw), "RANGE": 0, "AVG": 100, "DT_US": 0,
               "DT_MIN_US": DT_MIN_US, "LOG_Q24": q24, "T_START_US": t_start,
               "T_STOP_US": t_stop, "CYCLE": cycle, "T_STRESS_MS": t_total_ms}
        assert messdaten.time_axis_us(hdr) == times          # gleiche Zeitachse wie Python-Empfang
        name = dateinamen.make_name("MSM_TRANSIENT", device, start, 0, "BTI", 5.0, t_total_ms, cycle)
        path = dateinamen.make_path(OUT, device, name)
        messdaten.save_block(path, hdr, raw, ctx)
        print(f"  {path.relative_to(OUT.parent)}   N = {len(raw):4d}, "
              f"Recovery {window_ms/1000:g} s, ΔVth nach Stress = {dvth_stress*1e3:5.1f} mV")


# ---------------------------------------------------------------------------
# TEST-D: einzelner Transient mit linearer Zeitachse (zum Ausprobieren der Filter)
# ---------------------------------------------------------------------------
LIN_DT_US = 1000      # 1 kHz (100 Mittelungen bei 100 kSPS)
LIN_POINTS = 10000    # 10 s


def make_linear_transient(device, start, seed):
    rnd = random.Random(seed)
    params = messdaten.commands_to_params([
        "SENSE_RANGE= 0", "SENSE_AUTORANGE= OFF", "SENSE_MODE_AVERAGE= 100", "SENSE_MODE_GND= OFF",
        f"SOURce1_VOLTage= {READ_VG}", "SOURce2_VOLTage= 0.1", "SENSE_MODE_TRANSIENT= TRUE"])
    amp_per_raw = messdaten.raw_to_current([1], 0)[0]
    ctx = {"tab": "Transient", "device": device, "start": start, "params": params,
           "run_id": f"{start:%Y%m%d-%H%M%S}_{device}"}

    # zwei Traps: langsam (1,5 mV, τ ≈ 0,3 s / 0,8 s) und schnell (0,6 mV, τ ≈ 8 ms / 15 ms)
    traps = [{"dv": 1.5e-3, "tau": (0.30, 0.80), "on": False},
             {"dv": 0.6e-3, "tau": (0.008, 0.015), "on": True}]
    dt = LIN_DT_US * 1e-6
    raw = []
    for k in range(LIN_POINTS):
        t = k * dt
        for tr in traps:
            tau = tr["tau"][1] if tr["on"] else tr["tau"][0]
            if rnd.random() < 1 - math.exp(-dt / tau):
                tr["on"] = not tr["on"]
        vth = VTH0 + sum(tr["dv"] for tr in traps if tr["on"])
        i = 50e-9 * math.exp((READ_VG - vth) / N_UT)
        i += rnd.gauss(0, 1.5e-9)                              # weißes Rauschen ≈ 1,5 nA
        i += 2e-9 * math.sin(2 * math.pi * 50 * t + 0.3)       # 50-Hz-Brumm 2 nA
        if rnd.random() < 0.001:                               # ≈ 10 Spikes (Störimpulse)
            i += rnd.choice((-1, 1)) * rnd.uniform(15e-9, 30e-9)
        raw.append(max(0, min(65535, round(i / amp_per_raw))))

    hdr = {"TYPE": "TRANSIENT", "N": LIN_POINTS, "RANGE": 0, "AVG": 100, "DT_US": LIN_DT_US,
           "DT_MIN_US": 0, "LOG_Q24": 0, "T_START_US": 0, "T_STOP_US": 0,
           "CYCLE": 0, "T_STRESS_MS": 0}
    name = dateinamen.make_name("TRANSIENT", device, start, 0, read_vg=READ_VG)
    path = dateinamen.make_path(OUT, device, name)
    messdaten.save_block(path, hdr, raw, ctx)
    print(f"  {path.relative_to(OUT.parent)}   N = {LIN_POINTS}, 1 kHz, 10 s")


if __name__ == "__main__":
    print("Messung:")
    make_run("TEST-A", 9.5, datetime(2026, 11, 12, 15, 0), seed=1)
    print("Referenz:")
    make_run("TEST-B", 7.1, datetime(2026, 11, 12, 16, 0), seed=2)
    print("Transient nach MSM:")
    make_transient_run("TEST-C", 9.5, datetime(2026, 11, 12, 17, 0), seed=3)
    print("Linearer Transient (Filter testen):")
    make_linear_transient("TEST-D", datetime(2026, 11, 12, 18, 0), seed=4)
    print(f"\nFertig. Auswerten → Ordner {OUT} → Reiter ΔVth, I_krit 50 nA.")
