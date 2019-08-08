#! coding:utf8

#can test
import os
import can
import wiringpi
import time
'''
#enable can
wiringpi.wiringPiSetup()
wiringpi.pinMode(5,1)
wiringpi.digitalWrite(5,1)
time.sleep(1)
wiringpi.pinMode(22,1)
wiringpi.digitalWrite(22,1)
time.sleep(1)
os.system('sudo sh /home/pi/can-start.sh')
time.sleep(1)
os.system('sudo sh /home/pi/can-start.sh')
print('open can0 and can1')
print("please start exe 'candump can0 can1' ")
time.sleep(5)
'''
#send can msg
bus_can0 = can.interface.Bus(channel='can0', bustype='socketcan')
bus_can1 = can.interface.Bus(channel='can1', bustype='socketcan')
msg = can.Message(arbitration_id=0x7f,
                data=[11, 25, 11, 1, 1, 2, 23, 18], 
                extended_id=False)
print('can0 send msg')
bus_can0.send(msg)
#time.sleep(1)
#print('can1 send msg')
#bus_can1.send(msg)



