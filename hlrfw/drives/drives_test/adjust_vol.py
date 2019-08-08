#!coding:utf8

from smbus2 import SMBusWrapper

#voltage maybe is 10.3V
with SMBusWrapper(1) as bus:
    bus.write_byte_data(0x18, 0, 255)