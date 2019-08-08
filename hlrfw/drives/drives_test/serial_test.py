#!coding:utf8
import serial
'''
#USB
ser = serial.Serial('/dev/ttyUSB0',baudrate=115200,timeout=0.1)
ser.write('hello'.encode())
msg = ser.readline().decode()
print(msg)
'''
#mini
ser = serial.Serial('/dev/ttyAMA0',baudrate=115200,timeout=0.1)
ser.write('hello'.encode())
msg = ser.readline().decode()
print(msg)