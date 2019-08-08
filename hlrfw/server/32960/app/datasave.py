#!coding=utf-8
import pymysql
import time

def datasave(terminal_request, dict_msg, table_info):
    '''
    - 把数据存入数据库
    - terminal_request: 数据源字典
    - dict_msg: 需要保存的数据字典
    - table_info: 存入的数据表名
    '''
    save_res = {}
    sql_table = ''
    sql_values = ''
    # 获取游标
    conn = pymysql.connect(
        host = 'localhost',
        port = 3306,
        user = 'root',
        passwd = 'zhangroot',
        db = 'hlrfw_test',
        unix_socket = '/var/run/mysqld/mysqld.sock',
        #cursorclass = MySQLdb.cursors.DictCursor
        )    
    cur = conn.cursor()
    
    # 提取需要存储的数据，并且从10进制转换为16进制
    for key in dict_msg:
        res = ''
        # 如果数据是整型，就转为数组
        if isinstance(dict_msg[key],int):
            dict_msg[key] = (dict_msg[key],)
        
        for item in dict_msg[key]:
            # 如果数据是字符串，就不做处理直接存入数据库，之前是因为前面已经把VIN码转为字符串了，就不做处理直接存入
            if isinstance(item,str):
                pass
            # 如果整型大于255，也直接存入数据库
            elif item > 255:
                item = str(item)
            else:
                item = int(item)
                # 转码转成16进制，（没到16的话需要补一个0）
                if item/16 == 0:
                    item = '0'+str(hex(item)[2:])
                else:
                    item = str(hex(item)[2:])
            res = res+item
        # 组成了要保存的字典数据
        save_res[key] = res
    
    # 组成填充的sql语句
    for key in save_res:
        if save_res[key] != '':
            sql_table = sql_table+key+','
            sql_values = sql_values+'\''+str(save_res[key])+'\''+','
    
    # 去掉尾部的逗号
    sql_table = sql_table[0:-1]
    sql_values = sql_values[0:-1]
    # 组成sql语句
    sql_insert = 'insert into {}({}) values({});'.format(table_info, sql_table, sql_values)
    
    # 组成sql语句执行sql语句
    try:
        cur.execute(sql_insert)
        conn.commit()
    except Exception as e:
        print 'insert data failed!'
        conn.rollback()
    finally:
        conn.close()

def int_list_to_str(content):
    '''
    - 获取这次上报的数据的时间
    - 这个当初是为了获取 每条上报数据的时间间隔，但是其实没必要，直接计算数据库的时间间隔就行
    '''
    #getting this report time 
    this_report_time = ''
    for item in content:
        if item == 0:
            item = '0' + str(item)
        elif item/10 == 0:
            item = '0' + str(item)
        this_report_time = this_report_time + str(item)
    return (this_report_time,)


class Split_msg_to_str:
    '''
    - 分解实时上报数据，用于存储
    '''
    def __init__(self,content):
        self.con = content
        
    def split_con(self):
        self.con = list(self.con)
        self.con.append(23)
        num = 6
        con_appear = {}
        split_msg_to_str = Split_msg_to_str(1)
        # 23 是我填充到最后一位的数据,用来判断是否到达最后一位
        while self.con[num] != 23:
            # 分解方式，参考国标协议
            if self.con[num] == 1:
                con_appear['1'] = split_msg_to_str.int_list_to_hex_str(self.con[num+1:num+21])
                num = num+21
                print '1:',con_appear['1']
            if self.con[num] == 2:
                num = num+2
                num2 = int(self.con[num-1])
                self.con_res = ''
                self.con_res = self.con_res + split_msg_to_str.int_list_to_hex_str((num2,))
                for i in range(num2):
                    self.con_res = self.con_res + split_msg_to_str.int_list_to_hex_str(self.con[num:num+12])
                    num = num+12
                con_appear['2'] = self.con_res
                print '2:',con_appear['2']
            if self.con[num] == 3:
                num3 = 19+int(self.con[num+8])
                con_appear['3'] = split_msg_to_str.int_list_to_hex_str(self.con[num+1:num+num3])
                num = num+num3
                print '3:',con_appear['3']
            if self.con[num] == 4:
                con_appear['4'] = split_msg_to_str.int_list_to_hex_str(self.con[num+1:num+6])
                num = num+6
                print '4:',con_appear['4']
            if self.con[num] == 5:
                con_appear['5'] = split_msg_to_str.int_list_to_hex_str(self.con[num+1:num+10])
                num = num+10
                print '5:',con_appear['5']
            if self.con[num] == 6:
                con_appear['6'] = split_msg_to_str.int_list_to_hex_str(self.con[num+1:num+15])
                num = num+15
                print '6:',con_appear['6']
            if self.con[num] == 7:
                self.con_res = ''
                self.con_res = self.con_res + split_msg_to_str.int_list_to_hex_str(self.con[num+1:num+6])
                num = num+6
                for i in range(4):
                    self.con_res = self.con_res + split_msg_to_str.int_list_to_hex_str(self.con[num:num+int(self.con[num])*4+1])
                    num = num+int(self.con[num])*4+1
                con_appear['7'] = self.con_res
                print '7:',con_appear['7']
            if self.con[num] == 8:
                num8 = int(self.con[num+1])
                num = num+2
                self.con_res = ''
                self.con_res = self.con_res + split_msg_to_str.int_list_to_hex_str((num8,))
                for i in range(num8):
                    num81 = int(self.con[num+9])
                    self.con_res = self.con_res + split_msg_to_str.int_list_to_hex_str(self.con[num:num+2*num81+10])
                    num = num+2*num81+10
                con_appear['8'] = self.con_res
                print '8:',con_appear['8']
            if self.con[num] == 9:
                num9 = int(self.con[num+1])
                num = num+2
                self.con_res = ''
                self.con_res = self.con_res + split_msg_to_str.int_list_to_hex_str((num9,))
                for i in range(num9):
                    num91 = int(self.con[num+1])*256+int(self.con[num+2])
                    self.con_res = self.con_res + split_msg_to_str.int_list_to_hex_str(self.con[num:num+3+num91])
                    num = num+3+num91
                con_appear['9'] = self.con_res
                print con_appear['9']
                print self.con[num]
            if self.con[num] == 80:
                num8 = int(self.con[num+1])*256+int(self.con[num+2])
                con_appear['80'] = split_msg_to_str.int_list_to_hex_str(self.con[num+1:num+num8+3])
                num = num+num8+3
            else:
                # 如果数据不对，就会忽略后面的数据
                break
        return con_appear

    def int_list_to_hex_str(self, data):
        '''
        - 整型数组转为hex字符串
        '''
        return_hex_str = ''
        for item in data:
            if int(item) <=  15:
                item = hex(item)[2:]
                item = '0' + str(item)
            else:
                item = str(hex(item)[2:])
            return_hex_str = return_hex_str + item
        return return_hex_str
