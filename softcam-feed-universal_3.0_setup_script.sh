#!/bin/bash


###################
## This script was pulled from IPK package "softcam-feed-universal_3.0_all.ipk"
## Improved by s3n0 / 2019-06-05
###################
## I found a minor bug in detecting OpenATV versions. Version "6" no longer exists, but there is version "6.2" and "6.3". 
## This is a modified script. Beware... not an IPK-package which is useless I think, but the bash script only.
##
## This bash script updates/adds a softcam feed. Just copy the script to '/tmp' folder and run it via the Shell, for example:
##      sh /tmp/softcam-feed-universal_3.0_setup_script.sh
##
## If bash script doesn't want to execute, try to set the execution attribute:
##      chmod + x /tmp/softcam-feed-universal_3.0_setup_script.sh
##
## To uninstall a feed feed source, just delete the feed source file:
##      rm -f /etc/opkg/secret-feed.conf
###################


ERRENIGMA="""
**********************************
Unsupported Enigma found! Aborted!
**********************************
"""

ERRBRANDING="""
***************************************************************
Python script used to determine chipset architecture not found:
 '/usr/lib/enigma2/python/BoxBrandingTest.pyo'
Aborted!
***************************************************************
"""



if [ -e /usr/lib/enigma2/python/BoxBrandingTest.pyo ]; then 
    python /usr/lib/enigma2/python/BoxBrandingTest.pyo | sed 's/<$//' | sed 's/ /_/g' > /tmp/boxbranding.cfg
    if grep -qs 'getImageDistro=openvix' cat /tmp/boxbranding.cfg  ; then
        echo "$ERRENIGMA"
        exit 1
    fi
else
    echo "$ERRBRANDING"
    exit 1
fi
 


if grep -qs 'getImageDistro=openmips' or 'getImageDistro=open8' or 'getImageDistro=openxta' or 'getImageDistro=openpli' cat /tmp/boxbranding.cfg ; then
    IMAGEBASE="pli"
else
    IMAGEBASE="oea"
fi



DISTRONAME=$(grep 'getImageDistro' /tmp/boxbranding.cfg | grep -oE "[^=]+$")
if [[ $DISTRONAME == "openatv" ]] ; then
    ### Fixed script that gets the correct string "6.2" instead of "6" cut (that is a problem in OpenATV)
    DISTROVERSION=$(grep 'getImageVersion' /tmp/boxbranding.cfg | grep -oE "[^=]+$")
else
    ### Gets the string "6" from the file (only an integer part without real), but the string inside the file is "6.2" for example (used for all others images than OpenATV)
    DISTROVERSION=$(grep 'getImageVersion' /tmp/boxbranding.cfg | grep -oE "[^=]+$" | cut -c 1-1)
fi



ARCH=$(grep 'getImageArch' /tmp/boxbranding.cfg | grep -oE "[^=]+$")
#if [ $ARCH == "armv7ahf-neon" ] || [ $ARCH == "cortexa15hf-neon-vfpv4" ] ; then ARCH=armv7ahf ; fi       # original line
if [[ $ARCH == *"armv7"* ]] || [[ $ARCH == *"cortexa15"* ]] ; then ARCH=cortexa15hf-neon-vfpv4 ; fi       # updated line

### - a note for arm_v8 chipset:
### the old binary files compiled for the Cortex-A15/arm_v7 chipset can to be executed on the Cortex-A53/arm_v8 - due to backward compatibility with the new arm_v8 chipsets



url="http://nonpublic.space/$IMAGEBASE/$DISTROVERSION/$ARCH"
if [[ `wget -S --spider "$url/Packages.gz"  2>&1 | grep '200 OK'` ]]
then
    rm -f /etc/opkg/secret-feed.conf
    echo "src/gz secret-feed $url" > /etc/opkg/secret-feed.conf
    echo "***********************************************"
    echo "The new feed source was successfully installed!"
    echo "You can try updating your offline package list:"
    echo "  opkg update"
    echo "***********************************************"
else
    echo "***********************************************"
    echo "Failure! The feed source does not exists!"
    echo " '$url'"
    echo "Aborted!"
    echo "***********************************************"
    exit 1
fi



#wget -O /tmp/Packages.gz "http://nonpublic.space/$IMAGEBASE/$DISTROVERSION/$ARCH/Packages.gz"


### - working URL example - as a direct link:
### http://nonpublic.space/oea/6.2/mips32el/Packages.gz
###
### - not working URL example (wrong version retreived in the case of OpenATV 6.2):
### http://nonpublic.space/oea/6/mips32el/Packages.gz



exit 0
