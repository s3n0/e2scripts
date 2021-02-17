#!/bin/bash

#############################################################################
### script written by s3n0, 2021-02-17
### script is designed to automatically update the "oscam.srvid" file
### a great automatic .srvid file generator is used - HTTP://KOS.TWOJEIP.NET
#############################################################################

find_oscam_cfg_dir() {
    DIR_LIST="""/etc/tuxbox/config
                /etc/tuxbox/config/oscam
                /var/tuxbox/config
                /usr/keys
                /var/keys
                /var/etc/oscam
                /var/etc
                /var/oscam
                /config/oscam"""
    RET_VAL=""
    for FOLDER in $DIR_LIST; do
        [ -f "${FOLDER}/oscam.conf" ] && { RET_VAL="$FOLDER"; break; }
    done
    echo "$RET_VAL"
}

URL="http://kos.twojeip.net/download.php?download[]=pack-hdplus&download[]=pack-skygermany&download[]=pack-skylink"
#### # # # # # # # # # # # # #   downloading  :     pack-hdplus      +     pack-skygermany      +     pack-skylink
#### You can find the correct package names (or full URL) directly on the website KOS.TWOJEIP.NET - in the address of the downloaded file

CFG_DIR=$(find_oscam_cfg_dir)
[ -z "$CFG_DIR" ] && { echo "ERROR ! Oscam cfg-directory not found !"; exit 1; }

cp -f "${CFG_DIR}/oscam.srvid" "/tmp/oscam.srvid_backup"

echo -e "Downloading file...\n- from: ${URL}\n- to: ${CFG_DIR}/oscam.srvid"
if wget --spider "${URL}" 2>/dev/null; then          # check the existence of an online file or web-page
    wget -q -O "${CFG_DIR}/oscam.srvid" "${URL}"
    echo "...done !"
else
    echo "...ERROR - online URL ${URL} does not exist !"
    exit 1
fi

exit 0
