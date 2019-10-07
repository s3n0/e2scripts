#!/bin/bash


#######################################
# Oscam new version updater - script
# 2019-10, s3n0
# This script is designed to avoid having to add another feed to your Enigma.
#######################################
# This script uses "updates.mynonpublic.com" as an update source and
# also uses the Python source code, from the script from here:
#       http://updates.mynonpublic.com/oea/feed
# The 'feed' script was developed for the purpose of installing softcam feed into Enigma:
#       wget -O - -q http://updates.mynonpublic.com/oea/feed | bash
#######################################


LOCAL_OSCAM_BINFILE="/usr/bin/oscam"    # Oscam executable/binary file with full directory path




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

#######################################

get_oever
get_arch
check_compat

#######################################
#######################################

#### Download the list of all available packages + find out the package name according to the required Oscam edition
echo -n "Downloading and unpacking the list of softcam installation packages... "
# - some examples of Oscam builds included on the feed server:
#   "trunk_1.20", "trunk-ipv4only_1.20", "stable_1.20", "stable-ipv4only_1.20", "emu_1.20", "emu-ipv4only_1.20", etc.
IPK_NAME=$(wget -q -O - "$BASE_FEED/$OEVER/$ARCH/Packages.gz" | gunzip -c | grep "trunk_1.20" | cut -d " " -f 2)
[ -z "$IPK_NAME" ] && { echo " failed!"; exit 1; } || echo " done."

#### Finding out if there is a newer version of Oscam on the internet
OSCAM_LOCAL_VERSION="11000"                                                                             # as a precaution if there is no Oscam on the flash drive yet
OSCAM_LOCAL_VERSION=$(   $LOCAL_OSCAM_BINFILE --build-info | grep -i 'version:' | grep -o '.....$'  )   # output result is, as example:  11540
OSCAM_ONLINE_VERSION=$(  echo $IPK_NAME | sed -e 's/.*svn\([0-9]*\)-.*/\1/'   )                         # output result is, as example:  11546
echo -e "Oscam version found online:\t$OSCAM_ONLINE_VERSION\nOscam version on flash drive:\t$OSCAM_LOCAL_VERSION"
if [ "$OSCAM_ONLINE_VERSION" -gt "$OSCAM_LOCAL_VERSION" ]; then
    echo "New Oscam version $OSCAM_ONLINE_VERSION is available and will updated now."
    # wget -qO- "http://127.0.0.1/web/message?text=New+Oscam+version+found+($OSCAM_ONLINE_VERSION)%0ANew+version+will+updated+now.&type=1&timeout=10" > /dev/null 2>&1
else
    echo "Installed Oscam version $OSCAM_LOCAL_VERSION is current. No need to update."
    # wget -qO- "http://127.0.0.1/web/message?text=Installed+Oscam+version+$OSCAM_LOCAL_VERSION+is+current.%0ANo+need+to+update.&type=1&timeout=10" > /dev/null 2>&1
    exit 0
fi

#### Create a temporary sub-directory
rm -fr /tmp/aaa ; mkdir -p /tmp/aaa ; cd /tmp/aaa

#### Download the necessary oscam package
echo -n "Downloading the necessary Oscam installation package... "
wget -q --show-progress -O /tmp/aaa/$IPK_NAME $BASE_FEED/$OEVER/$ARCH/$IPK_NAME && echo " done." || { echo " failed!"; exit 1; }

#### Checking if the 7zip archiver is installed on system
if ! 7z > /dev/null 2>&1 ; then
    echo "ERROR ! The 7zip archiver was not found ! Please install the 7zip archiver !"
    echo "For example, using the following commands:   opkg update && opkg install p7zip-full"
    exit 1
fi

#### Extracting the IPK package
7z e $IPK_NAME                           # 1. splitting linked files ("ar" archive) - since "ar" separates files from the archive with difficulty, so I will use "7z" archiver
7z e data.tar.?z                         # 2. unpacking the ".gz" OR ".xz" archive
7z e data.tar ./usr/bin/oscam-trunk      # 3. unpacking ".tar" archive, but only one "oscam-trunk" file
echo -n "The Oscam binary file has "; [ -f /tmp/aaa/oscam-trunk ] && echo "been successfully extracted." || { echo "not been extracted! Please check the folder '/tmp/aaa'."; exit 1; }

#### Replace the oscam binary file with new one
/etc/init.d/softcam stop && mv -f /tmp/aaa/oscam-trunk $LOCAL_OSCAM_BINFILE && chmod 755 $LOCAL_OSCAM_BINFILE && /etc/init.d/softcam start

#### Remove all temporary files (sub-directory)
rm -fr /tmp/aaa

#######################################

exit 0
