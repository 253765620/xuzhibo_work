'''
- 自动化测试中所用到的各种脚本介绍
- auto_timing.sh: 自动校时, 注意，Pi上需要安装ntpdate
- can-start.sh: can开启脚本
- collect_current_data.py: 收集电流数据, 并且插入数据库
- confirm_ip_port.sh: git代码同步的时候执行的脚本
- creat_database.sh: 建立国标, 部标等平台的数据库
- disable_platform.sh/enable_platform.sh: 控制国标, 部标等平台的开启和关闭
- modify_thingsboard_attr.py/rfcase_sh.py: 修改thingsboard上的属性值
- serial_handle.py: 串口数据收发控制平台
- test_case_control.py: 自动化测试流程控制脚本
- upload_extra_addr_to_thingsboard.sh: 上传外网地址，到thingsboard，之前主要是用于网页串口采集工具
- upload_test_report.py: 上传报告到gitlab pages服务器
'''