"""Messdaten: Empfang (Parser), Umrechnung, Speichern/Laden (.h5), ΔVth-Abgleich.

Datenformat:  Software/py/Datenformat_Rueckgabe.md
    #HDR TYPE=… N=… RANGE=… AVG=… DT_US=… DT_MIN_US=… LOG_Q24=… T_START_US=…
         T_STOP_US=… CYCLE=… T_STRESS_MS=…\\r\\n
    <N × uint16 little endian>
    #END SUM=<Summe mod 65536>[ #DONE]\\r\\n
Vth-Methode:  Auswertung_Vth.md (Konstantstrom, log-Interpolation)
"""

import math
import struct
from datetime import datetime
from pathlib import Path

HEADER_FIELDS = ("N", "RANGE", "AVG", "DT_US", "DT_MIN_US", "LOG_Q24",
                 "T_START_US", "T_STOP_US", "CYCLE", "T_STRESS_MS")
TYPES = ("IDVG", "TRANSIENT", "SPOT", "MSM_IDVG", "MSM_TRANSIENT")

# ---------------------------------------------------------------------------
# Rohwert -> Strom   (VORLÄUFIG, mit Referenzstrom prüfen!)
#   U_ADC = raw · VREF / 65536                      (ADS8866, unipolar)
#   U_ADC = I · Rf · STAGE_GAIN   ->  I = U_ADC / (Rf · STAGE_GAIN)
#   Werte aus firmware/FETCH_V02_2/ADS8866.c (VREF, RF_100N, RF_10U, STAGE_GAIN)
# ---------------------------------------------------------------------------
VREF = 2.5
STAGE_GAIN = 10.0 / 30.0
RF = {0: 10.0e6, 1: 100.0e3}          # RANGE 0 = 100 nA, 1 = 10 µA


def raw_to_current(raw, sense_range):
    """Liste Rohwerte -> Liste Ströme in A."""
    k = VREF / 65536.0 / (RF[int(sense_range)] * STAGE_GAIN)
    return [r * k for r in raw]


# ---------------------------------------------------------------------------
# Empfang
# ---------------------------------------------------------------------------
class BlockParser:
    """Zerlegt den UART-Bytestrom in Textzeilen und Datenblöcke.

    feed(bytes) gibt eine Liste von Ereignissen zurück:
        ("LINE", text)          normale Textzeile (Echo, FETCH READY …)
        ("BLOCK", hdr, raw)     vollständiger, geprüfter Datenblock
        ("DONE", None)          #DONE empfangen
        ("ERROR", text)         fehlerhafter Block (verworfen)
    """

    def __init__(self):
        self._buf = bytearray()
        self._state = "TEXT"
        self._hdr = None
        self._need = 0

    def feed(self, data):
        self._buf += data
        events = []
        while True:
            if self._state == "BIN":
                if len(self._buf) < self._need:
                    break
                payload = bytes(self._buf[:self._need])
                del self._buf[:self._need]
                n = self._hdr["N"]
                self._raw = list(struct.unpack(f"<{n}H", payload)) if n else []
                self._state = "END"
                continue

            pos = self._buf.find(b"\n")
            if pos < 0:
                break
            line = bytes(self._buf[:pos]).decode("ascii", errors="replace").strip()
            del self._buf[:pos + 1]

            if self._state == "END":
                self._state = "TEXT"
                events += self._finish_block(line)
                continue
            if not line:
                continue
            if line.startswith("#HDR"):
                try:
                    self._hdr = parse_header(line)
                except ValueError as exc:
                    events.append(("ERROR", f"Header unlesbar: {exc} ({line})"))
                    continue
                self._need = 2 * self._hdr["N"]
                self._state = "BIN"
            elif line.startswith("#DONE"):
                events.append(("DONE", None))
            else:
                events.append(("LINE", line))
        return events

    def _finish_block(self, line):
        hdr, raw = self._hdr, self._raw
        self._hdr = self._raw = None
        if not line.startswith("#END"):
            return [("ERROR", f"{hdr['TYPE']}: Endzeile fehlt (Bytes verloren?), "
                              f"Block verworfen. Empfangen: {line[:40]!r}")]
        try:
            sum_token = next(t for t in line.split() if t.startswith("SUM="))
            expected = int(sum_token[4:])
        except (StopIteration, ValueError):
            return [("ERROR", f"{hdr['TYPE']}: Endzeile unlesbar: {line!r}")]
        actual = sum(raw) & 0xFFFF
        events = []
        if actual != expected:
            events.append(("ERROR", f"{hdr['TYPE']} c{hdr['CYCLE']:02d}: Prüfsumme falsch "
                                    f"({actual} statt {expected}), Block verworfen."))
        else:
            events.append(("BLOCK", hdr, raw))
        if "#DONE" in line:
            events.append(("DONE", None))
        return events


