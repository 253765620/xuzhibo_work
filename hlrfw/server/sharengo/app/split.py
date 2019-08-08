from core.split import SplitBase


class PositionSplit(SplitBase):
    # Required override the parent attribute
    split_list = ['alarm/4', 'status/4', 'latitude/4',
                  'longitude/4', 'altitude/2', 'speed/2',
                  'direction/2', 'timestamp/6']

    # Optional override
    # prefix = 'my_'


# class TerminalInfoSplit(SplitBase):
#     split_list = ['']
#
#

class TerminalAttributeSplit(SplitBase):
    split_list = ['ter_type/2', 'manuf_id/5', 'ter_model/20',
                  'ter_id/7', 'icc_id/10', 'ter_hardware_v_len/1',
                  'ter_hardware_v/#ter_hardware_v_len',
                  'ter_fixed_v_len/1', 'ter_fixed_v/#ter_fixed_v_len',
                  'gnss/1', 'gnss_attr/1'
                  ]
class Split_msg:
    def __init__(self,content):
        self.con = content
    def split_con(self):
        self.con = list(self.con)
        self.con.append(23)
        num = 6
        con_appear = {}
        while self.con[num] != 23:
            if self.con[num] == 1:
                con_appear['1'] = self.con[num+1:num+21]
                num = num+21
            if self.con[num] == 2:
                num = num+2
                num2 = int(self.con[num-1])
                self.con_res = []
                self.con_res.append(num2)
                for i in range(num2):
                    self.con_res.append(self.con[num+1:num+12])
                    num = num+12
                con_appear['2'] = self.con_res
            if self.con[num] == 3:
                num3 = 19+int(self.con[num+8])
                con_appear['3'] = self.con[num+1:num+num3]
                num = num+num3
            if self.con[num] == 4:
                con_appear['4'] = self.con[num+1:num+6]
                num = num+6
            if self.con[num] == 5:
                con_appear['5'] = self.con[num+1:num+10]
                num = num+10
            if self.con[num] == 6:
                con_appear['6'] = self.con[num+1:num+15]
                num = num+15
            if self.con[num] == 7:
                self.con_res = []
                self.con_res.append(self.con[num+1:num+6])
                num = num+6
                for i in range(4):
                    self.con_res.append(self.con[num:num+int(self.con[num])*4+1])
                    num = num+int(self.con[num])*4+1
                con_appear['7'] = self.con_res
            if self.con[num] == 8:
                num8 = int(self.con[num+1])
                num = num+2
                self.con_res = []
                self.con_res.append(num8)
                for i in range(num8):
                    num81 = int(self.con[num+9])
                    self.con_res.append(self.con[num:num+2*num81+10])
                    num = num+2*num81+10
                con_appear['8'] = self.con_res
            if self.con[num] == 9:
                num9 = int(self.con[num+1])
                num = num+2
                self.con_res = []
                self.con_res.append(num9)
                for i in range(num9):
                    num91 = int(self.con[num+1])*256+int(self.con[num+2])
                    self.con_res.append(self.con[num:num+3+num91])
                    num = num+3+num91
                con_appear['9'] = self.con_res
                
            if self.con[num] == 80:
                num8 = int(self.con[num+1]*256+self.con[num+2])
                con_appear['8'] = self.con[num+1:num+num8+3]
                num = num+num8+3
            return con_appear
        #print con_appear
        #print num,self.con[num]


if __name__ == '__main__':
    sample1 = (1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 21, 22, 22, 1, 5, 21, 17, 21)
    instance1 = PositionSplit(sample1)
    print instance1.result
