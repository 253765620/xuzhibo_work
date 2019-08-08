#!coding:utf8
import wiringpi
import time

#init
wiringpi.wiringPiSetup()
wiringpi.pcf8574Setup(101, 0x23)

'''
#enable
wiringpi.pinMode(101,1)
wiringpi.digitalWrite(101,1)
time.sleep(1)
wiringpi.pinMode(103,1)
wiringpi.digitalWrite(103,1)
time.sleep(1)
wiringpi.pinMode(105,1)
wiringpi.digitalWrite(105,1)
time.sleep(1)
wiringpi.pinMode(107,1)
wiringpi.digitalWrite(107,1)

'''
#disable
wiringpi.pinMode(101,1)
wiringpi.digitalWrite(101,0)
time.sleep(1)
wiringpi.pinMode(102,1)
wiringpi.digitalWrite(102,0)
time.sleep(1)
wiringpi.pinMode(103,1)
wiringpi.digitalWrite(103,0)
time.sleep(1)
wiringpi.pinMode(104,1)
wiringpi.digitalWrite(104,0)
time.sleep(1)
wiringpi.pinMode(105,1)
wiringpi.digitalWrite(105,0)
time.sleep(1)
wiringpi.pinMode(106,1)
wiringpi.digitalWrite(106,0)
time.sleep(1)
#time.sleep(1)
wiringpi.pinMode(108,1)
wiringpi.digitalWrite(108,0)
