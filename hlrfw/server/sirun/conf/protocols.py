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
        ('sys_ok', (0,)),
        ('sys_err', (1,)),
        ('sys_call_back_num', (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)),
        ('sys_reg_ACK_len', (0, 21)),
        ('sys_bid',(1,2,3,4)),
        ('sys_reg_result_ok', (121,)),
        ('sys_reg_result_err', (168,)),
        ('sys_reg_req_mid', (2,)),
        
        ('login_mid_cha', (2,)),
        ('login_mid_err', (4,)),
        ('login_mid_ok', (5,)),
        ('login_cha_md5', (5,)),
        ('login_random', (5,)),
        ('login_aesrandom',(16,)),
        ('login_serial',(1,)),
        ('login_time',(8,)),
        ('login_work_win',(8,)),
        ('login_link_hb',(8,)),
        



        
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
        ('0x0001', 't_register'),
        ('0x0002', 't_login'),
        ('0x0003', 't_logout'),
        ('0x0004', 't_relogin'),
        ('0x000B', 't_take_msg'),
        ('0x0005', 't_get_config'),
        ('0x0007', 't_set_config'),
        ('0x0006', 't_update'),
        ('0x002B', 't_keep_link'),
        ('0x004B', 't_keep_active'),
        ('0x01F1', 't_control_car'),
        ('0x01F2', 't_can_rep'),
        ('0x01F3', 't_err_rep'),
        ('0x01F4', 't_remote_diagnosis'),
        ('0x01F5', 't_actual_msg_rep'),
        ('0x01F6', 't_E_call'),
        ('0x01F7', 't_UBI_rep'),
        ('0x02E1', 't_nat_car_login'),
        ('0x02E2', 't_nat_car_logout'),
        ('0x02E3', 't_nat_reissue_msg_rep'),
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
