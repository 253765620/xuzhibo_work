#!/bin/bash

while true
do
	sleep 60s
	extra_addr=`curl ident.me`
	python3.7 /home/pi/hlrfw/scripts/modify_thingsboard_attr.py extra_addr ${extra_addr}
	sleep	1h
done