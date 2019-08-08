#!coding:utf-8
'''
功能:
- 上传自动化测试产生的报告, 到gitlab的服务器上, 和pages页面一起显示
- 服务器存放路径路径: /var/opt/gitlab/gitlab-rails/shared/pages/
'''
import os
import time
import pexpect
import sys
sys.path.append('/home/pi/hlauto')
from iwhole import *

def copy_data_from_report(level, goal_dir):
    '''
    - 复制/home/pi下生成的3个robot报告的文件，到/home/pi/localreport下
    - 5个level测试用例跑完之后, 同样把串口日志复制到/home/pi/localreport下
    '''
    if not os.path.exists('/home/pi/hllocalreport/'):
        os.system('mkdir /home/pi/hllocalreport/')
    if not os.path.exists(goal_dir):
        os.system('mkdir {}'.format(goal_dir))
    goal_dir_2 = goal_dir + '/level{}'.format(level)
    os.system('mkdir {}'.format(goal_dir_2))
    os.system('sudo cp /home/pi/report.html {}/report.html'.format(goal_dir_2))
    os.system('sudo cp /home/pi/log.html {}/log.html'.format(goal_dir_2))
    os.system('sudo cp /home/pi/output.xml {}/output.xml'.format(goal_dir_2))
    if level == 5:
        time.sleep(180)
        os.system('sudo cp -r /home/pi/Desktop/journal_log {}/journal_log'.format(goal_dir))
        os.system('sudo rm -rf /home/pi/Desktop/journal_log/*.txt')

def upload_test_report(level, goal_dir):
    '''
    - 上传报告主程序
    '''
    report_dir = '/home/pi/'
    #定义上传的目标服务器的登录信息
    username = 'root'
    host = '192.168.3.116'
    password = 'hlgitlab'

    copy_data_from_report(level, goal_dir)
    
    #获取当前的日期时间
    now_date = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time()))+'_level{}/'.format(level)

    #建立对应的报告存放的路径
    goal_dir = '/var/opt/gitlab/gitlab-rails/shared/pages/iot_p23/branch_report/'
    dir_list = [imodel, branch, version]
    try:
        process_ssh = pexpect.spawn('ssh {}@{}'.format(username, host))
        index = process_ssh.expect([
                "continue connecting (yes/no)?",
                "password:",
            ])

        if index == 0:
            process_ssh.sendline("yes")
            process_ssh.expect('password:')
            process_ssh.sendline(password)
            
        if index == 1:
            process_ssh.sendline(password)
            
        for item in dir_list:
            goal_dir = goal_dir + item + '/'
        process_ssh.sendline('mkdir -p {}'.format(goal_dir))
        goal_dir = goal_dir + now_date
        process_ssh.sendline('mkdir {}'.format(goal_dir))
        report_list = ['log', 'report', 'output']
        #上传报告文件
        for item in report_list:
            if item != 'output':
                report_dir_item = report_dir + item + '.html'
                goal_dir_item = goal_dir + item + '.html'
            else:
                report_dir_item = report_dir + item + '.xml'
                goal_dir_item = goal_dir + item + '.xml'
            order = 'scp -r {} {}@{}:{}'.format(report_dir_item,username,host,goal_dir_item)
            print(order)
            process = pexpect.spawn(order)
            index = process.expect([
                    "continue connecting (yes/no)?",
                    "password:",
                ])

            if index == 0:
                process.sendline("yes")
                process.expect('password:')
                process.sendline(password)
                
            if index == 1:
                process.sendline(password)
            time.sleep(5)
            process.close()
    except:
        print('update failed')
    access_addr = 'https://192.168.3.116:11601/' + goal_dir[42:] + 'report.html'
    return access_addr
