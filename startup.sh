#! /bin/bash

cd "${0%/*}"

bluetoothctl < bluetoothConfig

while : ; do
	status="$(hcitool dev | grep hci0)"
	if [ ! -z "$status" -a "$status" != " " ]; then
		break
	fi
done

#echo "Connected to Arduino"

rfcomm bind 0 98:D3:34:90:5D:05

./remoteDorm.py
