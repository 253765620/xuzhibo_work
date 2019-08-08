#!coding=utf-8
from core.split import SplitBase
from utils.tools import split_hex_str_to_dict
from utils.tools import merge_dict
class PositionSplit(SplitBase):
    # Required override the parent attribute
    split_list = ['alarm/4', 'status/4', 'latitude/4',
                  'longitude/4', 'altitude/2', 'speed/2',
                  'direction/2', 'timestamp/6']


class TerminalAttributeSplit(SplitBase):
    split_list = ['ter_type/2', 'manuf_id/5', 'ter_model/20',
                  'ter_id/7', 'icc_id/10', 'ter_hardware_v_len/1',
                  'ter_hardware_v/#ter_hardware_v_len',
                  'ter_fixed_v_len/1', 'ter_fixed_v/#ter_fixed_v_len',
                  'gnss/1', 'gnss_attr/1'
                  ]

class Split_msg:
    '''
    - 分解国标数据，用于判断实时数据是否合理
    - 其实和另一个数据解析有点重合，后期可以考虑合并
    '''
    def __init__(self,content):
        self.con = content
        
    def split_con(self):
        self.con = list(self.con)[6:]
        self.con.append(23)
        num = 0
        con_appear = {}
        n = 0
        while self.con[num] != 23:
            if n > 20:
                break
            n = n + 1
            if self.con[num] == 1:
                content1 = self.con[num+1:num+21]
                config1 = {
                    'vehicle_state_1' : ('B',1,(0,1)),
                    'charge_state_1' : ('B',1,(1,2)),
                    'operation_mode_1' : ('B',1,(2,3)),
                    'speed_1' : ('W',2,(3,5)),
                    'cumulative_mileage_1' : ('DW',4,(5,9)),
                    'total_vol_1' : ('W',2,(9,11)),
                    'total_current_1' : ('W',2,(11,13)),
                    'SOC_1' : ('B',1,(13,14)),
                    'DC_state_1' : ('B',1,(14,15)),
                    'gear_1' : ('B',1,(15,16)),
                    'insulation_resistance_1' : ('W',2,(16,18)),
                    'accelerator_pedal_trip_value_1' : ('B',1,(18,19)),
                    'brake_pedal_state_1' : ('B',1,(19,20)),
                    }
                mydict = split_hex_str_to_dict(content1, config1)
                con_appear = dict(con_appear, **mydict)
                num = num+21
                continue
                
            if self.con[num] == 2:
                num = num + 2
                motor_num = int(self.con[num-1])
                content2_total = self.con[num:num+12*motor_num]
                config2 = {
                    'motor_id_2' : ('B',1,(0,1)),
                    'motor_state_2' : ('B',1,(1,2)),
                    'motor_controller_temperature_2' : ('B',1,(2,3)),
                    'motor_speed_2' : ('W',2,(3,5)),
                    'motor_torque_2' : ('W',2,(5,7)),
                    'motor_temperature_2' : ('B',1,(7,8)),
                    'motor_controller_input_vol_2' : ('W',2,(8,10)),
                    'motor_controller_current_2' : ('W',2,(10,12)),
                    }
                mydict2 = {
                    'motor_num_2' : ((motor_num,)),
                    'motor_id_2' : (),
                    'motor_state_2' : (),
                    'motor_controller_temperature_2' : (),
                    'motor_speed_2' : (),
                    'motor_torque_2' : (),
                    'motor_temperature_2' : (),
                    'motor_controller_input_vol_2' : (),
                    'motor_controller_current_2' : (),
                    }
                location = 0
                for i in range(motor_num):
                    content2 = content2_total[location:location+12]
                    mydict = split_hex_str_to_dict(content2, config2)
                    mydict2 = merge_dict(mydict2, mydict)
                    location = location + 12
                con_appear = dict(con_appear, **mydict2)
                num = num + 12*motor_num
                continue
                
            if self.con[num] == 3:
                location = int(self.con[num+8]) + 256*int(self.con(num+7))
                num3 = 19 + location
                content3 = self.con[num+1:num+num3]
                config3 = {
                    'fuel_cell_vol_3' : ('W',2,(0,2)),
                    'fuel_cell_current_3' : ('W',2,(2,4)),
                    'fuel_consumption_rate_3' : ('W',2,(4,6)),
                    'fuel_cell_probe_num_3' : ('W',2,(6,8)),
                    'probe_temperature_3' : ('B',1,(8,location+8)),
                    'H_sys_max_temperature_3' : ('W',2,(location+8,location+10)),
                    'H_sys_max_temperature_probe_id_3' : ('B',1,(location+10,location+11)),
                    'H_max_concentration_3' : ('W',2,(location+11,location+13)),
                    'H_max_concentration_sensor_id_3' : ('B',1,(location+13,location+14)),
                    'H_max_pressure_3' : ('W',2,(location+14,location+16)),
                    'H_max_pressure_sensor_id_3' : ('B',1,(location+16,location+17)),
                    'DC_state_3' : ('B',1,(location+17,location+18)),
                    }
                mydict3 = split_hex_str_to_dict(content3, config3)
                con_appear = dict(con_appear, **mydict3)
                num = num+num3
                continue
                
            if self.con[num] == 4:
                content4 = self.con[num+1:num+6]
                config4 = {
                    'engine_state_4' : ('B',1,(0,1)),
                    'rotation_speed_4' : ('W',2,(1,3)),
                    'fuel_consumption_rate_4' : ('W',2,(3,5)),
                    }
                mydict4 = split_hex_str_to_dict(content4, config4)
                con_appear = dict(con_appear, **mydict4)
                num = num+6
                continue
                
            if self.con[num] == 5:
                content5 = self.con[num+1:num+10]
                config5 = {
                    'position_state_5' : ('B',1,(0,1)),
                    'longitude_5' : ('DW',4,(1,5)),
                    'latitude_5' : ('DW',4,(5,9)),
                    }
                mydict5 = split_hex_str_to_dict(content5, config5)
                con_appear = dict(con_appear, **mydict5)
                num = num + 10
                continue
                
            if self.con[num] == 6:
                content6 = self.con[num+1:num+15]
                config6 = {
                    'max_vol_subsys_id_6' : ('B',1,(0,1)),
                    'max_vol_battery_id_6' : ('B',1,(1,2)),
                    'max_battery_vol_6' : ('W',2,(2,4)),
                    'min_vol_subsys_id_6' : ('B',1,(4,5)),
                    'min_vol_battery_id_6' : ('B',1,(5,6)),
                    'min_battery_vol_6' : ('W',2,(6,8)),
                    'max_temperature_subsys_id_6' : ('B',1,(8,9)),
                    'max_temperature_probe_id_6' : ('B',1,(9,10)),
                    'max_temperature_6' : ('B',1,(10,11)),
                    'min_temperature_subsys_id_6' : ('B',1,(11,12)),
                    'min_temperature_probe_id_6' : ('B',1,(12,13)),
                    'min_temperature_6' : ('B',1,(13,14)),
                    }
                mydict6 = split_hex_str_to_dict(content6, config6)
                con_appear = dict(con_appear, **mydict6)
                num = num+15
                continue
                
            if self.con[num] == 7:
                '''
                msg parameter is to long
                '''
                a = 4*self.con[num+6]
                b = 4*self.con[num+7+a]
                c = 4*self.con[num+8+a+b]
                d = 4*self.con[num+9+a+b+c]
                len7 = 10 + a + b + c + d
                content7 = self.con[num+1:num+len7]
                config7 = {
                    'max_alarm_level_7' : ('B',1,(0,1)),
                    'com_alarm_sign_7' : ('DW',4,(1,5)),
                    'chargeable_device_fault_num_7' : ('B',1,(5,6)),
                    'chargeable_device_fault_list_7' : ('DW',4,(6,6+a)),
                    'motor_fault_num_7' : ('B',1,(6+a,7+a)),
                    'motor_fault_list_7' : ('DW',4,(7+a,7+a+b)),
                    'engine_fault_num_7' : ('B',1,(7+a+b,8+a+b)),
                    'engine_fault_list_7' : ('DW',4,(8+a+b,8+a+b+c)),
                    'other_fault_num_7' : ('B',1,(8+a+b+c,9+a+b+c)),
                    'other_fault_list_7' : ('DW',4,(9+a+b+c,9+a+b+c+d)),
                    }
                mydict7 = split_hex_str_to_dict(content7, config7)
                con_appear = dict(con_appear, **mydict7)
                num = num + len7
                #print mydict7
                #print content7
                
            if self.con[num] == 8:
                subsys_num = self.con[num+1]
                num = num +2
                mydict8 = {
                    'chargeable_subsys_num_8' : ((subsys_num,)),
                    'chargeable_subsys_id_8' : (),
                    'chargeable_service_vol_8' : (),
                    'chargeable_subsys_current_8' : (),
                    'unit_cell_num_8' : (),
                    'frame_cell_id_8' : (),
                    'frame_unit_cell_num_8' : (),
                    'unit_cell_vol_8' : (),
                    }
                for i in range(subsys_num):
                    cell_num = self.con[num+9]
                    subsys_len = 10 + 2*cell_num
                    subsys_content = self.con[num:num+subsys_len]
                    subsys_config = {
                        'chargeable_subsys_id_8' : ('B',1,(0,1)),
                        'chargeable_service_vol_8' : ('W',2,(1,3)),
                        'chargeable_subsys_current_8' : ('W',2,(3,5)),
                        'unit_cell_num_8' : ('W',2,(5,7)),
                        'frame_cell_id_8' : ('W',2,(7,9)),
                        'frame_unit_cell_num_8' : ('B',1,(9,10)),
                        'unit_cell_vol_8' : ('W',2,(10,subsys_len)),
                        }
                    subsys_dict = split_hex_str_to_dict(subsys_content, subsys_config)
                    mydict8 = merge_dict(mydict8, subsys_dict)
                    num = num + subsys_len
                con_appear = dict(con_appear, **mydict8)
                continue
                
            if self.con[num] == 9:
                subsys_num = self.con[num+1]
                num = num + 2
                mydict9 = {
                    'chargeable_subsys_num_9' : ((subsys_num,)),
                    'chargeable_subsys_id_9' : (),
                    'chargeable_probe_num_9' : (),
                    'chargeable_probe_temperature_9' : (),
                    }
                for i in range(subsys_num):
                    probe_num = 256*self.con[num+1] + self.con[num+2]
                    subsys_len = 3 + probe_num
                    subsys_content = self.con[num:num+subsys_len]
                    subsys_config = {
                        'chargeable_subsys_id_9' : ('B',1,(0,1)),
                        'chargeable_probe_num_9' : ('W',2,(1,3)),
                        'chargeable_probe_temperature_9' : ('B',1,(3,subsys_len)),
                        }
                    subsys_dict = split_hex_str_to_dict(subsys_content, subsys_config)
                    mydict9 = merge_dict(mydict9, subsys_dict)
                    num = num + subsys_len
                con_appear = dict(con_appear, **mydict9)
                continue
            else:
                break
              
            '''if self.con[num] == 80:
                num8 = int(self.con[num+1]*256+self.con[num+2])
                con_appear['8'] = self.con[num+1:num+num8+3]
                num = num+num8+3
            '''
        return con_appear


if __name__ == '__main__':
    sample1 = (1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 21, 22, 22, 1, 5, 21, 17, 21)
    instance1 = PositionSplit(sample1)
    print instance1.result
