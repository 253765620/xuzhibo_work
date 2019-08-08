#!/usr/bin/python3
#!coding:utf-8
'''
- robotframework对外开放的功能，只需要实现你要的方法就行，具体使用可以参照robotframwork的说明书中的监控器
'''
import sys
if '/home/pi' not in sys.path:
    sys.path.append('/home/pi')

#from production.QtView.flashloader import *
#from production.QtView.test_ctrl import *


class Listener_production(object):
    ROBOT_LISTENER_API_VERSION = 2
    
    def __init__(self):
        pass
        
    def start_suite(self, name, attrs):
        pass

        
    def end_suite(self, name, attrs):
        pass
    def start_test(self, name, attrs):
        self.write_data_display('{}测试开始'.format(name))
        
    def end_test(self, name, attrs):
        #self.process_display(attrs.get('stauts'))
        self.write_data_display('{}测试结束'.format(name))
        self.write_data_display('{}的测试结果为:{}'.format(name,attrs.get('status')))
    def _attrs_msg(self, name, attrs):
        pass

    def _choice_user_tag(self, attrs):
        pass
            
    def write_data_display(self,data):
        if data != None:
            with open('/home/pi/production/process_display.txt','a') as f:
                f.write(data+'\n')


