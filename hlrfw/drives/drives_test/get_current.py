#!coding:utf8
import wiringpi
import time
#init
wiringpi.wiringPiSetup()
wiringpi.pcf8591Setup(121, 0x48)

#GS1 gpio.1 GS0  gpio.4
wiringpi.pinMode(1,1)
wiringpi.digitalWrite(1,1)
wiringpi.pinMode(4,1)
wiringpi.digitalWrite(4,1)

#
current_sample = wiringpi.analogRead(122) - 1
print(current_sample)
current = current_sample*3.3/256*4/200*1000
print('current is {} mA'.format(current))
