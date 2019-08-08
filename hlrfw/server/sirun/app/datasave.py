import pymysql
import time

#global parameter
last_report_time = '0'


def datasave(terminal_request,dict_msg,table_info):
    #print terminal_request['GET']
    save_res = {}
    sql_table = ''
    sql_values = ''
    conn = pymysql.connect(
        host = 'localhost',
        port = 3306,
        user = 'root',
        passwd = 'zhangroot',
        db = 'hlrfw_test',
        unix_socket='/var/run/mysqld/mysqld.sock',
        )    
    cur = conn.cursor()
    for key in dict_msg:
        res = ''
        for item in dict_msg[key]:
            if isinstance(item,str):
                pass
            elif item > 255:
                item = str(item)
                pass
            else:
                item = int(item)
                if item/16 == 0:
                    item = '0'+str(hex(item)[2:])
                else:
                    item = str(hex(item)[2:])
            res = res+item
        save_res[key] = res
    for key in save_res:
        if save_res[key] != '':
            sql_table = sql_table+key+','
            sql_values = sql_values+'\''+save_res[key]+'\''+','
        else:
            pass
    sql_table = sql_table[0:-1]
    sql_values = sql_values[0:-1]
    sql_insert = 'insert into '+table_info+'('+sql_table+') values('+sql_values+');'
    #print sql_insert    
    try:
        cur.execute(sql_insert)
        conn.commit()
    except Exception as e:
        print 'insert data failed!'
        conn.rollback
    
    finally:
        conn.close

def int_list_to_str(content):
    #getting this report time 
    this_report_time = ''
    for item in content:
        if item == 0:
            item = '0' + str(item)
        elif item/10 == 0:
            item = '0' + str(item)
        this_report_time = this_report_time + str(item)
    return (this_report_time,)

def get_sql_dict(terminal_request, content, str_msg):
    '''
    make a mysql sentence dict
    '''
    car_actual_msg = {
            'time_pi':terminal_request['time_pi'],
            'client_msg_vin':terminal_request['client_msg_vin'],
            'time_ter':terminal_request['time_ter'],
            'time_interval':terminal_request['interval_time'],
            'client_msg_id':terminal_request['client_msg_id'],
            #'msg_content':content[6:],
            }
    for k,v in str_msg.items():
        k = 'data_type' + str(k)
        car_actual_msg[k] = (v,)
    return car_actual_msg
        
class Split_msg_to_str:
    def __init__(self,content):
        self.con = content
    def split_con(self):
        self.con = list(self.con)
        self.con.append(23)
        num = 6
        con_appear = {}
        split_msg_to_str = Split_msg_to_str(1)
        while self.con[num] != 23:
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
                break
        return con_appear

    def int_list_to_hex_str(self, data):
        return_hex_str = ''
        for item in data:
            if int(item) <=  15:
                item = hex(item)[2:]
                item = '0' + str(item)
            else:
                item = str(hex(item)[2:])
            return_hex_str = return_hex_str + item
        return return_hex_str
