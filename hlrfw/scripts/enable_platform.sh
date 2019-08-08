#!/bin/bash
path=/home/pi/hlrfw/scripts/platform_service_script

sudo chmod  777 -R $path
$path/gbtele start
$path/jtt808 start
$path/sirun start
$path/sharengo start
$path/zdmon start
#$path/zdgbt2 start
$path/auto_timing start
$path/serial start
$path/can_player start