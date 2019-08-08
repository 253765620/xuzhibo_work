#!/bin/bash

cd /home/pi

if [ -d "/home/pi/nodesim_so" ]
then
	git stash
	cd /home/pi/nodesim_so
	git pull
else
	git clone git@192.168.3.116:lvyou/nodesim_so.git
	cd /home/pi/nodesim_so
fi

if [ -f "/home/pi/nodesim_so/libnodesim.so" ]
then
	sudo cp -f /home/pi/nodesim_so/libnodesim.so /usr/lib/libnodesim.so
else
	echo "not find libnodesim.so"
fi

if [ -f "/home/pi/nodesim_so/libwiringPi.so" ]
then
	sudo cp -f /home/pi/nodesim_so/libwiringPi.so /usr/lib/libwiringPi.so
else
	echo "not find libnodesim.so"
fi