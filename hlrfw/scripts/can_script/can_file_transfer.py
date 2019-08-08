#!coding:utf-8
'''
功能:
- 用来将测试人员提交的, 使用busmaster生成的CAN回放文件(也就是.log),转化为python-can识别的csv格式文件
'''
import os
import csv
import time
import argparse
import subprocess

from itertools import islice


class CANFileTransfer(object):
    def __init__(self, log_file_dir, filter_dir, filter_id_list):
        self.filter = filter_id_list
        self.filter_dir = filter_dir
        self.log_file_dir = log_file_dir
        self._get_csv_dir()
        self._open_csv_file()
        
    def _get_csv_dir(self):
        '''
        if self.log_file_dir[-1] == '/':
            self.log_file_dir = self.log_file_dir[:-1]
        location = self.log_file_dir.rfind('/')
        self.csv_file_dir = self.log_file_dir[:location]
        '''
        self.csv_file_dir = self.log_file_dir[:self.log_file_dir.rfind('log')] + 'csv'
        
    def _open_csv_file(self):
        self.csv_file = csv.writer(open(self.csv_file_dir,'w'),lineterminator='\n')

    def get_filter(self):
        if self.filter_dir and os.path.exists(self.filter_dir):
            for maindir, subdir, file_name_list in os.walk(self.filter_dir):
                for file_name in file_name_list:
                    if file_name.rfind('.flt') != -1:
                        nodesim_file = maindir+'/'+file_name[:-4]
                        nodesim_filter_file = maindir+'/'+file_name
                        if self._get_process_pid(nodesim_file):
                            self.add_flt(nodesim_filter_file)
                    
    def _get_process_pid(self, name):
        '''
        功能: 获取执行进程的pid
        - name: 开启进程的shell命令（一部分就可以）
        
        - 返回值: 一个pid为整型的列表
        '''
        pid_list = []
        pid_list_obj = subprocess.Popen(['pgrep', '-f', name], stdout=subprocess.PIPE, shell=False)
        pid_list_bytes = pid_list_obj.communicate()[0].split()
        
        for index,pid in enumerate(pid_list_bytes):
            int_pid = int(pid)
            print('要查询的进程PID为: ',int_pid)
            pid_list.append(int_pid)

        return pid_list
    
    def add_flt(self, nodesim_filter_file):
        with open(nodesim_filter_file, 'r') as f:
            while 1:
                line = f.readline().strip()
                if not line:
                    break
                self.filter.append(line.strip())

    def start_tranfer(self):
        self.get_filter()
        with open(self.log_file_dir,'r') as f:
            for i in islice(f,10,None):
                try:
                    # split msg
                    file_list = i.strip().split(':')
                    file_list_3 = file_list[3]
                    
                    # parse msg
                    data_list = file_list_3[5:-24].split(' ')
                    direct, channel, can_id, data_type, dlc  = data_list
                    if can_id in self.filter:
                        continue
                    if data_type == 'x':
                        extended = '1'
                        if can_id[-1] == 'x':
                            can_id = can_id[:-1]
                    else:
                        extended = '0'
                    can_data = file_list_3[-23:]
                    
                    # get timestamp
                    myhour = file_list[0]
                    mymin = file_list[1]
                    myse = file_list[2]
                    mymse = file_list_3[:4]
                    #print(myhour,mymin,myse,mymse)
                    timestamp = int(myhour)*3600 + int(mymin)*60 + int(myse) + float(mymse)/10000
                    
                    # write to csv file
                    self.csv_file.writerow([str(timestamp),can_id,extended,'0','0',dlc,can_data])
                except Exception as e:
                    print(e)
            print('csv文件生成结束')

if __name__ == "__main__":
    #获取外部参数
    parser = argparse.ArgumentParser(
        description="",
        )
    parser.add_argument("-f", "--log_file_dir",
                        help="""Storage path of executed test cases""",
                        default=None)
    parser.add_argument("-D", "--filter",
                        help="""filtered can ID file direction""",
                        default=None)
    log_file_dir = parser.parse_args().log_file_dir
    filter = parser.parse_args().filter
    if not log_file_dir:
        raise AssertionError('No file direction input')
    can_file_trans = CANFileTransfer(log_file_dir, filter)
    can_file_trans.start_tranfer()
    