#! coding:utf-8

"""
some tool work for batter
Like example (1,2) become 0000 0001 0000 0010
and the digit should be :512+2=514
"""
import hashlib
import time
import binascii

from utils.check_code import check


def is_subpackage(val):
    """

    :param val: a tuple
    :return: a decimal digit!
    """
    temp = val[0]
    if temp & 64:
        return True
    else:
        return False


def is_encryption(val):
    """
    checking the 10bit if it's fill '1' mean use RSA encrytion
    return True else return False
    :return: BOOL
    """
    temp = val[0]
    if temp & 1024:
        return True  # RSA encryption!
    else:
        return False


def is_complete(val, std):
    """
    if the client crc equal the calculate value
    and then return True else return False!
    :param val:
    :return:
    """
    result = check(val)
    if result == std:
        return True  # The crc encryption equal the client send!
    else:
        return False


def field_langth(val):
    """
    Sometime,we don't know each field length before we resolute it!
    So,we need to calculate some field and then get the exactly length!
    That's why we need this function!
    :param val:
    :return: Integer value
    """
    return int(val[0])


def dec2hex4tuple(val):
    """
    :rtype: object
    :param val: a tuple ,which include decimal number!
    :return: a tuple ,which include hex number!
    """
    temp = []
    for item in val:
        temp_item = hex(item).replace('0x', '')
        temp_save = int(temp_item)
        temp.append(temp_save)
    return tuple(temp)


def to_dword(val):
    """
    :param val: a tuple (2, 110, 226, 147)
    :return:40821395 but what we need is range(38.0000 ~ 42.00000)
    """
    temp_hex = []
    for item in val:
        temp_hex.append(hex(item))
    temp_str = ''
    for item in temp_hex:
        temp_str += str(item).replace('0x', '')
    result = int(temp_str, 16)
    return result


def to_double_word_fun(val):
    """
    :param val: a tuple (2, 110, 226, 147)
    :return: (38.0000 ~ 42.00000)
    """
    a_value = to_dword(val)
    temp = float(a_value)
    ret = temp / 1000000
    return ret


def to_int_dword_fun(val):
    a_value = to_dword(val)
    temp = int(a_value)
    return temp


def to_a_word_fun(val):
    """
    :param val: a tuple with two element (2, 110)
    :return:
    """
    a_value = to_dword(val)
    temp = float(a_value)
    return temp

def split_hex_str_to_dict(content, config_dict):
    '''
    example input [1,2,3], {'1':(0,1),'1':(1,3)}
    output {'1':(1,),
            '2':(2,3)}
    '''
    ret_dict = {}
    for k,v in config_dict.items():
        display = v[0]
        split_msg = ''
        split_list = v[2:]
        data_len = len(split_list)
        for item in split_list:
            myitem = ''
            item_content = content[item[0]:item[1]]
            if display == 'B':
                for i in range(len(item_content)):
                    myitem = myitem + str(item_content[i]) + ','
            if display == 'W':
                location = 0
                for i in range(len(item_content)/2):
                    myitem = myitem + str(item_content[location]*256 + item_content[location+1]) + ','
                location = location + 2
            if display == 'DW':
                #myitem = str(item_content[0]*256**3 + item_content[1]*256**2 + item_content[2]*256 + item_content[3]) + ','
                for item in item_content:
                    if item/10 == 0:
                        item = '0' + str(hex(item)[2:])
                    else:
                        item = hex(item)[2:]
                    myitem = myitem + str(item)
            split_msg = split_msg + myitem
        ret_dict[k] = (split_msg,)
    return ret_dict

def merge_dict(dict1, dict2):
    '''
    把第二个字典中，每个键的值（元组），加到第一个字典中相同的键的值（元组）中
    '''
    for k,v in dict2.items():
        dict1[k] = dict1[k] + dict2[k]
    return dict1

def get_sys_time_list():
    '''
    获取系统时间，并转化为hex码
    返回一个整型时间戳元组
    '''
    stamp_time = time.time()
    str_hex_time = str(hex(int(stamp_time)))
    str_time = ()
    num = 2
    for i in range(4):
        str_time = str_time + (int('0x'+str_hex_time[num:num+2],16),)
        num = num + 2
    return str_time

def change_tuple(val):
    '''
    将val一串数字转化为一个整型元组
    '''
    ret_tuple = ()
    data_len = len(val)/2
    location = 0
    for i in range(data_len):
        ret_tuple = ret_tuple + (int(val[location:location+2]),)
        location = location + 2
    return ret_tuple

def get_config_bin_str(val):
    '''
    获取2进制的res结果数据
    '''
    bin_str = ''
    for item in val:
        item = str(bin(item)[2:])
        len_item = 8 - len(item)
        for i in range(len_item):
            item = '0' +item
        bin_str = bin_str +item
    return bin_str

def int_tuple_to_hex_str(val):
    hex_str = ''
    for item in val:
        hex_str = hex_str + str(hex(item))[2:]
    return hex_str

