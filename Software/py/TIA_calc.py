import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Button
import h5py
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

# === Startwerte =========================================================
Rf0 = 10e3      # Ω
Cf0 = 4e-12     # F
Rin0 = 1e3     # Ω
Cin0 = 10e-12   # F
GBW0 = 2.5e6    # Hz

# Frequenzachse
f = np.logspace(-2, 12, 4000)
w = 2 * np.pi * f
s = 1j * w

# === Kernfunktionen =====================================================
def tia_response(Rf, Cf, Rin, Cin, GBW):
    Zf = Rf / (1 + s * Rf * Cf)
    Zin = Rin / (1 + s * Rin * Cin)
    A_tia = -Zf / Zin
    NG = 1 + Zf / Zin
    A_ol = GBW / f
    return A_tia, NG, A_ol, Zf, Zin

def tia_transfer(Rf, Cf, Rin, Cin, GBW):
    Zf = Rf / (1 + s * Rf * Cf)
    Zin = Rin / (1 + s * Rin * Cin)
    A_OL = GBW / f
    H = -(A_OL * Zf * Zin) / ((A_OL + 1) * Zin + Zf)
    return H

def compute_phase_margin(NG, A_ol, NG_phase, f):
    NG_mag = np.abs(NG)
    A_ol_mag = A_ol
    idx = np.argmin(np.abs(A_ol_mag - NG_mag))
    f_cross = f[idx]
    # Phasenreserve = 180 + (Phase des Open Loop - Phase des Noise Gain)
    phase_margin = 180 + NG_phase[idx]
    return f_cross, phase_margin

# === Initialberechnung ==================================================
A_tia, NG, A_ol, Zf, Zin = tia_response(Rf0, Cf0, Rin0, Cin0, GBW0)
H = tia_transfer(Rf0, Cf0, Rin0, Cin0, GBW0)
A_tia_mag = 20*np.log10(np.abs(A_tia))
NG_mag = 20*np.log10(np.abs(NG))
A_ol_mag = 20*np.log10(A_ol)
A_tia_phase = np.unwrap(np.angle(A_tia, deg=True))
H_mag = 20*np.log10(np.abs(H))

fz = 1 / (2*np.pi*Rf0*(Cf0 + Cin0))
fp = 1 / (2*np.pi*Rf0*Cf0)
f_cross, phase_margin = compute_phase_margin(NG, A_ol, A_tia_phase, f)

# === Layout =============================================================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [2.5, 1]})
plt.subplots_adjust(left=0.35, bottom=0.25, hspace=0.35)

# 1. Amplitude
l_tia, = ax1.semilogx(f, A_tia_mag, label='|A_TIA| [dB]', color='tab:blue')
l_ng,  = ax1.semilogx(f, NG_mag, label='|Noise Gain| [dB]', color='tab:green')
l_ol,  = ax1.semilogx(f, A_ol_mag, '--', label='|Open Loop Gain| [dB]', color='tab:red')
l_hmag, = ax1.semilogx(f, H_mag, color='tab:purple', label='|Vout/Iin| [dBΩ]')
v_fz = ax1.axvline(fz, color='orange', linestyle=':', label=f"Zero fz={fz/1e6:.2f} MHz")
v_fp = ax1.axvline(fp, color='purple', linestyle=':', label=f"Pole fp={fp/1e6:.2f} MHz")
v_fc = ax1.axvline(f_cross, color='gray', linestyle='--', label=f"f_cross={f_cross/1e6:.2f} MHz")

ax1.set_ylabel("Amplitude [dB]")
ax1.set_title("TIA Bode-Diagramm")
ax1.grid(True, which='both', ls='--', alpha=0.6)
ax1.legend(loc='best')
ax1.set_yticks(np.arange(-100, 101, 20))

# 2. Phase
l_phase, = ax2.semilogx(f, A_tia_phase, color='tab:orange')
ax2.set_xlabel("Frequenz [Hz]")
ax2.set_ylabel("Phase [°]")
ax2.grid(True, which='both', ls='--', alpha=0.6)

