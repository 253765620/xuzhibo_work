#!coding: utf-8
import time
import wiringpi
from hlrfw.configs.io_config import PCF8574_START_ADDR

# 初始化
try:
    wiringpi.wiringPiSetup()
    wiringpi.pcf8574Setup(PCF8574_START_ADDR, 0x23)
    wiringpi.pinMode(26,1)
    wiringpi.digitalWrite(26,1)
except:
    print('init failed')
    

class Pcf8574(object):
    def enable_pin(self, pin):
        '''
        pin is a integer between 0 and 7
        '''
        pin_act = PCF8574_START_ADDR + pin - 1
        #print(pin_act)
        self._set_pin_mode_out(pin_act)
        wiringpi.digitalWrite(pin_act,1)

    def disable_pin(self, pin):
        '''
        pin is a integer between 0 and 7
        '''
        pin_act = PCF8574_START_ADDR + pin - 1
        self._set_pin_mode_out(pin_act)
        wiringpi.digitalWrite(pin_act,0)
        
    def _set_pin_mode_out(self, pin):
        '''
        - 设置对应引脚的模式为输出
        '''
        wiringpi.pinMode(pin,1)
     