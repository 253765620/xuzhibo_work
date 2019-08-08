# -*- coding: utf-8 -*-
import os
import re
import datetime
from hlrfw.configs.sys_config import SERIAL_LOG_USB0

def is_timeout_1(sear_line, mins):
    '''
    - 超时判断, 分钟数小于查找的分钟数
    '''
    _time = re.findall(r"[[](.*?)[]]", sear_line)
    if _time:
        if mins > _time[0][3:5]:
            return -1
    return 0

def is_timeout_2(sear_line, mins):
    '''
    - 超时判断, 分钟数大于查找的分钟数
    '''
    _time = re.findall(r"[[](.*?)[]]", sear_line)
    if _time:
        if mins < _time[0][3:5]:
            return -1
    return 0

def parse_ter_log(search_cont, mins, timeout_func, filesize):
    '''
    - 解析终端日志
    - 从日志最后开始，每次读取1024个字节数据, 200次
    '''
    blocksize = 1024
    maxseekpoint = 1
    dat_file = open(SERIAL_LOG, 'r')
    for i in range(200):
        # 如果读取的位置已经超过了日志文件的大小，就终止循环
        if (maxseekpoint-i-1)*blocksize < filesize:
            maxseekpoint = filesize // blocksize
            if maxseekpoint == 0:
                # 如果文件大小不到1024，就从头开始读取
                dat_file.seek(0, 0)
                # 读取游标后面所有的内容, readlines python2会返回一个数组，python3会返回一个生成器
                lines = dat_file.readlines()
                lines_len = len(lines)
                for item in range(lines_len):
                    # 从后往前读取数据
                    sear_line = lines[-1-item]
                    # 判断是否超时，超时就返回-1
                    if timeout_func(sear_line, mins):
                        return -1
                    # 判断是否有要查找的内容，有的话就返回这行数据
                    if sear_line.find(search_cont) != -1:
                        return sear_line
                # 文件都读取完了，就break
                break
            else:
                # 游标移动到文件末尾，前面内容为1024整数倍的位置
                dat_file.seek((maxseekpoint-i-1)*blocksize)
        else:
            # 文件都读取完了，就break
            break
        # 这是正常情况下，读取文件内容
        lines = dat_file.readlines()
        lines_len = len(lines)
        for item in range(lines_len):
            sear_line = lines[-1-item]
            if timeout_func(sear_line, mins):
                return -1
            if sear_line.find(search_cont) != -1:
                return sear_line
    # 关闭文件
    dat_file.close()
            

def search_ter_log(search_time, search_cont):
    '''
    找到返回对应字符, 超时返回-1, 找到返回字符串
    '''
    now_time = datetime.datetime.now()
    del_time = datetime.timedelta(seconds=search_time*60)
    search_time = (now_time - del_time).time()
    if now_time.minute > search_time.minute:
        timeout_func = is_timeout_1
    else:
        timeout_func = is_timeout_2
    filesize = os.path.getsize(SERIAL_LOG)
    readline = parse_ter_log(search_cont, str(search_time)[3:5], timeout_func, filesize)
    print(str(search_time)[3:5])
    return readline

def split_msg(val):
    '''
    负责将串口'='后面的数据切片,分开判断
    '''
    c = []
    # 判断字符串的长度是不是小于7，是的话，直接返回这个字符串的数组
    if len(val) > 7:
        # 
        if val[6] == '+':
            i = 0
            j = 0
            val = val[7:]
            for item in val:
                i = i + 1
                j = j + 1
                if item == ';':
                    if item == '\r\n':
                        continue
                    c.append(val[i-j:i-1])
                    j = 0
            c.append(val[i-j:])
        else:
            c.append(val)
    else:
        c.append(val)
    return c

