#!/bin/sh

#### CRON config example - download epg.dat file, every day, at 5:00
#### 00 5 * * *        sh /usr/script/epg_download.sh

# NOTE:
# -for sure it is recommended to set automatic and regular loading (refreshing) of epg data from the file, in the Enigma configuration
# -OpenATV:   MENU > Settings > EPG > EPG settings > Auto-reload: "Yes"
# -EPG refresh interval we can leave as the default value - i.e. every 24 hours

# folders:
log_file="/tmp/epg_download.log"
local_file="/etc/enigma2/epg.dat"

# online server with the "epg.dat" stored file:
online_file="http://example.com/folder/epg.dat"



if [ "$(wget -q -O - http://127.0.0.1/web/powerstate | grep '</e2instandby>' | cut -f 1)" == "false" ]; then
    echo `date`": Enigma2 is not in Standby. EPG-file downloading script was canceled." >> $log_file
    exit
fi



if wget --spider ${online_file} 2>/dev/null     # checking the online file
then
    init 4              # stop the Enigma2 (to leave the /etc/enigma2/epg.dat file from Enigma2 processing)
    sleep 5s            # wait a few seconds (stopping of the Enigma2)
    wget -q -O $local_file $online_file
    echo `date`": $online_file file was downloaded + replaced" >> $log_file
    init 3              # start the Enigma2 (to reload new file 'epg.dat')
    sleep 1m            # wait 1 min. to boot the Enigma2
    # Enigma2 will re-started into Power-On state... so, we need to switch the power state into Standby mode again !
    # in all standard versions of OpenWebif:   0 = toggle Standby , 1 = Deep-Standby , 2 = Reboot the System , 3 = Restart the GUI (Enigma2 only)
    # in newer versions of OpenWebif:          4 = wake-up from Standby , 5 = switch to Standby
    wget -q -O /dev/null "http://127.0.0.1/web/powerstate?newstate=5"
    echo `date`": Enigma2 was switched to Standby" >> $log_file
else
    echo `date`": $online_file file was not found" >> $log_file
fi



exit
