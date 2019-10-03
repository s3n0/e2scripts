#!/bin/bash


#########################################################
# Picons Downloader
# 2019-10-03, s3n0
#########################################################
# simple bash script for download & extract picons from
# Google-Drive server, which are compressed with 7zip
#########################################################




#### Specify the picon folder:

PICON_DIR=/media/hdd/picon
#PICON_DIR=/media/usb/picon
#PICON_DIR=/usr/share/enigma2/picon



#### Checking if the 7zip archiver is installed on system
if ! 7z > /dev/null 2>&1 ; then
    echo "ERROR ! The 7zip archiver was not found ! Please install the archiver !"
    echo "For example, using the following commands:   opkg update && opkg install p7zip-full"
    exit 1
fi




#### function for download the file archive from google.drive
gdrive_download_by_ID() {
    wget -O "$PICON_DIR/$1.7z" -q --show-progress --no-check-certificate "https://drive.google.com/uc?export=download&id=$1"
}




#### The first step:
# Download the list of all files (whole web-page) and their IDs from the google drive, for the directory with the "400x230-picontransparent" files inside.
# For example, you can download the whole HTML page via the web-browser:
#
# - root directory list on google.drive:      https://drive.google.com/embeddedfolderview?id=0Bwz6mBA7lUOKNVR4U3NrdW5hTEE#list
# - 400x240-picon-transparent list:           https://drive.google.com/embeddedfolderview?id=0Bwz6mBA7lUOKOENHZ0pGNjVxSEk#list

#### The second step:
# After download the whole HTML page to disk, find the neccessary google.drive IDs for a particullar .7z file inside of the HTML source code,
# and then add new download, as you need...
#
# (1) open the HTML file in some editor (Notepad++ is the best)
# (2) press CTRL+F to find the satellite position, for example by finding the string:  9.0E
# (3) when found it, look at the left side for a very long string (id="entry-...........") and copy the whole ID code, as backward part, for example:
#   - from the string:
#          id="entry-15Msuion-19xqqHm0wg1paO4yLeAX3EFf"
#   - do you need only the end of that string, i.e. this one (ID code):
#          15Msuion-19xqqHm0wg1paO4yLeAX3EFf
# (4) repeat all steps to find all downloading IDs for google.drive in a particular folder (in the saved HTML file)



#### Prepare/clean the picon folder
rm -rf "$PICON_DIR"
mkdir -p "$PICON_DIR"



#### Downloading
echo "-+-+-+-+-+-+-+-+-+-+-+-+-+-"
echo "Downloading..."
gdrive_download_by_ID "15Msuion-19xqqHm0wg1paO4yLeAX3EFf"     # for  9.0E , 400x240-picon-transparent
gdrive_download_by_ID "1OAyXOluc_-IADhwv6bjU3hIdPhBHxWAg"     # for 13.0E , 400x240-picon-transparent
#gdrive_download_by_ID "11xZdREdtQs_qmhZ1wM9lh98cM4iWcqzM"     # for 36.0E , 400x240-picon-transparent

#gdrive_download_by_ID "12tIEFHfivCwl5nT5GGQh_Op4NSUe1lbx"     # for  4.0W , 400x240-picon-transparent
#gdrive_download_by_ID "1PX7X8aJO3RNqtnPSzpNfTMi87sLbd62b"     # for 30.0W , 400x240-picon-transparent
#gdrive_download_by_ID "1b4Q7005qE507XYx5t8SrV-lHp2VgNQg4"     # for 39.0E , 400x240-picon-transparent
echo "...done."
echo "-+-+-+-+-+-+-+-+-+-+-+-+-+-"



#### Extracting all 7z files (7zip - archiver must be installed)
echo "-+-+-+-+-+-+-+-+-+-+-+-+-+-"
echo "Extracting..."
7z e -y -o"$PICON_DIR" "$PICON_DIR/*.7z"
echo "...done."
echo "-+-+-+-+-+-+-+-+-+-+-+-+-+-"



#### Cleaning all downloads (.7z files)
rm -f "$PICON_DIR"/*.7z



exit 0
