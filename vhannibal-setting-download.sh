#!/bin/bash

# Shell script was created by s3n0, 2021-02
# - shell script was intended for downloading the patricular zip-package / "setting" package
# - after download the zip-package, it is unpacked in a temporary folder
# - next, at least two strings are searched in all "*.tv" files to identify a specific one file - specific SAT provider
# - the userbouquet file is renamed and copied to the "/etc/enigma2" folder
# - userbouquet files are then reloaded via OpenWebif
# Of course, it is necessary to modify the search strings and also the ID number of the downloaded zip-file, according to your own needs


HR="#####################################################"
echo "$HR"
TMP_DIR="/tmp/vhannibal-temp"
rm -rf $TMP_DIR
mkdir -p $TMP_DIR
cd $TMP_DIR


echo "Downloading and extracting the Vhannibal setting archive file."
wget -O "${TMP_DIR}/setting.zip" --no-check-certificate "https://www.vhannibal.net/download_setting.php?id=13&action=download"
# NOTE: find your own setting zip-package on the Vhannibal-Enigma2 website and edit the required "id=??" in the URL, according to your setting zip-package
unzip -j "${TMP_DIR}/setting.zip" -d $TMP_DIR


echo "Search for 'Skylink' userbouquet file - with 'Movies' category."
FILE1=$(grep -l "Movies" `grep -l "Skylink" $TMP_DIR/*.tv`)
if [ -z "$FILE1" ]; then
    echo "SKYLINK userbouquet file was NOT found !"
else
    echo "SKYLINK userbouquet file found: ${FILE1}"
    sed -i -e 's/NAME Skylink/NAME SAT Skylink SK \& CZ (Vhannibal '$(date "+%Y-%m")')/I' $FILE1
    cp -f $FILE1 /etc/enigma2/userbouquet.sat-skylink-vhannibal.tv
fi


echo "Search for 'Deutschland' userbouquet file - with 'Regionalen' category."
FILE2=$(grep -l "Regionalen" `grep -l "Deutschland" $TMP_DIR/*.tv`)
if [ -z "$FILE2" ]; then
    echo "DEUTSCHLAND userbouquet file was NOT found !"
else
    echo "DEUTSCHLAND userbouquet file found: ${FILE}"
    sed -i -e 's/NAME HD+ Deutschland/NAME SAT Deutschland (Vhannibal '$(date "+%Y-%m")')/I' $FILE2
    cp -f $FILE2 /etc/enigma2/userbouquet.sat-deutschland-vhannibal.tv
fi


wget -qO- "http://127.0.0.1/web/servicelistreload?mode=0" > /dev/null 2>&1
sleep 2
wget -qO- "http://127.0.0.1/web/servicelistreload?mode=4" > /dev/null 2>&1


rm -rf $TMP_DIR
echo "$HR"
exit 0
