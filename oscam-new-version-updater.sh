#!/bin/bash


#######################################
# Oscam new version updater
#######################################
# 2019/10/21 script written by s3n0
#
# This bash script checks if there is a newer version of Oscam on the internet and if so,
# then downloads and overwrites the old Oscam binary file on the local disk.
#
# Script is designed to avoid having to add another feed to your Enigma.
# '7zip' archiver is required since 'ar' tool is a problematic when splitting files from IPK packages.
#######################################
# This script uses "updates.mynonpublic.com" as an update source and also
# uses the Python source code, from the script from here:
#       http://updates.mynonpublic.com/oea/feed
#
# The original 'feed' script was developed for the purpose of installing softcam-feed into Enigma:
#       wget -O - -q http://updates.mynonpublic.com/oea/feed | bash
#
# To run this script directly from the github server, use the following command:
#       wget -qO- --no-check-certificate "https://github.com/s3n0/e2scripts/raw/master/oscam-new-version-updater.sh" | bash
#######################################





## OSCAM_LOCAL_PATH="/usr/bin/oscam"
## [ -f $OSCAM_LOCAL_PATH ] || { echo "ERROR ! User-configured binary file $OSCAM_LOCAL_PATH not found !"; exit 1; }

OSCAM_LOCAL_PATH=$(find /usr/bin -name oscam* | head -n 1)
[ -z "$OSCAM_LOCAL_PATH" ] && { OSCAM_LOCAL_PATH="/usr/bin/oscam"; echo "Oscam binary file was not found in folder '/usr/bin'. The default path and filename $OSCAM_LOCAL_PATH will be used to download and to add a new Oscam binary file."; } || echo "Recognized binary file: $OSCAM_LOCAL_PATH"

## OSCAM_LOCAL_PATH=$(ps --no-headers -f -C oscam | sed 's@.*\s\([\-\_\/a-zA-Z]*\)\s.*@\1@' | head -n 1)
## [ -z "$OSCAM_LOCAL_PATH" ] && { OSCAM_LOCAL_PATH="/usr/bin/oscam"; echo "No Oscam process name found. The default file name $OSCAM_LOCAL_PATH will be used to download and add a new Oscam."; } || echo "Oscam process $OSCAM_LOCAL_PATH found."





REQUESTED_BUILD="oscam-trunk"
#REQUESTED_BUILD="oscam-emu"

# - some examples of Oscam builds included on the feed server, there is possible to change one of them:
#
#       oscam-trunk
#       oscam-trunk-ipv4only
#       oscam-stable
#       oscam-stable-ipv4only
#
#       oscam-emu
#       oscam-emu-ipv4only





# A temporary directory
TMP_DIR="/tmp/oscam_binary_update"





#######################################
#######################################

#### Auto-configuring the Enigma version and the chipset / CPU architecture (with the help of Python):

BASE_FEED="http://updates.mynonpublic.com/oea"
# OEVER="4.3"                           # this value is determined automatically using the Python script below
# ARCH="mips32el"                       # this value is determined automatically using the Python script below




export D=${D}


get_oever() {
    OEVER=$(python - <<END
import sys
import os
dest = ""
if os.environ.get('D'):
    dest = os.environ.get('D')
sys.path.append(dest + '/usr/lib/enigma2/python')
try:
    from boxbranding import getOEVersion
    oever = getOEVersion()
    print oever
except:
    print "unknown"
END
    )
    OEVER=$(echo $OEVER | sed "s/OE-Alliance //")
    if [ "x$OEVER" == "xunknown" ]; then
        if [[ -x "/usr/bin/openssl" ]]; then
            SSLVER=$(openssl version | awk '{ print $2 }')
            case "$SSLVER" in
                1.0.2a|1.0.2b|1.0.2c|1.0.2d|1.0.2e|1.0.2f)
                    OEVER="unknown"
                    ;;
                1.0.2g|1.0.2h|1.0.2i)
                    OEVER="3.4"
                    ;;
                1.0.2j)
                    OEVER="4.0"
                    ;;
                1.0.2k|1.0.2l)
                    OEVER="4.1"
                    ;;
                1.0.2m|1.0.2n|1.0.2o|1.0.2p)
                    OEVER="4.2"
                    ;;
                1.0.2q|1.0.2r|1.0.2s)
                    OEVER="4.3"
                    ;;
                *)
                    OEVER="unknown"
                    ;;
            esac
        fi
    fi
}

