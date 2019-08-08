"""
0x8100 Poor readability,so we need to give a name
to it.how about 'ter_reg_req' as it nickname!
"""
from core.urls import pattern
from core.dns import dns_key, dns_k2v
from utils.authentication import simple_auth

#AUTH_CODE = simple_auth()
AUTH_CODE = (1,2)
SYSTEM_CMD = pattern(
        ('sys_ok', (1,)),
        ('sys_err', (2,)),
        ('sys_crc', (1,)),
        ('sys_auth', AUTH_CODE),
        ('sys_product', (0, 1)),
        ('sys_fixed_msg_attr', (0, 5)),  # This is a fixed value ,you should calculate the msg attr yourself!
        ('sys_fixed_msg_attr2', (0, 6)),  # Empty message content for check terminal setting
        ('sys_msg_product',(0,0)),
)

"""
ser     : server
ter     : terminal
req     : request
rsp     : response
reg     : register
aut     : authentication
loc     : location
com     : commonly
get     : get
info    : information
attr    : attribute
"""
MSG_ID_ORIGINAL = pattern(
        ('0x01', 'load_car'),
        ('0x02', 'actual_msg_report'),
        ('0x04', 'reissue_msg_report'),
        ('0x05', 'logout_car'),
        ('0x03', 'heartbeat'),
        ('0x08', 'terminal_correcting_time'),
        #('0x09', 'err_return'),
)

"""
change the MSG_ID_ORIGINAL Dicts key
example1: 0x0100 --> (1,0)
example2: 0100 --> (1,2)
"""
MSG_ID = dns_key(MSG_ID_ORIGINAL)
SYS_ID = dns_k2v(MSG_ID)

if __name__ == '__main__':
    print 'MSG_ID       :', MSG_ID
    print 'SYSTEM_CMD   :', SYSTEM_CMD
    print 'SYS_ID       :', SYS_ID
