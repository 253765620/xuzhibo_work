#!/bin/bash
error_device_exist="\"Device with such name already exists!\""
error_count=0 
device=none
deviceid=none
devicetoken=none
#read -p "请输入设备名称（仅限数字和英文字母）:" ${devicename}
if [ ${1} ]
then
	#current=`date "+%Y-%m-%d %H:%M:%S"` 
	#timeStamp=`date -d "$current" +%s `
	currentTimeStamp=`date +%s`
	devicecreate="{\"id\": null,\"createdTime\": ${currentTimeStamp},\"additionalInfo\": {\"description\": \"device test\"},\"tenantId\": {\"entityType\": \"TENANT\",\"id\": \"af25c2c0-e4d3-11e8-9e6e-f57e105a4c2c\"}, \"customerId\": {\"entityType\": \"CUSTOMER\", \"id\": \"0745c7f0-e661-11e8-8a40-6ff32809665d\" }, \"name\": \"${1}\", \"type\": \"DEFAULT\"}"
	jwt_token_msg=$(curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{"username":"tenant@thingsboard.org", "password":"tenant"}' 'http://47.96.109.21:8080/api/auth/login')
	if [ "${jwt_token_msg}" != "" ]
	then
		jwt_token=$(echo ${jwt_token_msg} | jq '.token')
		jwt_token=$(echo ${jwt_token} | sed 's/\"//g')
		authorization=$(echo "Bearer ${jwt_token}")
		echo "Bearer ${jwt_token}">token.txt
		#authorization=$(echo "Bearer ${jwt_token}")
		#echo "${devicecreate}" 
		#echo "${authorization}" 
		device=$(curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' --header "X-Authorization: ${authorization}" -d "${devicecreate}" 'http://47.96.109.21:8080/api/device')	
		deviceid=$(echo ${device} | jq '.id')
		deviceid=$(echo ${deviceid} | jq '.id')
		deviceid=$(echo ${deviceid} | sed 's/\"//g')
		#echo "${device}" | grep "id"
		#echo "设备创建测试 ${deviceid}"
		if [ "${deviceid}" == "" ]
		then
			echo "重复创建设备测试"
			error_message=$(echo ${device} | jq '.message')
			if [ "${error_message}" == "${error_device_exist}" ]
			then
				echo -e "设备名称已被使用，请重新输入 \n"
				continue
			else
				echo -e "错误信息请将下面的信息保存，提交研发 \n"
				echo -e "${device} \n"
				error_count=$(($error_count+1))
				#echo -e "失败次数${error_count} \n"
				if [ $error_count -ge 3 ]
				then
					echo -e "程序异常！！！！！ 请联系研发处理！！！ \n"
					exit
				fi
				read -p "创建设备失败，按任意按键重新输入设备名称" -n1
				echo -e "\n"
				continue
			fi				
		fi
		echo "${device}" >> deviceinfo.txt
		echo -e "设备创建成功 \n"
		#echo "${decice}"
		#echo "${deviceid}"
		devicetoken=$(curl -X GET --header 'Accept: application/json' --header "X-Authorization: ${authorization}" "http://47.96.109.21:8080/api/device/${deviceid}/credentials")
		#echo "${devicetoken}"
		devicetoken=$(echo ${devicetoken} | jq '.credentialsId')
		devicetoken=$(echo ${devicetoken} | sed 's/\"//g')
		#echo ${devicetoken}
		if [ "${devicetoken}" != none ] && [ "${devicetoken}" != "null" ]
		then 
			echo -e "设备令牌获取成功 \n"
			echo -e "Access Token : ${devicetoken} \n" >> ./deviceinfo.txt
			echo "Access Token : ${devicetoken}"
		else
			echo -e "设备令牌获取失败 \n"
		fi
	fi		
fi