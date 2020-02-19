#!/bin/sh

# sh script for Enigma2 - the IPK package creation tool
# 2018-2019, by s3n0
#
# Simple creation of an IPK package without the use of OPKG-TOOLS.
# It's just a simple archiving of files or folders and then merging the created files into one.
#
# A note:
#
# The version of the plugin is taken from the "version.txt" file, which must always be present
# in the same folder where the plugin is located. I also use it in the plugin's own algorithm.




#### specify the plugin folder, the plugin version and the IPK output file:

plugin_dir=/usr/lib/enigma2/python/Plugins/Extensions/ProjectXYZ
ipk_pckgname=enigma2-plugin-extensions-projectxyz

VER=$(cat "$plugin_dir/version.txt")
ipk_filename=${ipk_pckgname}_${VER}_all.ipk
ipk_targetfile=/tmp/${ipk_filename}

project_dir=/tmp/${RANDOM}
build_dir=/tmp/${RANDOM}




# ==== preinst ==== (before installing a package) ===
# This script executes before that package will be unpacked from its Debian archive (".deb/.ipk") file. Many 'preinst' scripts stop services for packages which are being upgraded until their installation or upgrade is completed (following the successful execution of the 'postinst' script).
#
# ==== postinst === (after installing a package) ====
# This script typically completes any required configuration of the package foo once foo has been unpacked from its Debian archive (".deb/.ipk") file. Often, 'postinst' scripts ask the user for input, and/or warn the user that if he accepts default values, he should remember to go back and re-configure that package as the situation warrants. Many 'postinst' scripts then execute any commands necessary to start or restart a service once a new package has been installed or upgraded.
#
# ==== prerm ====== (before removing a package) =====
# This script typically stops any daemons which are associated with a package. It is executed before the removal of files associated with the package.
#
# ==== postrm ===== (after removing a package) ======
# This script typically modifies links or other files associated with foo, and/or removes files created by the package. 




#### prepare the CONTROL folder and all neccessary files into CONTROL folder:
rm -rf ${project_dir}/CONTROL
mkdir -p ${project_dir} ${project_dir}/CONTROL


cat > ${project_dir}/CONTROL/control << EOF
Package: ${ipk_pckgname}
Version: ${VER}
Description: Plugin for testing purpose (Enigma2 plugin)
Section: extra
Priority: optional
Maintainer: s3n0
License: GPLv3
Architecture: all
OE: ${ipk_pckgname}
Homepage: N/A
Depends:
Source: N/A
EOF

cat > ${project_dir}/CONTROL/postinst << EOF
#!/bin/sh
echo "*********************************************************"
echo "                  ProjectXYZ ${VER}                  "
echo "                Enigma2 plugin/extensions                "
echo "                   by s3n0 , 2016-2019                   "
echo "*********************************************************"
echo " Successfully INSTALLED. You should restart Enigma2 now. "
echo "*********************************************************"
exit 0 
EOF

cat > ${project_dir}/CONTROL/postrm << EOF
#!/bin/sh
[ "$1" != "upgrade" ] || exit 0 > /dev/null 2>&1               # prevent the OE2.5+ based Enigma2 for deleting files when the package is "upgrading"
rm -rf ${plugin_dir}
echo "*********************************************************"
echo "                  ProjectXYZ ${VER}                  "
echo "                Enigma2 plugin/extensions                "
echo "                   by s3n0 , 2016-2019                   "
echo "*********************************************************"
echo "  Successfully REMOVED. You should restart Enigma2 now.  "
echo "*********************************************************"
exit 0
EOF


chmod 755 ${project_dir}/CONTROL/*




#### remove all source files (Python source code):
#### WARNING - make sure your source codes are backed up !
rm -rf ${plugin_dir}/*.py

#### translate locale language files from .PO to .MO format (Machine Object)
#### if neccessary, install the locale translation tools:     opkg install gettext
msgfmt --help > /dev/null 2>&1 || opkg install gettext
for f in `find $plugin_dir/locale -name *.po`; do msgfmt -o ${f%.po}.mo $f; rm -f $f; done



#### prepare a copy of plugin_dir to project_dir
mkdir -p ${project_dir}/${plugin_dir}
cp -rp ${plugin_dir}/* ${project_dir}/${plugin_dir}

#### create two archive files "control.tar.gz" and "data.tar.gz" + also the file "debian-binary" into build_dir
mkdir -p ${build_dir}
tar -C ${project_dir} --exclude='CONTROL' -czf ${build_dir}/data.tar.gz .
tar -C ${project_dir}/CONTROL -czf ${build_dir}/control.tar.gz .
echo -e "2.0" > ${build_dir}/debian-binary

#### combining all three files together (into IPK package)
#### using the "ar" archiver to merge all 3 files in the following order:   1) debian-binary    2) control.tar.gz    3) data.tar.gz
cd ${build_dir}
rm -f ${ipk_targetfile}
ar -r ${ipk_targetfile} ./debian-binary ./control.tar.gz ./data.tar.gz



#### make a copy from .ipk package to .deb package
#### replace "/" by " " character from the end of filenames inside the "ar" archive
cp -f ${ipk_targetfile} ${ipk_targetfile%.ipk}.deb
sed -i 's/debian-binary\//debian-binary /g' ${ipk_targetfile%.ipk}.deb
sed -i 's/control.tar.gz\//control.tar.gz /g' ${ipk_targetfile%.ipk}.deb
sed -i 's/data.tar.gz\//data.tar.gz /g' ${ipk_targetfile%.ipk}.deb
#replaceByte() {
#    printf "$(printf '\\x%02X' $3)" | dd of="$1" bs=1 seek=$2 count=1 conv=notrunc &> /dev/null
#} #### USAGE:  replaceByte "filename" offset byte
#replaceByte "${ipk_targetfile%.ipk}.deb" 21 32    
#replaceByte "${ipk_targetfile%.ipk}.deb" 86 32
#sed -i 's/data.tar.gz\//data.tar.gz /g' ${ipk_targetfile%.ipk}.deb



#### cleaning all temporary directories
rm -rf ${project_dir} ${build_dir}



exit

