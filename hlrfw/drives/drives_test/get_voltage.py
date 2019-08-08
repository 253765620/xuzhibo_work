#!coding:utf8
import wiringpi
import time

wiringpi.wiringPiSetup()
wiringpi.pcf8591Setup(121, 0x48)

wiringpi.pinMode(7,1)
wiringpi.digitalWrite(7,1)

wiringpi.pinMode(0,1)
wiringpi.digitalWrite(0,1)
wiringpi.pinMode(2,1)
wiringpi.digitalWrite(2,1)
time.sleep(1)


for i in range(4):
    print(wiringpi.analogRead(121+i))
    time.sleep(1)
'''
print(wiringpi.analogRead(122))
'''