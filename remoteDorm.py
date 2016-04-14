import serial
import time
ser = serial.Serial('/dev/rfcomm0', 9600, timeout=0)
while True:
    var = str(input("Enter something: "))
    ser.write(var.encode())
