#!coding: utf-8
'''
功能:
- 更新thingsboard的属性
- 记得好像是准备启动测试的时候更新一下属性
'''
import os
import sys
from os import path
from sys import path as path2
path2.append(path.abspath(path.join(__file__,'../../..')))
from hlrfw.configs.sys_config import EQUIPMENT_TOKEN_DICT,EQUIPMENT_ID_DICT

script, key, value = sys.argv
equioment_token = None
output = os.popen('grep \"static ip_address=192.168.3\" /etc/dhcpcd.conf')
for ip in output:
    #print(ip[-4:-1])
    equioment_token = EQUIPMENT_TOKEN_DICT.get(EQUIPMENT_ID_DICT.get(ip[-4:-1]))
if not equioment_token:
    raise AssertionError('input ip error')


def update_euqipment_attribute(key, value, local_token):
    order = "curl -v -X POST -d \"{\\\"" + str(key) + "\\\": \\\"" + str(value) + "\\\"}\" http://47.96.109.21:8080/api/v1/" + local_token +"/attributes --header 'Content-Type:application/json'"
    os.system(order)

if __name__ == "__main__":
    update_euqipment_attribute(key, value, equioment_token)
    #modify branch version
    from hlauto.iwhole import *
    update_euqipment_attribute('branch',branch,equioment_token)
    update_euqipment_attribute('version',version,equioment_token)