get_arch() {
    ARCH=$(python - <<END
import sys
import os
dest=""
if os.environ.get('D'):
        dest=os.environ.get('D')
sys.path.append(dest + '/usr/lib/enigma2/python')
try:
    from boxbranding import getImageArch
    arch = getImageArch()
    print arch
except:
    print "unknown"
END
    )
    if [ "x$ARCH" == "xunknown" ]; then
        case "$OEVER" in
            3.4|4.0)
                ARCH="armv7a-neon"
                ;;
            4.1)
                ARCH="armv7athf-neon"
                ;;
            *)
                ARCH="armv7a"
                ;;
        esac
        echo $(uname -m) | grep -q "aarch64" && ARCH="aarch64"
        echo $(uname -m) | grep -q "mips" && ARCH="mips32el"
        echo $(uname -m) | grep -q "sh4" && ARCH="sh4"
        if echo $(uname -m) | grep -q "armv7l"; then
            echo $(cat /proc/cpuinfo | grep "CPU part" | uniq) | grep -q "0xc09" && ARCH="cortexa9hf-neon"
            if echo $(cat /proc/cpuinfo | grep "CPU part" | uniq) | grep -q "0x00f"; then
                case "$OEVER" in
                    3.4)
                        ARCH="armv7ahf-neon"
                        ;;
                    *)
                        ARCH="cortexa15hf-neon-vfpv4"
                        ;;
                esac
            fi
        fi
    fi
}

check_compat() {
    case "$OEVER" in
        unknown)
            echo Broken boxbranding ...
            exit 1
            ;;
        3.4)
            ;;
        3.*)
            echo Your image is EOL ...
            exit 1
            ;;
        2.*)
            echo Your image is EOL ...
            exit 1
            ;;
        1.*)
            echo Your image is EOL ...
            exit 1
            ;;
        0.*)
            echo Your image is EOL ...
            exit 1
            ;;
    esac
    if [ "x$ARCH" == "xunknown" ]; then
        echo Broken boxbranding ...
        exit 1
    fi
}


get_oever
get_arch
check_compat


#######################################
#######################################


#### Checking if the 7-zip archiver is installed on system
if [ -f /usr/bin/7z ]; then
    BIN7Z=/usr/bin/7z
#elif [ -f /usr/bin/7za ]; then    # !!!!! "7za" stand-alone archiver does not support the "ar" method (the outer layer of the .ipk file is compressed just through the "ar" archiver)
#    BIN7Z=/usr/bin/7za
else
    echo "ERROR ! The 7-zip archiver was not found ! Please install the 7-zip archiver !"
    echo "For example, using the following commands:   opkg update && opkg install p7zip-full"
    exit 1
fi

#### Download and unpack the list of all available packages + Find out the package name according to the required Oscam edition
echo "---------------------------"
echo -n "Downloading and unpacking the list of softcam installation packages... "
IPK_FILENAME=$(wget -q -O - "$BASE_FEED/$OEVER/$ARCH/Packages.gz" | gunzip -c | grep "Filename:" | grep "$REQUESTED_BUILD"_1.20 | cut -d " " -f 2)
[ -z "$IPK_FILENAME" ] && { echo " failed!"; exit 1; } || echo " done."

#### Create the temporary subdirectory and go in
rm -fr $TMP_DIR ; mkdir -p $TMP_DIR ; cd $TMP_DIR

#### Download the necessary Oscam installation package
echo -n "Downloading the necessary Oscam installation IPK package... "
wget -q --show-progress -O $TMP_DIR/$IPK_FILENAME $BASE_FEED/$OEVER/$ARCH/$IPK_FILENAME && echo " done." || { echo " failed!"; exit 1; }

