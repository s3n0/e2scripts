#!/bin/bash

# sh script for Enigma2 - the IPK package creation tool
# 2018-2023, by s3n0
#
# Simple creation of an IPK package without the use of OPKG-TOOLS.
# It's just a simple archiving of files or folders and then merging the created files into one.
#
# A note:
#
# The version of the plugin is taken from the "version.txt" file, which must always be present
# in the same folder where the plugin is located. I also use it in the plugin's own algorithm.
#
# It is also important to edit the created "control" file below - in this script, according to the needs of your project / plugin !




#### specify the plugin folder, the plugin version, the package output path + package filename, etc. :

PLUGIN_NAME="Project XYZ"

PLUGIN_DIR="/usr/lib/enigma2/python/Plugins/Extensions/"`echo "${PLUGIN_NAME}" | tr -d " -"`    # PLUGIN_NAME: delete all " " and "-" characters
PLUGIN_LANG_DIR="${PLUGIN_DIR}/locale"

PROJECT_DIR="/tmp/${RANDOM}"
BUILD_DIR="/tmp/${RANDOM}"

VER=$(cat "$PLUGIN_DIR/version.txt")        # VER="1.0.0"
ARCH="all"                                  # chipset / CPU architecture dependency:  all, mips32el, mipsel, armv7ahf-neon, cortexa15hf-neon-vfpv4, aarch64, ...etc.

IPK_PCKGNAME="enigma2-plugin-extensions-"`echo "${PLUGIN_NAME,,}" | tr " " "-"`                 # PLUGIN_NAME: lower case, replace all spaces with "-"
IPK_FILENAME="${IPK_PCKGNAME}_${VER}_${ARCH}.ipk"
IPK_FINISHED="/tmp/${IPK_FILENAME}"

# the description of the plugin will be extracted from the file "plugin.py":
#PLUGIN_DESCRIPTION=$(awk '/def Plugins/,/\]\s\n/' $PLUGIN_DIR/plugin.py | grep -E 'description.*=' | sed -e 's/.*description\s\=\s["'\'']//' -e 's/["'\''].*//')
# Warning : most Enigma2 distributions usually compile the found "*.pyo" files into "*.py" format after a restart and thus the possibility of getting the description from the "plugin.py" file is also lost!
# if you don't want or don't use the plugin definition in the "plugin.py" file, you can use your own definition here, for example:
PLUGIN_DESCRIPTION="Plugin for the needs of the Project XYZ tests"




# ==== preinst ========= (before installing a package) =====
# This script executes before that package will be unpacked from its Debian archive (".deb/.ipk") file. 
# Many 'preinst' scripts stop services for packages which are being upgraded until their installation or
# upgrade is completed (following the successful execution of the 'postinst' script).
#
# ==== postinst ======== (after installing a package) ======
# This script typically completes any required configuration of the package foo once foo has been unpacked from its Debian archive (".deb/.ipk") file.
# Often, 'postinst' scripts ask the user for input, and/or warn the user that if he accepts default values, he should remember to go back and re-configure that package
# as the situation warrants. Many 'postinst' scripts then execute any commands necessary to start or restart a service once a new package has been installed or upgraded.
#
# ==== prerm =========== (before removing a package) =======
# This script typically stops any daemons which are associated with a package. It is executed before the removal of files associated with the package.
#
# ==== postrm ========== (after removing a package) ========
# This script typically modifies links or other files associated with foo, and/or removes files created by the package.





#### prepare the CONTROL folder and all neccessary shell scripts inside of this folder:
rm -rf ${PROJECT_DIR}
mkdir -p ${PROJECT_DIR} ${PROJECT_DIR}/CONTROL



cat > ${PROJECT_DIR}/CONTROL/control << EOF
Package: ${IPK_PCKGNAME}
Version: ${VER}
Description: ${PLUGIN_DESCRIPTION}
Architecture: ${ARCH}
Section: extra
Priority: optional
Maintainer: MY_NICKNAME_AS_EXAMPLE
License: GPLv2
Homepage: https://MY_WEBPAGE.EXAMPLE.COM
EOF
# For more info about other fields, see here: https://www.debian.org/doc/debian-policy/ch-controlfields.html ; https://www.systutorials.com/docs/linux/man/5-deb-control/ ; https://linux.die.net/man/5/deb-control

cat > ${PROJECT_DIR}/CONTROL/postinst << EOF
#!/bin/sh
echo "*********************************************************"
echo "                  ${PLUGIN_NAME} ${VER}                  "
echo "                Enigma2 plugin/extension                 "
echo "*********************************************************"
echo " Successfully INSTALLED. You should restart Enigma2 now. "
echo "*********************************************************"
exit 0 
EOF

