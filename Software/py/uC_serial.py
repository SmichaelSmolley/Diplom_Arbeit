import serial

def serial_init(port, baudrate):
    """Initialize the serial port with the given baudrate."""
    ser = serial.Serial(port, baudrate)
    return ser

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

ser = serial_init('/dev/ttyUSB0', 9600)
serial_send(ser, 'Hello, uC!')
data = serial_receive(ser, 100)
print("Received:", data)
serial_close(ser)
