#!/bin/bash
path=/home/pi/hlrfw/scripts/platform_service_script

sudo chmod  777 -R $path
sudo $path/auto_timing stop
sudo $path/gbtele stop
sudo $path/jtt808 stop
sudo $path/sirun stop
sudo $path/sharengo stop
sudo $path/zdmon stop
#sudo $path/zdgbt2 stop
sudo $path/serial stop
$path/can_player stop