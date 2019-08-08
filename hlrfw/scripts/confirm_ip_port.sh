#!/bin/bash

cd /home/pi/hlrfw
git stash
git pull
#myip=`/sbin/ifconfig -a|grep inet|grep -v 127.0.0.1|grep -v inet6 | awk '{print $2}' | tr -d "addr:"`
#sed -ie "s#^myip = .*#myip = ${myip##*.}#g" /home/pi/hlrfw/configs/ip_config.py

sh /home/pi/hlrfw/scripts/can_script/can_update_so.sh

if [ ! -d /home/pi/rfcase_script/rfcase ]
then
	mkdir /home/pi/rfcase_script
	cd /home/pi/rfcase_script
	git clone git@192.168.3.116:hopelead/rfcase.git
	cd /home/pi/rfcase_script/rfcase
	bash /home/pi/rfcase_script/rfcase/rfcase_init.sh

else
	cd /home/pi/rfcase_script/rfcase
	git pull
	bash rfcase_init.sh
fi
echo confirm ip end