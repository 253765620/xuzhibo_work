#!coding:utf-8
import sys
import smtplib
if '/home/pi' not in sys.path:
    sys.path.append('/home/pi')
    
from email.mime.text import MIMEText
from email.header import Header

from hlrfw.utils.ding_notice.ding import AutoTestNoticeDing


class AutoTestNoticeMail(object):
    '''
    - 发送邮件接口
    '''
    def __init__(self, receivers='chengui@hopelead.com', message='send mail failed'):
        self.mail_host = '192.168.3.117'
        self.mail_user = 'chengui'
        self.mail_pass = '123456'
        self.sender = 'chengui@hopelead.com'
        self.receivers = [receivers,]
        self.set_message(message)
        self.smtpObj = smtplib.SMTP()
        self.ding = AutoTestNoticeDing('text')    # 钉钉对象，在发送邮件失败的时候用来提醒
        
    def set_receivers(self, receivers):
        '''
        - 设置接收对象的邮箱, 暂时只能发送一个，要群发需要改写
        '''
        self.receivers = [receivers,]
        
    def set_message(self, message):
        '''
        - 设置要发送的邮件内容
        '''
        self.message = MIMEText(message, 'plain', 'utf-8')
        self.message['From'] = 'Hlauto Test'
        
    def try_send_mail(self):
        '''
        - 尝试发送邮件，失败钉钉会有提示消息
        '''
        try:
            self._send_mail()
            print("邮件发送成功")
        except smtplib.SMTPException:
            self.ding.set_text_msg('Error: 无法发送邮件'+'\n'+self.receivers[0])
            self.ding.send_to_ding()
    
    def _send_mail(self):
        '''
        - 连接邮箱，登陆邮箱，发送邮件
        '''
        self._connect()
        self._login()
        self._sendmail()

    def _connect(self):
        self.smtpObj.connect(self.mail_host, 25)
        
    def _login(self):
        self.smtpObj.login(self.mail_user, self.mail_pass)
        
    def _sendmail(self):
        self.smtpObj.sendmail(self.sender, self.receivers, self.message.as_string())


if __name__ == "__mian__":
    '''
    - Test
    '''
    a = TestNoticeMail('xieanyue@hopelead.com', 'hello')
    a.try_send_mail() 
