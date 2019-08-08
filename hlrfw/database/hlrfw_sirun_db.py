from os import path
from sys import path as path2
path2.append(path.abspath(path.join(__file__,'../..')))
#d = path.abspath(path.dirname(__file__))
#d2 = path.abspath(path.join(__file__,'../..'))
from configs.db_config import DB_TYPE,DB_HOST,DB_USER,DB_PASSWORD,DB_PORT,DB_NAME
from configs.db_config import SIRUN_TABLE_DICT

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

class SirunRegisterTable(Base):
    __tablename__ = SIRUN_TABLE_DICT['register']
    id = Column(Integer,primary_key=True,autoincrement=True)
    dispatch_creation_time = Column(String(16))
    bid = Column(String(8))
    message_flag = Column(String(2))
    event_creation_time = Column(String(8))
    message_counter = Column(String(4))
    service_data_length = Column(String(4))
    result = Column(String(2))
    security_version = Column(String(2))
    peraeskey = Column(String(32))
    vin = Column(String(34))
    t_box_sn = Column(String(58))
    imsi = Column(String(30))
    roll_number = Column(String(32))
    iccid = Column(String(40))
    callback_number = Column(String(32))
    
    
class SirunLoginTable(Base):
    __tablename__ = SIRUN_TABLE_DICT['login']
    id = Column(Integer,primary_key=True,autoincrement=True)
    time_ter = Column(Integer,primary_key=True)
    time_pi = Column(Integer,primary_key=True)
    bid = Column(String(8))
    message_flag = Column(String(2))
    event_creation_time = Column(String(8))
    message_counter = Column(String(4))
    service_data_length = Column(String(4))
    security_version = Column(String(2))
    dispatch_creation_time = Column(String(20))
    login_req = Column(String(2))
    key_type = Column(String(2))
    t_box_sn = Column(String(58))
    vin = Column(String(34))
    t_box_random = Column(String(32))
    t_box_random_md5 = Column(String(32))
    platrandom = Column(String(32))
    serial_up = Column(String(32))
    acess_key = Column(String(32))
    aes_random = Column(String(32))
    timestamp = Column(String(2))
    work_window = Column(String(16))
    link_heart_beat = Column(String(16))
    
class SirunLogoutTable(Base):
    __tablename__ = SIRUN_TABLE_DICT['logout']
    id = Column(Integer,primary_key=True,autoincrement=True)
    time_ter = Column(Integer,primary_key=True)
    time_pi = Column(Integer,primary_key=True)
    bid = Column(String(8))
    message_flag = Column(String(2))
    event_creation_time = Column(String(8))
    message_counter = Column(String(4))
    service_data_length = Column(String(4))
    security_version = Column(String(2))
    dispatch_creation_time = Column(String(8))

class SirunActualMsg(Base):
    __tablename__ = SIRUN_TABLE_DICT['actual_msg']
    id = Column(Integer,primary_key=True,autoincrement=True)
    time_ter = Column(Integer,primary_key=True)
    time_pi = Column(Integer,primary_key=True)
    version_id = Column(String(8))
    fixtime = Column(String(8))
    position = Column(String(26))
    car_status = Column(String(16))
    car_data = Column(String(255))
    
Base.metadata.create_all(engine)
