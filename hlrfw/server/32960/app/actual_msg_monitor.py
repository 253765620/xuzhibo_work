#!coding=utf-8

def get_extremum_cell_vol_id(val, extremum):
    '''
    - 返回指定值的位置
    - [1,2,3,4,5], 3 return 2
    '''
    location = 1
    for item in val:
        if item == extremum:
            break
        location = location + 1
    return location

def get_plural_data(val, deviant=0):
    '''
    - 计算偏移量的数据
    '''
    arr = val[0].split('x')
    arr = arr[:-1]
    arr = map(int, arr)
    if deviant != 0:
        location = 0
        for item in arr:
            item = int(item) - deviant
            arr[location] = item
            location = location + 1
    return arr

def get_unit_data(val):
    '''
    - 获取单元数据
    '''
    if isinstance(val[0], int):
        val = val[0]
    else:
        val = int(val[0][:-1])
    return val
    

def chargeable_sys(msg_dict):
    '''
    判断终端上报数据的正确性
    输入：数据字典
    输出：一个代表错误状态的二进制数
    '''
    flag_2 = flag_6 = flag_8 = flag_9 = True
    #终端与服务器时间差
    time_interval = float(msg_dict['time_interval'][0])
    #1
    total_current_1 = get_unit_data(msg_dict['total_current_1']) - 10000
    speed_1 = get_unit_data(msg_dict['speed_1'])
    cumulative_mileage_1 = get_unit_data(msg_dict['cumulative_mileage_1'])
    total_vol_1 = get_unit_data(msg_dict['total_vol_1'])
    total_power = total_current_1 * total_vol_1
    DC_state_1 = get_unit_data(msg_dict['DC_state_1'])
    vehicle_state_1 = get_unit_data(msg_dict['vehicle_state_1'])
    charge_state_1 = get_unit_data(msg_dict['charge_state_1'])
    SOC_1 = get_unit_data(msg_dict['SOC_1'])
    operation_mode_1 = get_unit_data(msg_dict['operation_mode_1'])
    accelerator_pedal_trip_value_1 = get_unit_data(msg_dict['accelerator_pedal_trip_value_1'])
    brake_pedal_state_1 = get_unit_data(msg_dict['brake_pedal_state_1'])
    gear_bin_1 = bin(get_unit_data(msg_dict['gear_1']) + 2**8)
    gear_state = int(gear_bin_1,2) % 16
    
    #2
    #驱动电机个数
    if 'motor_num_2' in msg_dict:
        motor_num_2 = get_unit_data(msg_dict['motor_num_2'])
        motor_state_2 = get_plural_data(msg_dict['motor_state_2'])
        motor_controller_temperature_2 = get_plural_data(msg_dict['motor_controller_temperature_2'], 40)
        motor_speed_2 = get_plural_data(msg_dict['motor_speed_2'], 20000)
        motor_torque_2 = get_plural_data(msg_dict['motor_torque_2'], 20000)
        motor_temperature_2 = get_plural_data(msg_dict['motor_temperature_2'], 40)
        motor_controller_input_vol_2 = get_plural_data(msg_dict['motor_controller_input_vol_2'])
        motor_controller_current_2 = get_plural_data(msg_dict['motor_controller_current_2'], 10000)
    else:
        flag_2 = False
    #6
    #计算出整型数据
    if 'max_battery_vol_6' in msg_dict:
        max_battery_vol_6 = get_unit_data(msg_dict['max_battery_vol_6'])
        min_battery_vol_6 = get_unit_data(msg_dict['min_battery_vol_6'])
        #单字节数据
        max_vol_battery_id_6 = get_unit_data(msg_dict['max_vol_battery_id_6'])
        min_vol_battery_id_6 = get_unit_data(msg_dict['min_vol_battery_id_6'])
        max_temperature_6 = get_unit_data(msg_dict['max_temperature_6'])
        min_temperature_6 = get_unit_data(msg_dict['min_temperature_6'])
        max_temperature_probe_id_6 = get_unit_data(msg_dict['max_temperature_probe_id_6'])
        min_temperature_probe_id_6 = get_unit_data(msg_dict['min_temperature_probe_id_6'])
    else:
        flag_6 = False

    #8
    if 'chargeable_subsys_num_8' in msg_dict:
        chargeable_subsys_num_8 = get_unit_data(msg_dict['chargeable_subsys_num_8'])
        frame_unit_cell_num_8 = get_unit_data(msg_dict['frame_unit_cell_num_8'])
        unit_cell_vol_8 = get_plural_data(msg_dict['unit_cell_vol_8'])
        frame_cell_id_8 = get_unit_data(msg_dict['frame_cell_id_8'])
        #计算所有单体电池电压的和以及极值电压
        unit_cell_vol_sum_8 = sum(unit_cell_vol_8)
        max_unit_cell_vol_8 = max(unit_cell_vol_8)
        min_unit_cell_vol_8 = min(unit_cell_vol_8)
        max_unit_cell_vol_id_8 = get_extremum_cell_vol_id(unit_cell_vol_8, max_unit_cell_vol_8)
        min_unit_cell_vol_id_8 = get_extremum_cell_vol_id(unit_cell_vol_8, min_unit_cell_vol_8)
    else:
        flag_8 = False

    #9
    #获取探针温度的极值
    if 'chargeable_probe_num_9' in msg_dict:
        chargeable_probe_num_9 = get_unit_data(msg_dict['chargeable_probe_num_9'])
        temperature_9 = get_plural_data(msg_dict['chargeable_probe_temperature_9'])
        max_temperature_9 = max(temperature_9)
        min_temperature_9 = min(temperature_9)
        max_temperature_id_9 = get_extremum_cell_vol_id(temperature_9, max_temperature_9)
        min_temperature_id_9 = get_extremum_cell_vol_id(temperature_9, min_temperature_9) 
    else:
        flag_9 = False
    #判断数据正确性
    test_res = 0b0
    
    if time_interval > 10:
        test_res = test_res + 2**0

    #车辆启动
    if vehicle_state_1 == 1:
        if DC_state_1 != 1:
            test_res = test_res + 2**1
        if '2_motor_id' not in msg_dict:
            test_res = test_res + 2**2

    #车辆熄火
    if vehicle_state_1 == 2:
        if DC_state_1 != 2:
            test_res = test_res + 2**3
        if total_current_1 != 0:
            test_res = test_res + 2**4

    #停车充电
    if charge_state_1 == 1:
        if total_current_1 >= 0:
            test_res = test_res + 2**5
        if '2_motor_id' in msg_list:
            for i in range(motor_num_2):
                if motor_state_2[i] != 3 or motor_speed_2[i] != 0 or motor_torque_2[i] != 0 or motor_controller_current_2[i] != 0:
                    test_res = test_res + 2**6
                    break

    #行驶充电
    if charge_state_1 == 2:
        if flag_2:
            for i in range(motor_num_2):
                if motor_state_2[i] != 3:
                    test_res = test_res + 2**7
                    break

    #充电完成时
    if charge_state_1 == 4:
        if total_current_1 < 0:
            test_res = test_res + 2**8
        if SOC_1 != 100:
            test_res = test_res + 2**9

    #纯电模式时
    if operation_mode_1 == 1:
        if '4_engine_state' in msg_dict:
            test_res = test_res + 2**10
            
    #停车时
    if speed_1 == 0:
        if gear_state != 0 and gear_state != 15:
            test_res = test_res + 2**11

    #跑车时
    if speed_1 > 0:
        if gear_state != 14 and gear_state != 13:
            if (gear_state-1) not in range(6):
                 test_res = test_res + 2**12
        if brake_pedal_state_1 == 0:
            for i in range(motor_num_2):
                if motor_state_2[i] != 1:
                    test_res = test_res + 2**13
                    break
        if brake_pedal_state_1 == 1:
            for i in range(motor_num_2):
                if motor_state_2[i] != 2:
                    test_res = test_res + 2**14
                    break
                
    #车速不应大于2200          
    if speed_1 > 2200:
        test_res = test_res + 2**15
        
    #里程不应为0
    if cumulative_mileage_1 == 0:
        test_res = test_res + 2**16

    #判断单体电池电压和
    if flag_8:
        if abs(unit_cell_vol_sum_8-total_vol_1*100) > 5000:
            test_res = test_res + 2**17

    #加速时
    if accelerator_pedal_trip_value_1 != 0:
        if gear_bin_1[-6] != '1':
            test_res = test_res + 2**18

    #制动时
    if brake_pedal_state_1 != 0:
        if gear_bin_1[-5] != '1':
            test_res = test_res + 2**19

    if flag_2:
        for i in range(motor_num_2):
            #电机耗电
            if motor_state_2[i] == 1:
                if motor_controller_temperature_2[i] == 215 or motor_controller_temperature_2[i] == 0:
                    test_res = test_res + 2**20
                if (gear_state-1) in range(6):
                    if motor_speed_2[i] < 0:
                        test_res = test_res + 2**21
                    if motor_torque_2[i] < 0:
                        test_res = test_res + 2**22
                elif gear_state == 13:
                    if motor_speed_2[i] > 0:
                        test_res = test_res + 2**23
                    if motor_torque_2[i] > 0:
                        test_res = test_res + 2**24
                if motor_temperature_2[i] == 215 or motor_temperature_2[i] == 0:
                    test_res = test_res + 2**25
                if motor_controller_input_vol_2[i] == 255 or motor_controller_input_vol_2[i] == 0:
                    test_res = test_res + 2**26
                if motor_controller_current_2[i] > total_current_1:
                    test_res = test_res + 2**27
                if motor_controller_input_vol_2[i]*motor_controller_current_2[i] > total_power:
                    test_res = test_res + 2**28
            
            #电机发电
            if motor_state_2[i] == 2:
                if motor_controller_temperature_2[i] == 215 or motor_controller_temperature_2[i] == 0:
                    test_res = test_res + 2**29
                if (gear_state-1) in range(6):
                    if motor_speed_2[i] > 0:
                        test_res = test_res + 2**30
                    if motor_torque_2[i] > 0:
                        test_res = test_res + 2**31
                elif gear_state == 13:
                    if motor_speed_2[i] < 0:
                        test_res = test_res + 2**32
                    if motor_torque_2[i] < 0:
                        test_res = test_res + 2**33
                if motor_temperature_2[i] == 215 or motor_temperature_2[i] == 0:
                    test_res = test_res + 2**34
                if motor_controller_input_vol_2[i] == 255 or motor_controller_input_vol_2[i] == 0:
                    test_res = test_res + 2**35
                if motor_controller_current_2[i] > total_current_1:
                    test_res = test_res + 2**36
                if motor_controller_input_vol_2[i]*motor_controller_current_2[i] > total_power:
                    test_res = test_res + 2**37
             
            #电机关闭
            if motor_state_2[i] == 3:
                if abs(motor_speed_2[i]) > 1:
                    test_res = test_res + 2**38
                if abs(motor_torque_2[i]) > 1:
                    test_res = test_res + 2**39
                if motor_controller_input_vol_2[i] == 255 or motor_controller_input_vol_2[i] == 0:
                    test_res = test_res + 2**40
                if motor_controller_current_2[i] != 0:
                    test_res = test_res + 2**41
                if motor_controller_temperature_2[i] == 215:
                    test_res = test_res + 2**42
    #极值数据
    if flag_6 and flag_8:
        if max_unit_cell_vol_8 != max_battery_vol_6 or max_unit_cell_vol_id_8 != max_vol_battery_id_6:
            test_res = test_res + 2**43
            
        if min_unit_cell_vol_8 != min_battery_vol_6 or min_unit_cell_vol_id_8 != min_vol_battery_id_6:
            test_res = test_res + 2**44

        if max_temperature_9 != max_temperature_6 or max_temperature_id_9 != max_temperature_probe_id_6:
            test_res = test_res + 2**45
            
        if min_temperature_9 != min_temperature_6 or min_temperature_id_9 != min_temperature_probe_id_6:
            test_res = test_res + 2**46

    #可充电储能装置电压数据
    if flag_8:
        if len(unit_cell_vol_8) != frame_unit_cell_num_8:
            test_res = test_res + 2**47
        for item in unit_cell_vol_8:
            if item == 255 or item == 0:
                test_res = test_res + 2**48
                break

    #可充电储能装置温度数据
    if flag_9:
        if len(temperature_9) != chargeable_probe_num_9:
            test_res = test_res + 2**49
        for item in temperature_9:
            if item == 255:
                test_res = test_res + 2**50
                break
            
    msg_dict['test_res'] = bin(test_res)[2:]
    #print msg_dict['test_res']
    return msg_dict
