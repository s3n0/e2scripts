#!/bin/sh


#### shell-script to download userbouquet file from the internet, and then overwrite local userbouquet file - if both files are different (tested for file content differences)


#### it isn't based on "init 4" and "init 3" commands to fast restart of Enigma2 (as the most reliable method for all Enigma distributions),
#### but it is based on the OpenWebif reload services !!!


#### CRON config example - check and download new userbouquet file - every day, at 05:15 :
####      15 05 * * *        /bin/sh -c "/usr/script/bouquetx.sh download"




fname="userbouquet.iptv-example.tv"
bq_file_local="/etc/enigma2/${fname}"
bq_file_online="http://example.com/iptv/${fname}"  # bq_file_online="http://example.com/iptv/some.file.name.tv"
tmp_file="/tmp/${fname}"                        # temporary file for downloading the online file and to compare with the local file
log_file="/tmp/bouquetx.log"                    # log_file="/home/root/bouquetx.log"
log_file_sizemax=65000                          # max log_file size [Bytes]
bq_entry="#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET \"$fname\" ORDER BY bouquet"


help_msg="
USAGE:
    $0 install ......... to install   the userbouquet file into the Enigma2 bouquet favorite list (/etc/enigma2/bouquets.tv)
    $0 uninstall ....... to uninstall the userbouquet file from the Enigma2 bouquet favorite list (/etc/enigma2/bouquets.tv)
    $0 download ........ to download  the new userbouquet file + replace if there is a newer version online
"








# function to logging
fLog() 
{
    if [ "${1:0:3}" = "===" ]; then             # if echo "$1" | grep -q "==="; then
        logmsg="$1"
    else
        logmsg=$(echo "$1" | sed "s/^/`date '+%Y-%m-%d %H:%M:%S'` /")       # add a timestamp to each line of input argument (it can be a multiline string)
    fi
    
    #echo "$logmsg" > /dev/null                  ### null device   <---  log will disabled (do nothing)
    #echo "$logmsg" >> $log_file                 ### file
    #echo "$logmsg" >> $log_file 2>&1            ### file + stderr
    #echo "$logmsg" | tee -a $log_file           ### file + stdout(display)
    echo "$logmsg" 2>&1 | tee -a $log_file       ### file + stdout(display) + stderr
    
    # reduction the log filesize, if neccessary (delete first 20 lines):
    if [ -f "$log_file" ] && [ $(wc -c <"$log_file") -gt $log_file_sizemax ]; then sed -i -e '1,20d' "$log_file"; fi
}


# function to detect the standby mode (e2/OpenWebif power-state)
is_standby() {
	[ "$(wget -q -O - http://127.0.0.1/web/powerstate | grep '</e2instandby>' | cut -f 1)" = "true" ]
}


# reload userbouquets, lamedb, blacklist in the Enigma2  (mode 0 as well as 4 - both modes are required for correct reload services !)
services_reload() {
    wget -q -O - "http://127.0.0.1/web/servicelistreload?mode=0" > /dev/null 2>&1                   # reloading: userbouquet.*.tv ; userbouquets.tv ; lamedb
    sleep 1
    wget -q -O - "http://127.0.0.1/web/servicelistreload?mode=4" > /dev/null 2>&1                   # reloading: blacklist ; whitelist
    fLog "service lists was reloaded in your Enigma (userbouquet.*.tv / .radio , userbouquets.tv , lamedb)"
}


# download and replace the userbouquet file - only if there is a newer version online
download_replace_userbouquet() {
    rm -f $tmp_file
    
    if wget -q -O $tmp_file "$bq_file_online" > /dev/null 2>&1; then
        fLog "$bq_file_online file was downloaded"
    else
        fLog "$bq_file_online file download failed !"
    fi
    
    if [ -f "$tmp_file" ] && diff -aw $tmp_file $bq_file_local > /dev/null 2>&1; then
        fLog "$bq_file_local file was not replaced (the content of the files is the same)"
    else
        mv -f $tmp_file $bq_file_local
        fLog "$bq_file_local file was replaced"
    fi
}


case "$1" in
    install)
        if ! cat /etc/enigma2/bouquets.tv | grep -w "$bq_entry" > /dev/null; then
            sed -i "1 a $bq_entry" /etc/enigma2/bouquets.tv
            [ -f $bq_file_local ] || touch $bq_file_local         # create an empty userbouquet file - if the file does not exist
            download_replace_userbouquet
            services_reload
        fi
        ;;
    uninstall)
        sed -i "/$bq_entry/d" /etc/enigma2/bouquets.tv
        rm -f $bq_file_local
        services_reload
        ;;
    download)        
        if is_standby; then         # only if the Enigma is in standby, then...
            download_replace_userbouquet
            services_reload
        else
            fLog "Enigma2 is not in standby mode - download function was canceled"
        fi
        ;;
    *)
        echo "$help_msg"
        ;;
esac


rm -f $tmp_file
fLog "==========================================="


exit 0