#### Extracting the IPK package
extractor() {
    echo -n "Extracting:  $1 $2  --  "; $BIN7Z e -y $1 $2 > /dev/null 2>&1 && echo "OK" || { echo "FAILED!"; exit 1; }
}
echo "---------------------------"
echo "Extracting the IPK package:"
extractor $IPK_FILENAME                          # 1. splitting linked files ("ar" archive) - since "ar" separates files from the archive with difficulty, so I will use "7-zip" archiver
extractor data.tar.?z                            # 2. unpacking the ".gz" OR ".xz" archive
extractor data.tar ./usr/bin/$REQUESTED_BUILD    # 3. unpacking ".tar" archive, but only one file - i.e. an oscam binary file, for example as "oscam-trunk"
echo -n "The Oscam binary file has "
[ -f $TMP_DIR/$REQUESTED_BUILD ] && echo "been successfully extracted." || { echo "not been extracted! Please check the folder '$TMP_DIR'."; exit 1; }
echo "---------------------------"

#### Retrieve Oscam online version   (from downloaded binary file)
chmod a+x $TMP_DIR/$REQUESTED_BUILD
OSCAM_ONLINE_VERSION=$( $TMP_DIR/$REQUESTED_BUILD --build-info | grep -i 'version:' | grep -o '[0-9]\{5\}' )    # output result is, as example:  11552
#OSCAM_ONLINE_VERSION=$( echo $IPK_FILENAME | sed -e 's/.*svn\([0-9]*\)-.*/\1/'  )                              # old method to retrieve online Oscam version
[ -z "$OSCAM_ONLINE_VERSION" ] && { echo "Error! The Oscam online version cannot be recognized!"; exit 1; }

#### Retrieve Oscam local version    (from current binary file placed in the /usr/bin folder)
OSCAM_LOCAL_VERSION=$(  $OSCAM_LOCAL_PATH --build-info | grep -i 'version:' | grep -o '[0-9]\{5\}'   )          # output result is, as example:  11546
[ -z "$OSCAM_LOCAL_VERSION" ] && OSCAM_LOCAL_VERSION="11000"                                                    # sets the null version as a precaution if there is no Oscam on the local harddisk yet

#### Compare Oscam local version VS. online version
echo -e "Oscam version on internet:\t$OSCAM_ONLINE_VERSION\nOscam version on local drive:\t$OSCAM_LOCAL_VERSION"
if [ "$OSCAM_ONLINE_VERSION" -gt "$OSCAM_LOCAL_VERSION" ]
then
    echo "A new version of Oscam has been found and will be updated."
    # wget -qO- "http://127.0.0.1/web/message?text=New+Oscam+version+found+($OSCAM_ONLINE_VERSION)%0ANew+version+will+updated+now.&type=1&timeout=10" > /dev/null 2>&1     # show WebGUI info message
    #### Replace the oscam binary file with new one
    OSCAM_BIN_FNAME=${OSCAM_LOCAL_PATH##*/}
    OSCAM_CMD=$(ps -f --no-headers -C $OSCAM_BIN_FNAME | head -n 1 | grep -o '/.*$')
    [ -z "$OSCAM_CMD" ] || { killall -9 $OSCAM_BIN_FNAME ; echo "Recognized Oscam command-line: $OSCAM_CMD" ; }
    mv -f $TMP_DIR/$REQUESTED_BUILD $OSCAM_LOCAL_PATH
    chmod a+x $OSCAM_LOCAL_PATH
    [ -z "$OSCAM_CMD" ] || $OSCAM_CMD
else
    echo "Installed Oscam version is current. No need to update."
    # wget -qO- "http://127.0.0.1/web/message?text=Installed+Oscam+version+($OSCAM_LOCAL_VERSION)+is+current.%0ANo+need+to+update.&type=1&timeout=10" > /dev/null 2>&1     # show WebGUI info message
fi

#### Remove all temporary files (sub-directory)
rm -rf $TMP_DIR



echo "---------------------------"

exit 0