def parse_header(line):
    hdr = {}
    for part in line.split()[1:]:
        name, _, value = part.partition("=")
        hdr[name] = value if name == "TYPE" else int(value)
    if hdr.get("TYPE") not in TYPES:
        raise ValueError(f"unbekannter TYPE {hdr.get('TYPE')!r}")
    for name in HEADER_FIELDS:
        hdr.setdefault(name, 0)
    return hdr


def time_axis_us(hdr):
    """Zeitachse in µs (Datenformat Kap. 5) oder None bei ID-VG."""
    n, typ = hdr["N"], hdr["TYPE"]
    if typ == "TRANSIENT":
        return [hdr["T_START_US"] + i * hdr["DT_US"] for i in range(n)]
    if typ == "MSM_TRANSIENT":
        t = [hdr["T_START_US"]]
        while len(t) < n:
            gap = max(hdr["DT_MIN_US"], (t[-1] * hdr["LOG_Q24"]) >> 24)
            t.append(t[-1] + gap)
        return t[:n]
    if typ == "SPOT":
        return [hdr["T_START_US"]] * n
    return None


def gate_axis(params, n):
    """VG-Achse für ID-VG aus den gesendeten Sweep-Parametern."""
    start = float(params["SOURce1_Sweep_Start"])
    stop = float(params["SOURce1_Sweep_Stop"])
    step = abs(float(params["SOURce1_Sweep_Step"]))
    if stop < start:
        step = -step
    return [start + i * step for i in range(n)]


def commands_to_params(commands):
    """['NAME= wert', …] -> {'NAME': 'wert'} (letzter Wert gewinnt)."""
    params = {}
    for cmd in commands:
        name, sep, value = cmd.partition("=")
        if sep:
            params[name.strip()] = value.strip()
    return params


# ---------------------------------------------------------------------------
# Speichern / Laden
# ---------------------------------------------------------------------------
def _h5py():
    try:
        import h5py
    except ImportError as exc:
        raise RuntimeError("h5py fehlt – im venv: pip install -r requirements.txt") from exc
    return h5py


def save_block(path, hdr, raw, ctx):
    """Einen Datenblock als eigene .h5-Datei speichern.

    ctx: Kontext vom Messstart (device, tab, start, run_id, params = gesendete Befehle)
    Aufbau:  /raw (uint16), /current (A), /x (VG in V oder t in s)
             Attribute: Header-Felder, device, tab, run_id, start, param_<Befehl>
    """
    h5py = _h5py()
    params = ctx.get("params", {})
    current = raw_to_current(raw, hdr["RANGE"] if "SENSE_RANGE" not in params
                             else int(params["SENSE_RANGE"]))
    if hdr["TYPE"] in ("IDVG", "MSM_IDVG") and "SOURce1_Sweep_Start" in params:
        x, x_name, x_unit = gate_axis(params, hdr["N"]), "VG", "V"
    else:
        t = time_axis_us(hdr)
        x, x_name, x_unit = ([v * 1e-6 for v in t] if t else list(range(hdr["N"]))), "t", "s"

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(path, "w") as f:
        f.create_dataset("raw", data=raw, dtype="uint16")
        d = f.create_dataset("current", data=current, dtype="float64")
        d.attrs["unit"] = "A"
        d = f.create_dataset("x", data=x, dtype="float64")
        d.attrs["name"] = x_name
        d.attrs["unit"] = x_unit
        a = f.attrs
        a["format"] = "FETCH-1"
        a["TYPE"] = hdr["TYPE"]
        for name in HEADER_FIELDS:
            a[name] = int(hdr[name])
        a["device"] = ctx.get("device", "")
        a["tab"] = ctx.get("tab", "")
        a["run_id"] = ctx.get("run_id", "")
        a["start"] = ctx.get("start", datetime.now()).isoformat(timespec="seconds")
        a["saved"] = datetime.now().isoformat(timespec="seconds")
        a["raw_to_current"] = f"I = raw*{VREF}/65536/(Rf*{STAGE_GAIN:.6g}), Rf={RF}"
        for name, value in params.items():
            a[f"param_{name}"] = str(value)
    return path


