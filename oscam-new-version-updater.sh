#!/bin/bash


#######################################
# Oscam new version updater
# 2019-10, s3n0
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
#######################################



LOCAL_OSCAM_BINFILE=$(find /usr/bin -name oscam* | head -n 1)
[ -z "$LOCAL_OSCAM_BINFILE" ] && { LOCAL_OSCAM_BINFILE="/usr/bin/oscam"; echo "No Oscam binary file found. The default path and filename $LOCAL_OSCAM_BINFILE will be used to download and add a new Oscam binary file."; } || echo "Oscam binary file $LOCAL_OSCAM_BINFILE was found."

## LOCAL_OSCAM_BINFILE="/usr/bin/oscam"
## [ -f $LOCAL_OSCAM_BINFILE ] || { echo "ERROR ! User-configured binary file $LOCAL_OSCAM_BINFILE not found !"; exit 1; }

## LOCAL_OSCAM_BINFILE=$(ps --no-headers -f -C oscam | sed 's@.*\s\([\-\_\/a-zA-Z]*\)\s.*@\1@' | head -n 1)
## [ -z "$LOCAL_OSCAM_BINFILE" ] && { LOCAL_OSCAM_BINFILE="/usr/bin/oscam"; echo "No Oscam process name found. The default file name $LOCAL_OSCAM_BINFILE will be used to download and add a new Oscam."; } || echo "Oscam process $LOCAL_OSCAM_BINFILE found."


REQUESTED_BUILD="oscam-trunk"

# - some examples of Oscam builds included on the feed server, there is possible to change one of them:
#      oscam-trunk
#      oscam-trunk-ipv4only
#      oscam-stable
#      oscam-stable-ipv4only



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
dest=""
if os.environ.get('D'):
        dest=os.environ.get('D')
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

#### Download and unpack the list of all available packages + Find out the package name according to the required Oscam edition
echo -n "Downloading and unpacking the list of softcam installation packages... "
IPK_FILENAME=$(wget -q -O - "$BASE_FEED/$OEVER/$ARCH/Packages.gz" | gunzip -c | grep "Filename:" | grep "$REQUESTED_BUILD"_1.20 | cut -d " " -f 2)
[ -z "$IPK_FILENAME" ] && { echo " failed!"; exit 1; } || echo " done."

#### Finding out if there is a newer version of Oscam on the internet
OSCAM_LOCAL_VERSION=$(  $LOCAL_OSCAM_BINFILE --build-info | grep -i 'version:' | grep -o '.....$'  )    # output result is, as example:  11540
[ -z "$OSCAM_LOCAL_VERSION" ] && OSCAM_LOCAL_VERSION="11000"                                            # as a precaution if there is no Oscam on the flash drive yet
OSCAM_ONLINE_VERSION=$( echo $IPK_FILENAME | sed -e 's/.*svn\([0-9]*\)-.*/\1/'  )                       # output result is, as example:  11546
echo -e "Oscam version on internet:\t$OSCAM_ONLINE_VERSION\nOscam version on flash drive:\t$OSCAM_LOCAL_VERSION"
if [ "$OSCAM_ONLINE_VERSION" -gt "$OSCAM_LOCAL_VERSION" ]; then
    echo "A new version of Oscam has been found and will be updated."
    # wget -qO- "http://127.0.0.1/web/message?text=New+Oscam+version+found+($OSCAM_ONLINE_VERSION)%0ANew+version+will+updated+now.&type=1&timeout=10" > /dev/null 2>&1
else
    echo "Installed Oscam version is current. No need to update."
    # wget -qO- "http://127.0.0.1/web/message?text=Installed+Oscam+version+($OSCAM_LOCAL_VERSION)+is+current.%0ANo+need+to+update.&type=1&timeout=10" > /dev/null 2>&1
    exit 0
fi

#### Create a temporary sub-directory and go in
rm -fr /tmp/aaa ; mkdir -p /tmp/aaa ; cd /tmp/aaa

#### Download the necessary Oscam installation package
echo -n "Downloading the necessary Oscam installation package... "
wget -q --show-progress -O /tmp/aaa/$IPK_FILENAME $BASE_FEED/$OEVER/$ARCH/$IPK_FILENAME && echo " done." || { echo " failed!"; exit 1; }

#### Checking if the 7zip archiver is installed on system
if ! 7z > /dev/null 2>&1 ; then
    echo "ERROR ! The 7zip archiver was not found ! Please install the 7zip archiver !"
    echo "For example, using the following commands:   opkg update && opkg install p7zip-full"
    exit 1
fi

#### Extracting the IPK package
echo "---------------------------"
echo "Extracting the IPK package:"
7z e $IPK_FILENAME                         # 1. splitting linked files ("ar" archive) - since "ar" separates files from the archive with difficulty, so I will use "7z" archiver
7z e data.tar.?z                           # 2. unpacking the ".gz" OR ".xz" archive
7z e data.tar ./usr/bin/$REQUESTED_BUILD   # 3. unpacking ".tar" archive, but only one file - i.e. an oscam binary file, for example as "oscam-trunk"
echo -n "The Oscam binary file has "; [ -f /tmp/aaa/$REQUESTED_BUILD ] && echo "been successfully extracted." || { echo "not been extracted! Please check the folder '/tmp/aaa'."; exit 1; }
echo "---------------------------"

#### Specify a startup softcam script (usually in the '/etc/init.d' folder)
[ -f /etc/init.d/softcam ] && INITD_SCRIPT=/etc/init.d/softcam
[ -f /etc/init.d/softcam.oscam ] && INITD_SCRIPT=/etc/init.d/softcam.oscam
[ -z "$INITD_SCRIPT" ] && echo -e "WARNING ! Softcam control script (usually placed in the '/etc/init.d' folder) not found. \nPlease download some autostart softcam script + set the execution rights \nand apply the particular run-level. \nFor example using the following commands: \nwget -O /etc/init.d/softcam --no-check-certificate https://github.com/s3n0/e2scripts/raw/master/softcam && chmod +x /etc/init.d/softcam && update-rc.d softcam defaults 90"

#### Run a separate process in the background
echo "Starting a separate process in the background, for replace oscam binary file."
echo "The new Oscam binary file will replaced now."
echo "If you start the script via the Oscam Webif, please wait 10 seconds and reload the Oscam Webif."
sleep 5

background_process() {    
    #### Replace the oscam binary file with new one
    [ -z "$INITD_SCRIPT" ] || $INITD_SCRIPT stop
    if ps -C ${LOCAL_OSCAM_BINFILE##*/} > /dev/null 2>&1 ; then killall -9 ${LOCAL_OSCAM_BINFILE##*/} ; fi     # if "init.d" script was not found, the task must to be killed
    sleep 1
    mv -f /tmp/aaa/$REQUESTED_BUILD $LOCAL_OSCAM_BINFILE
    chmod 755 $LOCAL_OSCAM_BINFILE
    [ -z "$INITD_SCRIPT" ] || $INITD_SCRIPT start

    #### Remove all temporary files (sub-directory)
    rm -fr /tmp/aaa
}
background_process &

