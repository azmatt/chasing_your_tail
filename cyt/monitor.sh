#!/bin/bash
while true;
do
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # no color
numprocesses=$(ps aux | grep -i 'kismet' | wc -l)
#echo $numprocesses
if [[ $numprocesses > 2 ]] ; then 
		echo -e "${GREEN}kismet up${NC}"
	else
		echo -e "${RED}kismet down${NC}"
fi

string=$(iwconfig wlan0 & iwconfig wlan1 )
if [[ $string == *"Mode:Monitor"* ]]; then
	echo -e "${GREEN}Monitor Mode Detected${NC}"
	echo
else
	echo -e "${RED}Monitor Mode Not Detected${NC}"
	echo
fi 
sleep 10;
done