#保存终端信息的工具
def int_to_str_display(val):
    '''
    获取终端的VIN，也就是把数据转为对应的字符
    '''
    a = ''
    for item in val:
        item = chr(item)
        a = a + item
    return (a,)

def time_tuple_to_timestamp_tuple(val):
    '''
    把终端发送的终端时间转化为一个时间戳
    '''
    a = '20'
    for item in val:
        if item/10 == 0:
            item = '0' + str(item)
        else:
            item = str(item)
        a = a + item
    b = time.strptime(a, '%Y%m%d%H%M%S')
    c = (str(int(time.mktime(b))),)
    return c

def ter_time_to_stamp(val):
    '''
    把终端时间转化为时间戳
    用作数据库存储
    '''
    mytime = '20'
    for item in val:
        if item/10 == 0:
            item = '0' + str(item)
        else:
            item = str(item)
        mytime = mytime + item
    ret_stamp = int(time.mktime(time.strptime(mytime,'%Y%m%d%H%M%S')))
    return (ret_stamp,)

def get_B11G_timestamp(val):
    stamp = val[0]*256**3 + val[1]*256**2 + val[2]*256 + val[3]
    return (stamp,)

def dec_10_to_2(val):
    '''
    将10进制转化为2进制返回
    '''
    a = ''
    for item in val:
        b =  bin(item)[2:]
        while len(b) < 8:
            b = '0' + b
        a = a + b
    return a

#返回终端信息的工具
def get_sys_localtime_tuple():
    '''
    获取系统时间，转化为时间元组
    '''
    mytime = time.localtime()
    time_tuple = (20,)
    i = 0
    for item in mytime:
        if str(item).find('201') != -1:
            item = item % 100
        time_tuple = time_tuple + (item,)
        if i > 4:
            break
        i = i + 1
    return time_tuple

def get_sys_time_int_tuple():
    '''
    用于返回终端的时间
    （18,1,1,1,1,1）
    '''
    mytime = time.localtime()
    time_tuple = ()
    i = 0
    for item in mytime:
        if str(item).find('201') != -1:
            item = item % 100
        time_tuple = time_tuple + (item,)
        if i > 4:
            break
        i = i + 1
    return time_tuple

def to_md5_data(val):
    '''
    将val进行md5加密
    val需要输入一个元组
    返回加密后的数据的前16个字节组成的元组
    '''
    str_hex = ''
    ret_data = ()
    num = 0
    for item in val:
        item = str(hex(item))[2:]
        str_hex = str_hex + item
    m = hashlib.md5()
    md5_data = hashlib.new('md5', str_hex).hexdigest()
    for i in range(16):
        str_md5_hex = '0x'+binascii.b2a_hex(md5_data[num:num+1]).upper()
        ret_data = ret_data + (int(str_md5_hex,0),)
        num = num + 1
    return ret_data

def get_sharengo_check_code(val):
    '''
    对xlg的服务器数据进行校验，并返回一个加密后的前后各两个字节，组成数组校验码
    [1,2，3,4]
    '''
    str_hex = ''
    ret_data = ()
    num = 0
    for item in val:
        if item/16 == 0:
            item = '0' + str(hex(item))[2:]
        else:
            item = str(hex(item))[2:]
        str_hex = str_hex + item
    str_hex = (str_hex + '30313233343536373839616263646566').decode('hex')
    m = hashlib.md5()
    md5_data = hashlib.new('md5', str_hex).hexdigest()
    ret_list = (md5_data[0:2],md5_data[2:4],md5_data[-4:-2],md5_data[-2:])
    for item in ret_list:
        item = '0x' + item
        item = int(item,0)
        ret_data = ret_data + (item,)
    return list(ret_data)
    
    

#显示终端信息的工具
def display_sys_time():
    '''
    获取终端的时间斌且打印出来
    '''
    a = time.time()
    b = time.localtime(a)
    c = time.strftime('%Y-%m-%d %H:%M:%S',b)
    print 'time pi: ',c

def display_stamp_to_date(val):
    a = time.localtime(val)
    b = time.strftime('%Y%m%d%H%M%S',a)
    print 'ter time: ',b


if __name__ == '__main__':
    sample1 = (127, 2)
    print is_subpackage(sample1)
    sample2 = (1023, 0)
    print is_encryption(sample2)

    print '----------Test to_dword --------------'
    sample5 = (2, 110, 226, 147)
    sample5x = to_dword(sample5)
    print 'old      :', sample5
    print 'new      :', sample5x

    print '---------Test to_position-----------'
    sample6 = (6, 168, 93, 143)
    print 'old      :', sample6
    print 'new      :', to_double_word_fun(sample6)

    print '---------Test to_altitude----------'
    sample7 = (4, 89)
    print 'old      :', sample7
    print 'new      :', to_a_word_fun(sample7)

    print '---------Test to_int_dword---------'
    sample8 = (6, 168)
    print 'old      :', sample8
    print 'new      :', to_int_dword_fun(sample8)
