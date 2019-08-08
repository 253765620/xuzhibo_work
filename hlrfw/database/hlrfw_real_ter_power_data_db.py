from os import path
from sys import path as path2
path2.append(path.abspath(path.join(__file__,'../..')))
from configs.db_config import DB_TYPE,DB_HOST,DB_USER,DB_PASSWORD,DB_PORT,DB_NAME
import time

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
    
class CollectPowerTable(Base):
    __tablename__ = 'real_ter_power_data'
    id      = Column(Integer,primary_key=True,autoincrement=True)
    time_pi = Column(String(14))
    current = Column(String(10))
    voltage = Column(String(10))
    
Base.metadata.create_all(engine)
