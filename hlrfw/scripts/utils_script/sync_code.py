#!coding: utf-8
'''
功能:
- 自动同步git上的代码，到各个Pi上
'''
import sys
import os
import pexpect
import time
import threading
sys.path.append('/home/pi')

from hlrfw.configs.ip_config import myip

#os.system('sh /home/pi/hlrfw/scripts/sync.sh')

ip_list = [120,121,122,124,125,126,127,128,130,131,133,134,137,138,139,141,142,143,144,145,147]

def sync_code(ip):
    try:
        username = 'pi'
        host = '192.168.3.{}'
        if ip in [120,122,125,126,130,137,138]:
            password = 'hlgitlab'
        else:
            password = '12345678'
        host = host.format(ip)
        process_ssh = pexpect.spawn('ssh {}@{}'.format(username, host))

        index = process_ssh.expect([
                "continue connecting (yes/no)?",
                "password:",
            ])

        if index == 0:
            process_ssh.sendline("yes")
            process_ssh.expect('password:')
            process_ssh.sendline(password)
            print('login successful 0')
            
        if index == 1:
            process_ssh.sendline(password)
            print('login successful 1')

        #process_ssh.sendline('cd /home/pi/hlrfw')
        #process_ssh.sendline('git stash')
        #process_ssh.sendline('git pull')
        process_ssh.sendline('sh /home/pi/hlrfw/scripts/confirm_ip_port.sh')
        time.sleep(20)
        #process_ssh.expect('confirm ip end')
        process_ssh.close()
    except Exception as e:
        print(myip,':',e)

for ip in ip_list:
    if ip == 145:
        continue
    t_sync = threading.Thread(target=sync_code, args=(ip,))
    t_sync.start()