cat > ${PROJECT_DIR}/CONTROL/postrm << EOF
#!/bin/sh
[ "\$1" != "upgrade" ] || exit 0 > /dev/null 2>&1              # prevent the OE2.5+ based Enigma2 for deleting files when the package is "upgrading"
rm -rf ${PLUGIN_DIR}
echo "*********************************************************"
echo "                  ${PLUGIN_NAME} ${VER}                  "
echo "                Enigma2 plugin/extension                 "
echo "*********************************************************"
echo "  Successfully REMOVED. You should restart Enigma2 now.  "
echo "*********************************************************"
exit 0
EOF


chmod a+x ${PROJECT_DIR}/CONTROL/*





#### remove all comments from the source code
#if [ -f /usr/script/remove_comments.sh ]; then
#    /usr/script/remove_comments.sh $PLUGIN_DIR/plugin.py
#    init 4; sleep 5; init 3; sleep 20       # restart Enigma - for recompile the source code again - after removing all comments from the source code file
#fi




#### translate language files from .PO to .MO format (Machine Object)
#### if necessary, install the language translation tools:  opkg install gettext
msgfmt --help > /dev/null 2>&1 || opkg install gettext          # if the translation tool fails to start, an attempt is made to install it
msgfmt --help > /dev/null 2>&1 \
 && { for f in `find $PLUGIN_LANG_DIR -name *.po`; do msgfmt -o ${f%.po}.mo $f; rm -f $f; done; } \
 || echo -e "--- Warning ! \n--- The 'msgfmt' tool or the 'gettext' package does not exist. \n--- Unable to translate language '.po' files to '.mo' format."




#### prepare a copy of $PLUGIN_DIR to $PROJECT_DIR
mkdir -p ${PROJECT_DIR}/${PLUGIN_DIR}
cp -rp ${PLUGIN_DIR}/* ${PROJECT_DIR}/${PLUGIN_DIR}

#### prepare a copy of $ANOTHER_DIR to $PROJECT_DIR
# ANOTHER_DIR="/etc/iptv"
# mkdir -p ${PROJECT_DIR}/${ANOTHER_DIR}
# cp -rp ${ANOTHER_DIR}/* ${PROJECT_DIR}/${ANOTHER_DIR}

#### remove unnecessary files and folders
rm -rf ${PROJECT_DIR}/${PLUGIN_DIR}/*.py                       # remove all source-code python files
#rm -rf ${PROJECT_DIR}/${PLUGIN_DIR}/*.pyo                      # remove all compiled python files (bytecode files - optimized)
#rm -rf ${PROJECT_DIR}/${PLUGIN_DIR}/*.pyc                      # remove all compiled python files (bytceode files)
#rm -rf ${PROJECT_DIR}/${PLUGIN_DIR}/__pycache__

#### create archive files "control.tar.gz" and "data.tar.gz" + create the text file "debian-binary" in $BUILD_DIR
mkdir -p ${BUILD_DIR}
tar -C ${PROJECT_DIR} --exclude='CONTROL' -czf ${BUILD_DIR}/data.tar.gz .
tar -C ${PROJECT_DIR}/CONTROL -czf ${BUILD_DIR}/control.tar.gz .
echo -e "2.0" > ${BUILD_DIR}/debian-binary

#### combining all three files together (into IPK package)
#### using the "ar" archiver to merge all 3 files in the following order:   1) debian-binary    2) control.tar.gz    3) data.tar.gz
cd ${BUILD_DIR}
rm -f ${IPK_FINISHED}
ar -r ${IPK_FINISHED} ./debian-binary ./control.tar.gz ./data.tar.gz




#### make a copy of the .ipk file, but with a .deb extension
#### replace "/" by " " character from the end of filenames inside the "ar" archive
cp -f ${IPK_FINISHED} ${IPK_FINISHED%.ipk}.deb
sed -i 's/debian-binary\//debian-binary /g' ${IPK_FINISHED%.ipk}.deb
sed -i 's/control.tar.gz\//control.tar.gz /g' ${IPK_FINISHED%.ipk}.deb
sed -i 's/data.tar.gz\//data.tar.gz /g' ${IPK_FINISHED%.ipk}.deb
#replaceByte() {
#    printf "$(printf '\\x%02X' $3)" | dd of="$1" bs=1 seek=$2 count=1 conv=notrunc &> /dev/null
#} #### USAGE:  replaceByte "filename" offset byte
#replaceByte "${IPK_FINISHED%.ipk}.deb" 21 32    
#replaceByte "${IPK_FINISHED%.ipk}.deb" 86 32
#sed -i 's/data.tar.gz\//data.tar.gz /g' ${IPK_FINISHED%.ipk}.deb



#### remove all temporary directories
rm -rf ${PROJECT_DIR} ${BUILD_DIR}



exit