# === Eingabefelder links ===============================================
boxes = {
    "Rf": plt.axes([0.05, 0.70, 0.20, 0.04]),
    "Cf": plt.axes([0.05, 0.64, 0.20, 0.04]),
    "Rin": plt.axes([0.05, 0.58, 0.20, 0.04]),
    "Cin": plt.axes([0.05, 0.52, 0.20, 0.04]),
    "GBW": plt.axes([0.05, 0.46, 0.20, 0.04]),
    "Name": plt.axes([0.05, 0.40, 0.20, 0.04]),
}
button_ax = plt.axes([0.05, 0.31, 0.20, 0.05])
save_ax = plt.axes([0.05, 0.24, 0.20, 0.05])
load_ax = plt.axes([0.05, 0.17, 0.20, 0.05])
info_ax = plt.axes([0.05, 0.08, 0.20, 0.07])

tbox_Rf = TextBox(boxes["Rf"], 'Rf [Ω]: ', initial=str(Rf0))
tbox_Cf = TextBox(boxes["Cf"], 'Cf [F]: ', initial=str(Cf0))
tbox_Rin = TextBox(boxes["Rin"], 'Rin [Ω]: ', initial=str(Rin0))
tbox_Cin = TextBox(boxes["Cin"], 'Cin [F]: ', initial=str(Cin0))
tbox_GBW = TextBox(boxes["GBW"], 'GBW [Hz]: ', initial=str(GBW0))
tbox_Name = TextBox(boxes["Name"], 'DATA-Prefix: ', initial="tia_data")
info_box = TextBox(info_ax, 'Ergebnisse:', initial="", label_pad=0.05)

button_update = Button(button_ax, 'Aktualisieren', color='lightblue', hovercolor='skyblue')
button_save = Button(save_ax, 'Speichern (.h5)', color='lightgreen', hovercolor='lime')
button_load = Button(load_ax, 'Laden (.h5)', color='lightyellow', hovercolor='khaki')

# === Funktionen =========================================================
def update(event=None):
    try:
        Rf = float(tbox_Rf.text)
        Cf = float(tbox_Cf.text)
        Rin = float(tbox_Rin.text)
        Cin = float(tbox_Cin.text)
        GBW = float(tbox_GBW.text)
    except ValueError:
        print("Ungültige Eingabe – bitte nur Zahlen eingeben.")
        return

    A_tia, NG, A_ol, Zf, Zin = tia_response(Rf, Cf, Rin, Cin, GBW)
    H = tia_transfer(Rf, Cf, Rin, Cin, GBW)

    A_tia_mag = 20*np.log10(np.abs(A_tia))
    NG_mag = 20*np.log10(np.abs(NG))
    A_ol_mag = 20*np.log10(A_ol)
    A_tia_phase = np.unwrap(np.angle(A_tia, deg=True))
    H_mag = 20*np.log10(np.abs(H))

    fz = 1 / (2*np.pi*Rf*(Cf + Cin))
    fp = 1 / (2*np.pi*Rf*Cf)
    f_cross, phase_margin = compute_phase_margin(NG, A_ol, A_tia_phase, f)

    l_tia.set_ydata(A_tia_mag)
    l_ng.set_ydata(NG_mag)
    l_ol.set_ydata(A_ol_mag)
    l_phase.set_ydata(A_tia_phase)
    l_hmag.set_ydata(H_mag)
    v_fz.set_xdata([fz, fz])
    v_fp.set_xdata([fp, fp])
    v_fc.set_xdata([f_cross, f_cross])

    result_text = (f"fz = {fz/1e6:.2f} MHz\n"
                   f"fp = {fp/1e6:.2f} MHz\n"
                   f"f_cross = {f_cross/1e6:.2f} MHz\n"
                   f"PM = {phase_margin:.1f}°")
    info_box.set_val(result_text)

    fig.canvas.draw_idle()

# === Events ==============================================================  
button_update.on_clicked(update)
for box in [tbox_Rf, tbox_Cf, tbox_Rin, tbox_Cin, tbox_GBW]:
    box.on_submit(update)

update()
plt.show()
