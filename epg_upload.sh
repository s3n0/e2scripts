#!/bin/sh


#### CRON config example - upload epg.dat file via the script, every 2nd day, at 03:00
#### 00 03 */2 * *      /bin/sh /usr/script/epg_upload.sh



# enigma2 folders:
log_file="/tmp/epg_upload.log"
local_file="/etc/enigma2/epg.dat"

# online web-server (ftp connection) to store the epg.dat file:
online_file="ftp://example.com/folder/epg.dat"
xuser="user_login"
xpass="user_password"



# for sure I will test the functionality and presence of the necessary "curl" in the system!
if [ ! "$(curl --version)" ]
then
	echo `date '+%Y-%m-%d %H:%M:%S'`": curl command NOT found (NOT installed)... please install it first:  opkg update && opkg install curl" >> $log_file
	exit 0
fi



# I will only upload the $local_file (EPG data) only if exists and is greater than 65 kB
#wget -q -O - "http://127.0.0.1/web/saveepg" > /dev/null 2>&1         # save epg.dat file to disk - using the Enigma2 Open-Webif
if [ -f "$local_file" ] && [ $(wc -c < "$local_file") -gt 65000 ]; then             #  -gt = GreaterThan       # -lt = LesserThan
	curl --insecure --ftp-ssl -u $xuser:$xpass -T $local_file $online_file
	echo `date '+%Y-%m-%d %H:%M:%S'`": $local_file file was uploaded" >> $log_file
else
	echo `date '+%Y-%m-%d %H:%M:%S'`": $local_file file to upload is too small or not found" >> $log_file
fi


exit 0