def load_file(path):
    """.h5 einlesen -> dict(attrs, params, x, x_name, x_unit, current, raw)."""
    h5py = _h5py()
    with h5py.File(path, "r") as f:
        attrs = {k: _plain(v) for k, v in f.attrs.items()}
        out = {
            "path": Path(path),
            "attrs": attrs,
            "params": {k[6:]: v for k, v in attrs.items() if k.startswith("param_")},
            "x": [float(v) for v in f["x"][()]],
            "x_name": _plain(f["x"].attrs.get("name", "x")),
            "x_unit": _plain(f["x"].attrs.get("unit", "")),
            "current": [float(v) for v in f["current"][()]],
            "raw": [int(v) for v in f["raw"][()]],
        }
    return out


def read_attrs(path):
    h5py = _h5py()
    with h5py.File(path, "r") as f:
        return {k: _plain(v) for k, v in f.attrs.items()}


def _plain(v):
    if isinstance(v, bytes):
        return v.decode("utf-8", errors="replace")
    if hasattr(v, "item"):
        return v.item()
    return v


# ---------------------------------------------------------------------------
# Vth (Konstantstrom) und ΔVth eines MSM-Laufs
# ---------------------------------------------------------------------------
def vth_constant_current(vg, current, i_krit):
    """Vth = VG bei I = i_krit, lineare Interpolation in log(I).
    None, wenn i_krit nicht erreicht wird."""
    pts = sorted(zip(vg, current))
    for (v1, i1), (v2, i2) in zip(pts, pts[1:]):
        if i1 < i_krit <= i2:
            if i1 > 0:
                frac = (math.log(i_krit) - math.log(i1)) / (math.log(i2) - math.log(i1))
            else:
                frac = (i_krit - i1) / (i2 - i1)      # Rauschen um 0: linear
            return v1 + frac * (v2 - v1)
    return None


def find_run(path):
    """Alle Dateien desselben Laufs (gleiche run_id im selben Ordner), nach Zyklus sortiert."""
    path = Path(path)
    run_id = read_attrs(path).get("run_id", "")
    if not run_id:
        return [path]
    files = []
    for p in path.parent.glob("*.h5"):
        try:
            a = read_attrs(p)
        except OSError:
            continue
        if a.get("run_id") == run_id:
            files.append((int(a.get("CYCLE", 0)), p))
    return [p for _, p in sorted(files)]


def analyse_run(path, i_krit):
    """ΔVth je Zyklus eines MSM-IDVG-Laufs (Referenz = c00 desselben Laufs).

    Rückgabe dict: files, device, stress, cycles=[{cycle, t_stress_ms, vth, dvth}],
                   max (Eintrag mit größtem |ΔVth|), warnings, params, error
    """
    res = {"path": Path(path), "cycles": [], "warnings": [], "error": None, "max": None}
    files = find_run(path)
    first = load_file(files[0])
    a, params = first["attrs"], first["params"]
    res.update(device=a.get("device", ""), params=params, files=files,
               stress=f"{params.get('STRESS_TYPE', '?')} {params.get('STRESS_VOLTage', '?')} V")
    if a.get("TYPE") != "MSM_IDVG":
        res["error"] = (f"ΔVth geht nur mit ID-VG-Kurven (MSM mit Messart IDVG); "
                        f"diese Datei ist {a.get('TYPE')}.")
        return res

    vth_ref = None
    for p in files:
        d = load_file(p)
        cyc = int(d["attrs"].get("CYCLE", 0))
        vth = vth_constant_current(d["x"], d["current"], i_krit)
        if vth is None:
            res["warnings"].append(f"c{cyc:02d}: I_krit = {i_krit*1e9:g} nA nicht erreicht.")
        if cyc == 0:
            vth_ref = vth
        res["cycles"].append({"cycle": cyc, "t_stress_ms": int(d["attrs"].get("T_STRESS_MS", 0)),
                              "vth": vth, "dvth": None})
    if not res["cycles"] or res["cycles"][0]["cycle"] != 0:
        res["error"] = "Referenzmessung c00 fehlt (MSM_INITIAL_MEASURE= TRUE nötig)."
        return res
    if vth_ref is None:
        res["error"] = "Vth der Referenz c00 nicht bestimmbar (I_krit nicht erreicht)."
        return res
    for c in res["cycles"]:
        if c["vth"] is not None:
            c["dvth"] = c["vth"] - vth_ref
    valid = [c for c in res["cycles"] if c["dvth"] is not None and c["cycle"] > 0]
    if valid:
        res["max"] = max(valid, key=lambda c: abs(c["dvth"]))
    else:
        res["error"] = "Kein Zyklus nach dem Stress auswertbar."
    return res


