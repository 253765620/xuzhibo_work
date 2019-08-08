# -*- coding: utf-8 -*-
'''
指定使用的芯片的常量
'''

# PCF8574 起始地址
PCF8574_START_ADDR = 100
# PCF8574 io口定义
PCF8574_MATCH_DICT = {
    'gnss_open' : 1,'wwan_open' : 3,'ble_open' : 5,'wifi_open' : 7,
    'gnss_short' : 2,'wwan_short' : 4,'ble_short' : 6,'buzzer_ctrl' : 8,
    }

# PCF8591 起始地址
PCF8591_START_ADDR = 120
# PCF8591 io口定义
PCF8591_MATCH_DICT = {
    'power_volt' : 1, 'curr_volt':2, 'out1_volt' : 3, 'acc_volt' : 4,
    }


# PCF8591 计算公式常量
PCF8591_CONSTANT = 3.3/255 #3.3/255
PCF8591_DEVIATION = 0
PCF8591_CURR_VOL_DEVIATION = 0

# INA255 电流检测计算公式常量
INA255_CONSTANT = 2 #1/0.5
#INA255_CONSTANT_DEVIATION = 2/1000
#pi io口定义
RASPI_MATCH_DICT = {
    'power' : 7,
    'acc' : 2,
    'out_1' : 0,
    'CAR_SRS':28 ,
    'OPUT1':29
    }
