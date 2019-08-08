#!coding:utf-8
'''
功能:
- 清理 串口日志文件
- 现在每次自动化测试结束后会自动移动日志，所以这个很少使用
'''
import os
import time
import sys

path_dir = '/home/pi/Desktop/journal_log/'

files = os.listdir(path_dir)

for log_file in files:
    print(log_file)
    clean_log = ': > /home/pi/Desktop/journal_log/{0}'.format(log_file)
    os.system(clean_log)



