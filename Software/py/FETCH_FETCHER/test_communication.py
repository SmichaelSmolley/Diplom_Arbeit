
from instrument import Instrument

print("TESTDATEI WURDE GESTARTET")

class FakeSerial:

    def __init__(self):
        self.last_command = ""

    def write(self, data):
        self.last_command = data.decode().strip()
        print("Messgerät empfängt:", self.last_command)

    def readline(self):
        if self.last_command == "*IDN?":
            response = "RTN-Tester,Version1.0"

        elif self.last_command == ":SENSE1:CURRENT?":
            response = "0.00000125"

        elif self.last_command == ":SYSTEM:VERSION?":
            response = "1.2.0"

        else:
            response = "ERROR: Unbekannter Befehl"

        print("Messgerät sendet:", response)
        return (response + "\n").encode()


instrument = Instrument()

# Simulator als Verbindung einsetzen
instrument.connection = FakeSerial()
instrument.connected = True

instrument.set_voltage(1, 1.2)
instrument.set_output(1, True)
instrument.set_output(1, False)

# Drei verschiedene Anfragen testen
for command in ["*IDN?", ":SENSE1:CURRENT?", ":SYSTEM:VERSION?"]:
    print("\nNeue Anfrage:")
    response = instrument.query(command)
    print("Python empfängt:", response)