def _fmt_ts(ms):
    s = ms / 1000
    return f"{s:g} s" if s < 120 else f"{s/60:.1f} min" if s < 7200 else f"{s/3600:.2f} h"


COMPARE_KEYS = (("STRESS_TYPE", "Stress-Typ"), ("STRESS_VOLTage", "Gate-Stress"),
                ("STRESS_DRAIN_VOLTage", "Drain-Stress"), ("SENSE_RANGE", "Strombereich"),
                ("SENSE_MODE_AVERAGE", "Mittelungen"), ("SOURce2_VOLTage", "Lese-Drain"),
                ("SOURce1_Sweep_Step", "Sweep-Schritt"), ("MSM_START_TIME", "Startzeit"),
                ("MSM_TIME_FACTOR", "Zeitfaktor"))


def compare_text(meas, ref, i_krit):
    """Text für den Abgleich max ΔVth Messung vs. Referenz."""
    lines = [f"Methode: Konstantstrom, I_krit = {i_krit*1e9:g} nA", ""]
    for label, r in (("Messung", meas), ("Referenz", ref)):
        lines.append(f"{label}: {r['path'].name}")
        lines.append(f"  Device {r.get('device') or '–'} · {r.get('stress', '')} · "
                     f"{len(r['cycles'])} Dateien")
        if r["error"]:
            lines.append(f"  ✗ {r['error']}")
        elif r["max"]:
            m = r["max"]
            lines.append(f"  max ΔVth = {m['dvth']*1e3:+.1f} mV  (c{m['cycle']:02d}, "
                         f"Stress gesamt {_fmt_ts(m['t_stress_ms'])})")
        lines += [f"  ! {w}" for w in r["warnings"]]
        lines.append("")

    if meas["max"] and ref["max"] and not meas["error"] and not ref["error"]:
        dm, dr = meas["max"]["dvth"], ref["max"]["dvth"]
        diff = (dm - dr) * 1e3
        rel = f" ({(dm / dr - 1) * 100:+.1f} %)" if dr else ""
        lines.append(f"Differenz Messung − Referenz: {diff:+.1f} mV{rel}")
        lines.append("")
        # gleiche Bedingungen?
        diffs = [f"{name}: {meas['params'].get(k, '–')} ↔ {ref['params'].get(k, '–')}"
                 for k, name in COMPARE_KEYS
                 if meas["params"].get(k) != ref["params"].get(k)]
        if meas["max"]["t_stress_ms"] != ref["max"]["t_stress_ms"]:
            diffs.append(f"Stresszeit beim Maximum: {_fmt_ts(meas['max']['t_stress_ms'])} ↔ "
                         f"{_fmt_ts(ref['max']['t_stress_ms'])}")
        if diffs:
            lines.append("Achtung, unterschiedliche Bedingungen:")
            lines += [f"  · {d}" for d in diffs]
            lines.append("")
        # Zyklen nebeneinander
        lines.append("Zyklus  Stress gesamt     ΔVth Messung   ΔVth Referenz")
        ref_by = {c["cycle"]: c for c in ref["cycles"]}
        for c in meas["cycles"]:
            r = ref_by.get(c["cycle"])
            fm = f"{c['dvth']*1e3:+8.1f} mV" if c["dvth"] is not None else "       –   "
            fr = f"{r['dvth']*1e3:+8.1f} mV" if r and r["dvth"] is not None else "       –   "
            lines.append(f"c{c['cycle']:02d}     {_fmt_ts(c['t_stress_ms']):>12}   {fm}    {fr}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Daten für die Anzeige (ohne matplotlib, damit testbar)
# ---------------------------------------------------------------------------
RANGE_TEXT = {0: "100 nA", 1: "10 µA"}


def view_single(path, overlay_run, i_krit):
    """Kurven einer Datei bzw. des ganzen Laufs.

    Rückgabe dict: title, xlabel, xlog, ylabel, series=[{label, x, y}] (y in nA),
                   vth (V oder None), i_krit_nA, info (Text)
    """
    d = load_file(path)
    a, params = d["attrs"], d["params"]
    typ = a.get("TYPE", "?")
    files = find_run(path) if overlay_run else [Path(path)]
    idvg = typ in ("IDVG", "MSM_IDVG")
    out = {"title": Path(path).name, "series": [], "vth": None, "i_krit_nA": None,
           "ylabel": "|I_D| (nA)", "xlog": False}

    if typ == "SPOT" and len(files) > 1:
        # SPOT-Lauf: ein Punkt pro Zyklus -> I über gesamte Stresszeit
        xs, ys = [], []
        for p in files:
            q = load_file(p)
            ts = int(q["attrs"].get("T_STRESS_MS", 0)) / 1000
            if ts > 0 and q["current"]:
                xs.append(ts)
                ys.append(abs(q["current"][0]) * 1e9)
        out.update(xlabel="Stresszeit gesamt (s)", xlog=True,
                   series=[{"label": "SPOT", "x": xs, "y": ys, "marker": "o"}])
    else:
        for p in files:
            q = d if Path(p) == Path(path) else load_file(p)
            cyc = int(q["attrs"].get("CYCLE", 0))
            label = f"c{cyc:02d}" if q["attrs"].get("tab") == "MSM" or typ.startswith("MSM") \
                else Path(p).stem
            out["series"].append({"label": label, "x": q["x"],
                                  "y": [abs(i) * 1e9 for i in q["current"]],
                                  "marker": "." if idvg or len(q["x"]) < 50 else ""})
        out["xlabel"] = "V_G (V)" if idvg else "t (s)"
        out["xlog"] = typ == "MSM_TRANSIENT"

    if idvg and not overlay_run:
        out["vth"] = vth_constant_current(d["x"], d["current"], i_krit)
        out["i_krit_nA"] = i_krit * 1e9

    rng = int(params.get("SENSE_RANGE", a.get("RANGE", 0)))
    parts = [typ, f"Device {a.get('device') or '–'}", f"N = {a.get('N')}",
             f"Bereich {RANGE_TEXT.get(rng, rng)}", f"AVG {params.get('SENSE_MODE_AVERAGE', a.get('AVG'))}"]
    if typ.startswith("MSM") or a.get("tab") == "MSM":
        parts.append(f"c{int(a.get('CYCLE', 0)):02d}, Stress gesamt {_fmt_ts(int(a.get('T_STRESS_MS', 0)))}")
    if "STRESS_TYPE" in params and a.get("tab") in ("Stress", "MSM"):
        parts.append(f"{params['STRESS_TYPE']} {params.get('STRESS_VOLTage', '?')} V")
    if idvg:
        parts.append(f"V_D = {params.get('SOURce2_VOLTage', '?')} V")
    elif "SOURce1_VOLTage" in params:
        parts.append(f"V_G = {params['SOURce1_VOLTage']} V, V_D = {params.get('SOURce2_VOLTage', '?')} V")
    if out["vth"] is not None:
        parts.append(f"Vth({i_krit*1e9:g} nA) = {out['vth']:.4f} V")
    elif idvg and not overlay_run:
        parts.append(f"Vth: I_krit {i_krit*1e9:g} nA nicht erreicht")
    if overlay_run:
        parts.append(f"{len(files)} Dateien im Lauf")
    parts.append(f"gestartet {a.get('start', '–')}")
    out["info"] = "  ·  ".join(parts)
    return out


def view_compare(meas, ref):
    """ΔVth (mV) über gesamte Stresszeit (s) für Messung und Referenz."""
    series = []
    for label, r in (("Messung", meas), ("Referenz", ref)):
        pts = [(c["t_stress_ms"] / 1000, c["dvth"] * 1e3) for c in r["cycles"]
               if c["dvth"] is not None and c["t_stress_ms"] > 0]
        if pts:
            series.append({"label": f"{label}: {r.get('device') or r['path'].name}",
                           "x": [p[0] for p in pts], "y": [p[1] for p in pts], "marker": "o"})
    return {"title": "ΔVth über Stresszeit", "xlabel": "Stresszeit gesamt (s)", "xlog": True,
            "ylabel": "ΔVth (mV)", "series": series, "vth": None, "i_krit_nA": None}


def view_multi(paths, overlay_run, i_krit):
    """Mehrere ausgewählte Dateien überlagern. Dateien mit anderer x-Achse als die
    erste werden übersprungen (z. B. ID-VG und Transient gemischt)."""
    first = view_single(paths[0], overlay_run, i_krit)
    out = dict(first, series=[], vth=None, i_krit_nA=None,
               title=f"{len(paths)} Dateien überlagert")
    skipped = []
    for p in paths:
        v = first if p == paths[0] else view_single(p, overlay_run, i_krit)
        if v["xlabel"] != first["xlabel"]:
            skipped.append(Path(p).name)
            continue
        stem = Path(p).stem
        for s in v["series"]:
            label = s["label"] if s["label"] == stem else f"{stem} {s['label']}"
            out["series"].append(dict(s, label=label))
    out["info"] = f"{len(paths) - len(skipped)} Dateien überlagert"
    if skipped:
        out["info"] += f"  ·  übersprungen (andere x-Achse): {', '.join(skipped)}"
    return out
