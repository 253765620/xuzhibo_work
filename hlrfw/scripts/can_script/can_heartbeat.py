#!coding: utf-8
import time
import can
import os
import sys

def change_data(goal_data):
    ret_data = []
    a = len(str(goal_data))
    if a != 23:
        print('data length error!')
    for i in range(int(len(goal_data)/3) + 1):
        a = int(goal_data[3*i:3*i+2], 16)
        ret_data.append(a)
    return ret_data

def k_can_format_check():
    global can_id, can_data, can_interface, interval_time
    can_id = int(can_id, 16)
    can_data = change_data(can_data)
    can_interface = str(can_interface)
    interval_time = float(interval_time)/1000
    bus = can.interface.Bus(channel=can_interface,
                          bustype='socketcan')
    msg = can.Message(arbitration_id=can_id,
        data = can_data,
        extended_id=False)
    while 1:
        bus.send(msg)
        time.sleep(interval_time)

#for i in range(2):
#    os.system('sudo sh /usr/local/lib/python2.7/site-packages/hlrfw/script/can-start.sh')

#print sys.argv
script, can_id, can_data, can_interface, interval_time = sys.argv
#print can_id, can_data, can_interface, interval_time

k_can_format_check()
