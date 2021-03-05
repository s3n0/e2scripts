#!/bin/bash

HEADER="
#################################################################################
### script written by s3n0, 2021-02-17, https://github.com/s3n0
### script is designed to automatically update the 'oscam.srvid' file
### as the 'srvid' generator is used the online web-page:  HTTP://KOS.TWOJEIP.NET
#################################################################################
"

find_oscam_cfg_dir() {
    RET_VAL=""
    DIR_LIST="/etc/tuxbox/config
              /etc/tuxbox/config/oscam
              /var/tuxbox/config
              /usr/keys
              /var/keys
              /var/etc/oscam
              /var/etc
              /var/oscam
              /config/oscam"
    for FOLDER in $DIR_LIST; do
        [ -f "${FOLDER}/oscam.conf" ] && { RET_VAL="$FOLDER"; break; }
    done
    echo "$RET_VAL"
}

echo "$HEADER"

URL="http://kos.twojeip.net/download.php?download[]=pack-hdplus&download[]=pack-mtv&download[]=pack-skylink&download[]=pack-austriasat&download[]=pack-orfdigital&download[]=pack-skygermany"
#### # # # # # # # # # # # # #   downloading  :     pack-hdplus      +     pack-mtv      +     pack-skylink     +      pack-austriasat      +     pack-orfdigital      +     pack-skygermany
#### You must to find the correct package names (or full URL) directly on the website HTTP://KOS.TWOJEIP.NET - in the URL address of the downloaded file
#### !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

OSCAM_CFGDIR=$(find_oscam_cfg_dir)

[ -z "$OSCAM_CFGDIR" ] && { echo "ERROR ! Oscam cfg-directory not found !"; exit 1; }

cp -f "${OSCAM_CFGDIR}/oscam.srvid" "/tmp/oscam.srvid_backup"

echo -e "Downloading file...\n- from: ${URL}\n- to: ${OSCAM_CFGDIR}/oscam.srvid"
if wget --spider "${URL}" 2>/dev/null; then          # check the existence of an online file or web-page
    wget -q -O "${OSCAM_CFGDIR}/oscam.srvid" "${URL}"
    echo "...done !"
else
    echo "...ERROR - online URL ${URL} does not exist !"
    exit 1
fi

exit 0
