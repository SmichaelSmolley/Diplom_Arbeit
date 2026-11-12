"""Vorverarbeitung für die Anzeige: Zeitbereich, Medianfilter, digitaler Tiefpass.

Reihenfolge: Zeitbereich -> Medianfilter -> Tiefpass.
Die gespeicherten .h5-Dateien werden NICHT verändert, nur die Anzeige.
"""

import numpy as np


def crop(x, y, start_pct, end_pct, xlog=False):
    """Nur den Bereich start_pct … end_pct (0–100 %) der x-Achse behalten.
    Bei log-Achse in Dekaden gerechnet (10 % = erstes Zehntel der Dekaden)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 2 or (start_pct <= 0 and end_pct >= 100):
        return x, y
    lo, hi = sorted((start_pct, end_pct))
    if xlog and np.all(x > 0):
        u = np.log10(x)
    else:
        u = x
    u0, u1 = u.min(), u.max()
    a, b = u0 + (u1 - u0) * lo / 100, u0 + (u1 - u0) * hi / 100
    keep = (u >= a) & (u <= b)
    return x[keep], y[keep]


def median(y, width):
    """Gleitender Median über 'width' Punkte (ungerade), Ränder mit Randwert aufgefüllt."""
    y = np.asarray(y, float)
    width = int(width) | 1
    if width < 3 or len(y) < width:
        return y
    half = width // 2
    padded = np.pad(y, half, mode="edge")
    windows = np.lib.stride_tricks.sliding_window_view(padded, width)
    return np.median(windows, axis=1)


def uniform_fs(x, tol=0.01):
    """Abtastrate in Hz, wenn die Zeitachse gleichmäßig ist (±1 %), sonst None."""
    x = np.asarray(x, float)
    if len(x) < 3:
        return None
    dx = np.diff(x)
    if np.any(dx <= 0):
        return None
    mean = dx.mean()
    if (dx.max() - dx.min()) / mean > tol:
        return None
    return 1.0 / mean


def lowpass(y, fs, fc, kind="Bessel", order=4, zero_phase=True):
    """IIR-Tiefpass (scipy.signal, SOS-Form). Gibt (y_gefiltert, Hinweis) zurück."""
    try:
        from scipy import signal
    except ImportError:
        return y, "Tiefpass: scipy fehlt (pip install -r requirements.txt)"
    y = np.asarray(y, float)
    nyq = fs / 2
    if fc >= nyq:
        return y, f"Tiefpass: f_g = {fc:.3g} Hz ≥ f_s/2 = {nyq:.3g} Hz – nicht gefiltert"
    order = int(round(order))
    if kind == "Butterworth":
        sos = signal.butter(order, fc, btype="low", fs=fs, output="sos")
    else:
        # norm="mag": −3 dB genau bei f_g (wie bei Butterworth vergleichbar)
        sos = signal.bessel(order, fc, btype="low", fs=fs, output="sos", norm="mag")
    if zero_phase:
        try:
            return signal.sosfiltfilt(sos, y), None
        except ValueError:            # zu wenige Punkte für die Randauffüllung
            return signal.sosfiltfilt(sos, y, padlen=len(y) - 1), None
    return signal.sosfilt(sos, y), None


def apply(x, y, cfg, is_time, xlog):
    """cfg: dict t_start, t_end (%), med_on, med_w, lp_on, fc, kind, order, zero_phase.
    Gibt (x, y_roh, y_gefiltert oder None, [Hinweise]) zurück."""
    notes = []
    x, y = crop(x, y, cfg["t_start"], cfg["t_end"], xlog)
    filtered = None
    if cfg["med_on"] and len(y) >= 3:
        filtered = median(y, cfg["med_w"])
    if cfg["lp_on"]:
        if not is_time:
            notes.append("Tiefpass nur bei Zeitsignalen (nicht bei ID-VG)")
        else:
            fs = uniform_fs(x)
            if fs is None:
                notes.append("Tiefpass übersprungen: Zeitachse nicht gleichmäßig (log. Abstände)")
            elif len(y) < 4:
                notes.append("Tiefpass: zu wenige Punkte")
            else:
                out, note = lowpass(filtered if filtered is not None else y, fs,
                                    cfg["fc"], cfg["kind"], cfg["order"], cfg["zero_phase"])
                if note:
                    notes.append(note)        # nicht gefiltert -> nichts vortäuschen
                else:
                    filtered = out
    return x, y, filtered, notes
