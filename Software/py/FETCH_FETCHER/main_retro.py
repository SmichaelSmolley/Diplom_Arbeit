"""Startet das Programm im hellen Design (Stil einer Qt-Messsoftware, qt_light.json)."""
from gui import App


if __name__ == "__main__":
    app = App(retro=True)
    app.mainloop()
