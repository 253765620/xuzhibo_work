#!coding:utf-8
import wiringpi
import time

wiringpi.wiringPiSetup()
wiringpi.pinMode(8,3)
#wiringpi.digitalWrite(8,1)
#wiringpi.pinMode(29,1)
#wiringpi.digitalWrite(29,0)
time.sleep(1)
