#!/bin/bash


# Shell script was created by s3n0, 02.2021
# - shell script was intended for downloading the patricular zip-package / "setting" package
# - after download the zip-package, it is unpacked in a temporary folder
# - next, at least two strings are searched in all "*.tv" files to identify a specific one file - specific SAT provider
# - the userbouquet file is renamed and copied to the "/etc/enigma2" folder
# - userbouquet files are then reloaded via OpenWebif
# Of course, it is necessary to modify the search strings and also the ID number of the downloaded zip-file, according to your own needs


HR="#####################################################"
echo "$HR"
TMP_DIR="/tmp/vhannibal_settings"
rm -rf $TMP_DIR
mkdir -p $TMP_DIR
cd $TMP_DIR


#### Notice:   Find your own setting zip-package on the Vhannibal web-site https://www.vhannibal.net/enigma2.php
####            and edit the required "id=??" number, according to your downloaded zip-file.
ID_NUMBER=13
echo "- downloading and extracting the main Vhannibal enigma2 settings file, with ID number ${ID_NUMBER}"
wget -O "${TMP_DIR}/setting.zip" --no-check-certificate "https://www.vhannibal.net/download_setting.php?id=${ID_NUMBER}&action=download" > /dev/null 2>&1
[ "$?" -ne "0" ] && { echo "! ERROR ! The main Vhannibal enigma2 settings file, with ID number ${ID_NUMBER} - download failed !"; exit 1; }
unzip -qj "${TMP_DIR}/setting.zip" -d $TMP_DIR


BOUQUET2SAVE=/etc/enigma2/userbouquet.sat-skylink-vhannibal.tv
echo "- search for 'Skylink' userbouquet file (with 'Movies' category)"
BOUQUET2FIND=$(grep -l "Movies" `grep -l "Skylink" $TMP_DIR/*.tv`)
if [ -z "$BOUQUET2FIND" ]; then
    echo "! 'Skylink' userbouquet file was NOT found !"
else
    echo "- 'Skylink' userbouquet file found: ${BOUQUET2FIND}"
    sed -i -e 's/NAME Skylink/NAME SAT Skylink SK \& CZ (Vhannibal '$(date "+%Y-%m")')/I' $BOUQUET2FIND
    echo "- copying: ${BOUQUET2FIND} ----> ${BOUQUET2SAVE}"
    cp -f $BOUQUET2FIND $BOUQUET2SAVE
fi


BOUQUET2SAVE=/etc/enigma2/userbouquet.sat-deutschland-vhannibal.tv
echo "- search for 'Deutschland' userbouquet file (with 'Regionalen' category)"
BOUQUET2FIND=$(grep -l "Regionalen" `grep -l "Deutschland" $TMP_DIR/*.tv`)
if [ -z "$BOUQUET2FIND" ]; then
    echo "! 'Deutschland' userbouquet file was NOT found !"
else
    echo "- 'Deutschland' userbouquet file found: ${BOUQUET2FIND}"
    sed -i -e 's/NAME HD+ Deutschland/NAME SAT Deutschland (Vhannibal '$(date "+%Y-%m")')/I' $BOUQUET2FIND
    echo "- copying: ${BOUQUET2FIND} ----> ${BOUQUET2SAVE}"
    cp -f $BOUQUET2FIND $BOUQUET2SAVE
fi


wget -qO- "http://127.0.0.1/web/servicelistreload?mode=0" > /dev/null 2>&1
sleep 2
wget -qO- "http://127.0.0.1/web/servicelistreload?mode=4" > /dev/null 2>&1


rm -rf $TMP_DIR
echo "$HR"


exit 0
