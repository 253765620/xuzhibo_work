#!coding: utf-8
import time
from smbus2 import SMBusWrapper

class Ad5259(object):
    def _adjust_volt_to(self, out_volt):
        # 公式的电阻更改为4.7K, 后续要改为3K, 0.3V是补偿, 4.7是R87的阻值
        calculate_volt_val = 255 - (float(19125)/(out_volt-0.3)-4.7*255)/50 #255 - (75*255/(out_volt-0.3)-2.98*255)/50
        self.write_data(int(round(calculate_volt_val)))
        
    def write_data(self, volt_val):
        '''
        - 写入调节的电压值, 范围是0~255
        '''
        with SMBusWrapper(1) as bus:
            bus.write_byte_data(0x18, 0, volt_val)
