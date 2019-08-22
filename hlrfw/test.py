import os, sys, time
import subprocess
import pexpect


def server_ping(url,timeout=10):
    these_time = time.time()
    cmd = "ping -c 1  \"%s\" " % (url)
    for i in range(int(timeout)):
        result = os.system(cmd)
        result >>= 8
        if result:
            #print('ping fail')
            last_time = time.time()
            time_difference = int(last_time - these_time)
            print('sub:{}'.format(time_difference))
            if time_difference >= timeout:
                #print('sub')
                print('ping fail')
                break
                return (1,time_difference)
        else:
            print('ping suc')
            last_time = time.time()
            time_difference = int(last_time - these_time)
            print(time_difference)
            return (0,time_difference)

a = server_ping('192.168.3.101')
print(a)