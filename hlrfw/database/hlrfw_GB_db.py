from os import path
from sys import path as path2
path2.append(path.abspath(path.join(__file__,'../..')))
from configs.db_config import DB_TYPE,DB_HOST,DB_USER,DB_PASSWORD,DB_PORT,DB_NAME
from configs.db_config import GB_TABLE_DICT

try:
    import pymysql
    
    DB_INFO = '%s://%s:%s@%s:%i/%s' % (DB_TYPE, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
except Exception as e:
    print(e)
    print("Run 'sudo pip install pymysql' to fixed this!")

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import Column, String, Integer
    from sqlalchemy.orm import relationships

    engine = create_engine(DB_INFO)
    Base = declarative_base()
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()  # For view import ...
except ImportError as msg:
    print(msg)
    print("Run 'sudo pip install sqlalchemy' to fixed this!")
try:
    conn = pymysql.connect(
                host = 'localhost',
                port = 3306,
                user = 'root',
                passwd = 'zhangroot',
                )
    cur = conn.cursor()
    cur.execute('create database hlrfw_test default character set utf8')
    cur.close()
except:
    print('database is already created!')
    

class GBLoginTable(Base):
    __tablename__ = GB_TABLE_DICT['login']
    id = Column(Integer,primary_key=True,autoincrement=True)
    time_ter = Column(Integer,primary_key=True)
    time_pi = Column(Integer,primary_key=True)
    time_interval = Column(Integer)
    client_msg_vin = Column(String(34))
    login_id = Column(String(4))
    iccid = Column(String(40))
    num_subsys = Column(String(4))
    len_coding = Column(String(4))
    sys_coding = Column(String(255))
    
class GBLogoutTable(Base):
    __tablename__ = GB_TABLE_DICT['logout']
    id = Column(Integer,primary_key=True,autoincrement=True)
    time_ter = Column(Integer,primary_key=True)
    time_pi = Column(Integer,primary_key=True)
    time_interval = Column(Integer)
    client_msg_vin = Column(String(34))
    login_id = Column(String(4))
    ICCID = Column(String(40))
    num_subsys = Column(String(4))
    len_coding = Column(String(4))
    sys_coding = Column(String(255))
    
class GBHeartbeat(Base):
    __tablename__ = GB_TABLE_DICT['heartbeat']
    id = Column(Integer,primary_key=True,autoincrement=True)
    time_pi = Column(Integer,primary_key=True)
    client_msg_vin = Column(String(34))
    
class GBTerCorTime(Base):
    __tablename__ = GB_TABLE_DICT['ter_cor_time']
    id = Column(Integer,primary_key=True,autoincrement=True)
    time_pi = Column(Integer,primary_key=True)
    client_msg_vin = Column(String(34))

class GBActualMsg(Base):
    __tablename__ = GB_TABLE_DICT['actual_msg']
    id = Column(Integer,primary_key=True,autoincrement=True)
    time_ter = Column(Integer,primary_key=True)
    time_pi = Column(Integer,primary_key=True)
    test_res = Column(String(255))
    client_msg_vin = Column(String(34))
    time_interval = Column(Integer)
    client_msg_id = Column(String(5))
    vehicle_state_1 = Column(String(5))
    charge_state_1 = Column(String(5))
    operation_mode_1 = Column(String(5))
    speed_1 = Column(String(5))
    cumulative_mileage_1 = Column(String(9))
    total_vol_1 = Column(String(6))
    total_current_1 = Column(String(6))
    SOC_1 = Column(String(5))
    DC_state_1 = Column(String(5))
    gear_1 = Column(String(5))
    insulation_resistance_1 = Column(String(15))
    accelerator_pedal_trip_value_1 = Column(String(5))
    brake_pedal_state_1 = Column(String(5))
    motor_num_2 = Column(String(2))
    motor_id_2 = Column(String(255))
    motor_state_2 = Column(String(255))
    motor_controller_temperature_2 = Column(String(255))
    motor_speed_2 = Column(String(255))
    motor_torque_2 = Column(String(255))
    motor_temperature_2 = Column(String(255))
    motor_controller_input_vol_2 = Column(String(255))
    motor_controller_current_2 = Column(String(255))
    fuel_cell_vol_3 = Column(String(4))
    fuel_cell_current_3 = Column(String(4))
    fuel_consumption_rate_3 = Column(String(4))
    fuel_cell_probe_num_3 = Column(String(4))
    probe_temperature_3 = Column(String(255))
    H_sys_max_temperature_3 = Column(String(4))
    H_sys_max_temperature_probe_id_3 = Column(String(2))
    H_max_concentration_3 = Column(String(4))
    H_max_concentration_sensor_id_3 = Column(String(2))
    H_max_pressure_3 = Column(String(4))
    H_max_pressure_sensor_id_3 = Column(String(2))
    DC_state_3 = Column(String(2))
    engine_state_4 = Column(String(2))
    rotation_speed_4 = Column(String(4))
    fuel_consumption_rate_4 = Column(String(4))
    position_state_5 = Column(String(2))
    longitude_5 = Column(String(12))
    latitude_5 = Column(String(12))
    max_vol_subsys_id_6 = Column(String(3))
    max_vol_battery_id_6 = Column(String(3))
    max_battery_vol_6 = Column(String(5))
    min_vol_subsys_id_6 = Column(String(3))
    min_vol_battery_id_6 = Column(String(3))
    min_battery_vol_6 = Column(String(5))
    max_temperature_subsys_id_6 = Column(String(3))
    max_temperature_probe_id_6 = Column(String(3))
    max_temperature_6 = Column(String(3))
    min_temperature_subsys_id_6 = Column(String(3))
    min_temperature_probe_id_6 = Column(String(3))
    min_temperature_6 = Column(String(3))
    max_alarm_level_7 = Column(String(2))
    com_alarm_sign_7 = Column(String(8))
    chargeable_device_fault_num_7 = Column(String(3))
    chargeable_device_fault_list_7 = Column(String(255))
    motor_fault_num_7 = Column(String(3))
    motor_fault_list_7 = Column(String(255))
    engine_fault_num_7 = Column(String(3))
    engine_fault_list_7 =Column(String(255)) 
    other_fault_num_7 = Column(String(3))
    other_fault_list_7 = Column(String(255))
    chargeable_subsys_num_8 = Column(String(3))
    chargeable_subsys_id_8 = Column(String(255))
    chargeable_service_vol_8 = Column(String(255))
    chargeable_subsys_current_8 = Column(String(255))
    unit_cell_num_8 = Column(String(255))
    frame_cell_id_8 = Column(String(255))
    frame_unit_cell_num_8 = Column(String(3))
    unit_cell_vol_8 = Column(String(500))
    chargeable_subsys_num_9 = Column(String(3))
    chargeable_subsys_id_9 = Column(String(255))
    chargeable_probe_num_9 = Column(String(255))
    chargeable_probe_temperature_9 = Column(String(255))

Base.metadata.create_all(engine)
