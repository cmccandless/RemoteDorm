#!/usr/bin/python

import serial
import time
ser = serial.Serial('/dev/rfcomm0', 9600, timeout=0)
while True:
    ser.write(str(input("Enter something: ")).encode())
