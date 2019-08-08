import os
import sys
import time
if '/home/pi' not in sys.path:
    sys.path.append('/home/pi')
from hlrfw.configs.sys_config import DING_ADDR_2

class AutoTestNoticeDing(object):
    '''
    - 钉钉提醒接口
    - 默认提醒的群是CZG
    '''
    def __init__(self, type, text='', title='', messageUrl='', picUrl=''):
        self.type = type
        self.title = title
        self.text = text
        self.messageUrl = messageUrl
        self.picUrl = picUrl
        self.ding_addr = DING_ADDR_2
        
    def send_to_ding(self):
        self.setup_ding_msg()
        os.system(self.ding_order)
        
    def setup_ding_msg(self):
        if self.type == 'link':
            self.ding_order = 'curl \'%s\' -H \'Content-Type: application/json\' -d \'{\"msgtype\": \"link\", \"link\": {\"messageUrl\": \"%s\", \"picUrl\": \"%s\",\"title\":\"%s\",\"text\":\"%s\", }}\''%(self.ding_addr,self.messageUrl,self.picUrl,self.title,self.text)
        elif self.type == 'text':
            self.ding_order = 'curl \'%s\' -H \'Content-Type: application/json\' -d \'{\"msgtype\": \"text\", \"text\": {\"content\":\"%s\", }}\''%(self.ding_addr,self.text)

    def set_text_msg(self, text):
        self.text = text
        
    def set_ding_addr(self, ding_addr):
        self.ding_addr = ding_addr
        
        
if __name__ == "__main__":
    a = AutoTestNoticeDing('text', 'test')
    a.send_to_ding()
