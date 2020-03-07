#!/bin/sh


#### shell script to download userbouquet file from internet and overwrite local userbouquet file, but only if there is a change in the file (tested for file content differences)
#### it is based on "init 4" and "init 3" reboots of Enigma as the most reliable method for all Enigma distributions


#### CRON config example - check and download new userbouquet file - every day, at 05:15 :
####      15 05 * * *        /bin/sh -c "/usr/script/bouquetx.sh download"


fname="userbouquet.iptv-world.tv"
online_file="http://example.com/$fname"
local_file="/etc/enigma2/$fname"
log_file="/home/root/bouquet_download.log"
tmp_file="/tmp/u"
bouquet="#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET \"$fname\" ORDER BY bouquet"


help_msg="
USAGE:
    bouquetx.sh install ....... to install   iptv-userbouquet into the Enigma2 bouquet favorite list
    bouquetx.sh uninstall ..... to uninstall iptv-userbouquet from the Enigma2 bouquet favorite list
    bouquetx.sh download ...... to download  iptv-userbouquet file + replace if there is a newer version online
"







# function to detect the standby mode (e2/OpenWebif power-state)
is_standby() {
	[ "$(wget -q -O - http://127.0.0.1/web/powerstate | grep '</e2instandby>' | cut -f 1)" == "true" ]
}


# check for the new online bouquet file
is_new_bouquet() {
    # [ "$(wget -q -O - "$online_file" | wc -c)" != "$(wc -c < $local_file)" ]
    # wget -q -O $tmp_file "$online_file" > /dev/null 2>&1 && [ "$(wc -c < $tmp_file)" != "$(wc -c < $local_file)" ]
    wget -q -O $tmp_file "$online_file" > /dev/null 2>&1 && ! diff -aw $tmp_file $local_file > /dev/null 2>&1
}


# download and replace userbouquet file - only if there is a newer version online
download_userbouquet() {
    if is_new_bouquet; then
        mv -f $tmp_file $local_file
        echo `date '+%Y-%m-%d %H:%M:%S'`": $online_file file was downloaded, replaced and reloaded in your Enigma2" >> $log_file
    else
        echo `date '+%Y-%m-%d %H:%M:%S'`": $online_file file was downloaded, but not replaced ((no differences in file content))" >> $log_file
    fi
    # wget -q -O - "http://127.0.0.1/web/servicelistreload?mode=2" > /dev/null 2>&1
}


case "$1" in
    install)
        if ! cat /etc/enigma2/bouquets.tv | grep -w "$bouquet" > /dev/null; then
            init 4; sleep 5         # stop the Enigma
            sed -i "1 a $bouquet" /etc/enigma2/bouquets.tv
            [ -f $local_file ] || touch $local_file     # create an empty userbouquet file on local disk - if the file does not exist
            download_userbouquet
            init 3                  # start the Enigma
        fi
        ;;
    uninstall)
        init 4; sleep 5             # stop the Enigma
        sed -i "/$bouquet/d" /etc/enigma2/bouquets.tv
        rm -f $local_file
        init 3                      # start the Enigma
        ;;
    download)        
        if is_standby && is_new_bouquet; then           # only if the Enigma is in standby
            init 4; sleep 5         # stop the Enigma
            download_userbouquet
            init 3; sleep 60        # start the Enigma (and waiting 60 seconds for Enigma to boot)
            wget -q -O - "http://127.0.0.1/web/powerstate?newstate=5" > /dev/null 2>&1             # turn the Enigma back into standby
        else
            echo `date '+%Y-%m-%d %H:%M:%S'`": Enigma2 is not in Standby. Bouquet downloading was canceled." >> $log_file
        fi
        ;;
    *)
        echo "$help_msg"
        ;;
esac


[ -f $tmp_file ] && rm -f $tmp_file


exit 0
