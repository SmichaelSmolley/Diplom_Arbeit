import serial
from ADC_class import SourceADCConfig

test_adc = SourceADCConfig()

def serial_init(port, baudrate):
    return serial.Serial(port, baudrate, timeout=1)  # 1 Sekunde timeout

def serial_send(ser, data):
    """Send data over the serial port."""
    ser.write(data.encode())
    ser.flush()

def serial_receive(ser, size=1024):
    """Receive data from the serial port."""
    data = ser.read(size)
    return data.decode()

def serial_close(ser):
    """Close the serial port."""
    ser.close()

# Example usage:
# ser = serial_init('/dev/ttyUSB0', 9600)
# serial_send(ser, 'Hello, uC!')
# ser = serial_init('/dev/ttyUSB0', 9600)
# data = serial_receive(ser, 100)
# print("Received:", data)
# serial_close(ser)



ser = serial_init('COM8', 9600)
serial_send(ser, 'Hello, uC!')
data = serial_receive(ser, 100)
print("Received:", data)
serial_close(ser)

print("ADC Config Internal Ref:", test_adc.internal_ref)
print("ADC Config Sample Rate:", test_adc.sample_rate)
print("ADC Config Input Range:", test_adc.input_range_setting)
