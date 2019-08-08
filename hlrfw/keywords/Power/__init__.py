# -*- coding: utf-8 -*-
'''
- 电源控制关键字
- 主要是电压的开关
- 电压大小调节和大小获取
- 电流的大小获取
'''
import sys
if '/home/pi' not in sys.path:
    sys.path.append('/home/pi')

from robot.api import logger
from robot.utils import asserts

from hlrfw.drives.pcf8574 import Pcf8574
from hlrfw.drives.pcf8591 import Pcf8591
from hlrfw.drives.ad5259 import Ad5259
from hlrfw.configs.io_config import PCF8574_MATCH_DICT,PCF8591_MATCH_DICT,RASPI_MATCH_DICT

class PinCheck(object):
    def match_pcf8574_pin_num(self, match_key):
        self.act_ant_num = PCF8574_MATCH_DICT.get(match_key)
        if not self.act_ant_num:
            asserts.fail('act_ant_num error !!!')
            
    def match_pcf8591_pin_num(self, match_key):
        act_volt_num = PCF8591_MATCH_DICT.get(str(match_key)+'_volt')
        if not act_volt_num:
            asserts.fail('act_volt_num error !!!')
        else:
            return act_volt_num
            
    def is_int_data(self, check_data):
        try:
            return int(check_data)
        except:
            asserts.fail('input data is not a integer')

class Power(PinCheck, Pcf8574, Pcf8591, Ad5259):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def power_ant_open(self, ant_obj, status='open'):
        '''
        功能:
        - 天线开路控制,默认天线连接
        
        参数:
        - ant_obj : gnss, wwan, ble, wifi,控制对应的天线
        - status : 输入'open' 天线开路,‘close’天线连接
        
        例子:
        | ant_open | open |
        '''
        self.match_pcf8574_pin_num(ant_obj+'_open')
        if status == 'open':
            self.enable_pin(self.act_ant_num)
            logger.info('ant open')
        else:
            self.disable_pin(self.act_ant_num)
            logger.info('ant connect')
        
    def power_ant_short(self, ant_obj, status='open'):
        '''
        功能:
        - 控制天线是否短接到地,默认不短
        
        参数:
        - ant_obj : gnss, wwan, ble, ,控制对应的天线
        - status : 输入'open' 天线短接到地,‘close’天线不短接到地
        
        例子:
        | ant_short | open |
        '''
        self.match_pcf8574_pin_num(ant_obj+'_short')
        if status == 'open':
            self.enable_pin(self.act_ant_num)
            logger.info('ant connect to earth')
        else:
            self.disable_pin(self.act_ant_num)
            logger.info('ant disconnect to earth')

    def power_volt_get(self, volt_obj):
        '''
        功能:
        - 获取对应的电压
        
        参数:
        - volt_obj : power, acc, out1
        
        例子:
        | get_volt | power |
        '''
        curr_volt = self.read_pin(self.match_pcf8591_pin_num(volt_obj))*11
        logger.info(curr_volt)
        return curr_volt
        
    def power_curr_get(self):
        '''
        功能:
        - 获取Power路的电流
        
        参数:
        无
        
        例子:
        | get_curr |
        '''
        now_curr = self.get_now_curr()*1000
        print('now current is: %.2fmA' % now_curr)
        return now_curr
        
    def power_volt_adjust(self, volt_adjust):
        '''
        功能:
        - 调节power, acc, out1的电压
        
        参数:
        - volt_adjust : 需要的电压(V)
        
        例子:
        | volt_adjust | 12 |
        '''
        self._adjust_volt_to(self.is_int_data(volt_adjust))
        
    def power_KL30_open(self):
        '''
        功能:
        - 打开KL30(power)
        
        例子:
        | open_KL30 |
        '''
        self._control_io(RASPI_MATCH_DICT['power'], 1)
    
    def power_KL15_open(self):
        '''
        功能:
        - 打开KL15(acc)
        
        例子:
        | open_KL15 |
        '''
        self._control_io(RASPI_MATCH_DICT['acc'], 1)
        
    def power_out_1_open(self):
        '''
        功能:
        - 打开out_1
        
        例子:
        | open_out_1 |
        '''
        self._control_io(RASPI_MATCH_DICT['out_1'], 1)
    
    def power_KL30_close(self):
        '''
        功能:
        - 关闭KL15
        
        例子:
        | close_power |
        '''
        self._control_io(RASPI_MATCH_DICT['power'], 0)
        
    def power_KL15_close(self):
        '''
        功能:
        - 关闭KL30
        
        例子:
        | close_acc |
        '''
        self._control_io(RASPI_MATCH_DICT['acc'], 0)
        
    def power_out_1_close(self):
        '''
        功能:
        - 关闭out_1
        
        例子:
        | close_out_1 |
        '''
        self._control_io(RASPI_MATCH_DICT['out_1'], 0)
        
    def power_buzzer_ctrl(self,status):
        self.match_pcf8574_pin_num('buzzer_ctrl')
        if status == 'open':
            self.enable_pin(self.act_ant_num)
            print(self.act_ant_num)
        else:
            self.disable_pin(self.act_ant_num)
    
    def power_srs_ctrl(self,status):
        if status == 'open':
            self._control_io(RASPI_MATCH_DICT['CAR_SRS'],1)
        else:
            self._control_io(RASPI_MATCH_DICT['CAR_SRS'],0)
    
    def power_OPUT1_ctrl(self,status):
        if status == 'open':
            self._control_io(RASPI_MATCH_DICT['OPUT1'],1)
        else:
            self._control_io(RASPI_MATCH_DICT['OPUT1'],0)
    
    def _control_io(self, io_num, status):
        import wiringpi
        wiringpi.pinMode(io_num,1)
        wiringpi.digitalWrite(io_num,status)
        

try:
    init_voltage = Power()
    init_voltage.volt_adjust(12)
except:
    print('init voltage failed')
    
    