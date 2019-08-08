#!coding: utf-8
import time
import wiringpi
import sys
if '/home/pi' not in sys.path:
    sys.path.append('/home/pi')
from hlrfw.configs.io_config import PCF8591_START_ADDR,PCF8591_CONSTANT,PCF8591_DEVIATION,INA255_CONSTANT,PCF8591_CURR_VOL_DEVIATION

# 初始化
wiringpi.wiringPiSetup()
wiringpi.pcf8591Setup(PCF8591_START_ADDR, 0x48)

class Ina225(object):
    '''
    - INA255自动切换量程
    - 输出的电压小于0.5, 或者等于3.3, 会调节量程
    '''
    gain_model_list = [
        (25,0,0),# 25 对应放大系数25, gpio4电平, gpio1电平, 0代表对应引脚电压置低
        (50,0,1),# 50
        (100,1,0),# 100
        (200,1,1),# 200
        ]
    def __init__(self):
        '''
        - 初始化参数, 放大系数50
        '''
        self.curr_list = []
        self.now_gain_model = 1
        wiringpi.pinMode(1,1)
        wiringpi.pinMode(4,1)
        wiringpi.digitalWrite(4,0)
        wiringpi.digitalWrite(1,1)

    def gain_model_choice(self, now_curr_vol):
        '''
        - 量程选择
        '''
        if now_curr_vol == 3.3 and self.now_gain_model != 0:
            self.now_gain_model = self.now_gain_model - 1
            self.change_gain_modle()
            return True
        if now_curr_vol < 0.5 and self.now_gain_model != 3:# 0.5 is not sure
            self.now_gain_model = self.now_gain_model + 1
            self.change_gain_modle()
            return True
        return False
    
    def change_gain_modle(self):
        '''
        - 量程对应的电平变化
        '''
        wiringpi.digitalWrite(4,self.gain_model_list[self.now_gain_model][1])
        wiringpi.digitalWrite(1,self.gain_model_list[self.now_gain_model][2])

class Pcf8591(Ina225):
    def __init__(self):
        super(Pcf8591, self).__init__()
        self.now_curr_vol = 0
        
    def read_pin(self, pin):
        '''
        - 读取电压
        '''
        pin_value = wiringpi.analogRead(pin+PCF8591_START_ADDR-1)
        # 如果读取到的值小于5，就忽略,需要更改
        if pin_value < 5:
            pin_value = 0
        pin_volt = pin_value*PCF8591_CONSTANT + PCF8591_DEVIATION
        return pin_volt
    
    def get_now_curr(self):
        while 1:
            self.get_now_curr_volt()
            if not self.gain_model_choice(self.now_curr_vol):
                return self.vol_to_curr()
    
    def get_now_curr_volt(self):
        '''
        - 获取根据电流输出的电压值
        '''
        self.now_curr_vol = self.read_pin(2)
    
    def vol_to_curr(self):
        '''
        - 根据电压值, 计算出对应的电流值
        '''
        #print()
        return self.now_curr_vol*INA255_CONSTANT/self.gain_model_list[self.now_gain_model][0]
