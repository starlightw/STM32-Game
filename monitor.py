import serial
import io
import argparse

# read from serial port and print to console with format 8n1 baud 115200
def monitor(args):
    ser = serial.Serial(args.port, args.baudrate, timeout=1)
    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
    while True:
        line = sio.readline()
        if line:
            print(line.strip())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Monitor serial port output.')
    parser.add_argument('port', help='Serial port to monitor (e.g., COM3 or /dev/ttyUSB0)')
    parser.add_argument('baudrate', help='Baud rate for the serial port (e.g., 115200)', default=115200, type=int)
    args = parser.parse_args()
    monitor(args)