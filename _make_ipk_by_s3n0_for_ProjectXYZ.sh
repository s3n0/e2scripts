#!/bin/sh


# sh script for Enigma2
# the IPK package creation tool
#
# 2018-2019, by s3n0
#
# Simple creation of an IPK package without the use of OPKG-TOOLS.
# It's just a simple archiving of files or folders and then merging the created files into one.
#
# A note:
# The version of the plugin is taken from the "version.txt" file, which must always be present
# in the same folder where the plugin is located. I also use it in the plugin's own algorithm.
#
# If the same version of the plugin has already been installed in the Enigma,
# or if only the plugin directory was deleted without uninstalling using the OPKG package manager
# then you must use a "force" method to install / remove plugin, such as:
#
#       opkg install --force-reinstall /<folder_name>/enigma2-plugin-extensions-projectxyz_1.0.181219_all.ipk
#       opkg remove --force-remove enigma2-plugin-extensions-projectxyz



#### specify the plugin folder and the IPK output file:
plugin_dir=/usr/lib/enigma2/python/Plugins/Extensions/ProjectXYZ
VER=$(cat "$plugin_dir/version.txt")
ipk_pckgname=enigma2-plugin-extensions-projectxyz
ipk_filename=${ipk_pckgname}_${VER}_all.ipk
ipk_target=/tmp/${ipk_filename}



#### prepare the CONTROL folder and all neccessary files into CONTROL folder:
rm -rf $plugin_dir/CONTROL
mkdir $plugin_dir/CONTROL

cat > ${plugin_dir}/CONTROL/control << EOF
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

cat > ${plugin_dir}/CONTROL/preinst << EOF
#!/bin/sh
rm -rf ${plugin_dir}
exit 0
EOF

cat > ${plugin_dir}/CONTROL/postinst << EOF
#!/bin/sh
echo "*********************************************************"
plugin_dir=${plugin_dir}
rm -fR $plugin_dir/CONTROL > /dev/null 2>&1
echo "*********************************************************"
echo "                  ProjectXYZ ${VER}                  "
echo "                Enigma2 plugin/extensions                "
echo "                   by s3n0 , 2016-2019                   "
echo "*********************************************************"
echo " Successfully installed. You should restart Enigma2 now. "
echo "*********************************************************"
exit 0 
EOF

cat > ${plugin_dir}/CONTROL/prerm << EOF
#!/bin/sh
exit 0
EOF

cat > ${plugin_dir}/CONTROL/postrm << EOF
#!/bin/sh
rm -rf ${plugin_dir}
exit 0
EOF




#### remove all source files (Python source code):
rm -rf $plugin_dir/*.py

#### as the first, it's a neccessary to set the execution rights to all files (mainly in the '/CONTROL' directory):
chmod -R 755 $plugin_dir

#### create archive file 'control.tar.gz' (without a relative path to the directory):
cd $plugin_dir/CONTROL
tar zcpv -f $plugin_dir/control.tar.gz *

#### create archive file 'data.tar.gz' (with a relative path to the directory):
tar zcpv -f $plugin_dir/data.tar.gz $plugin_dir/images/* $plugin_dir/plugin.pyo $plugin_dir/__init__.pyo $plugin_dir/version.txt

#### create version file 'debian-binary':
echo -e "2.0\n" > $plugin_dir/debian-binary

#### combining all three files together (into IPK package):
#### using the "ar" archiver to merge all 3 files in the following order:   1) debian-binary  2) control.tar.gz  3) data.tar.gz
rm -f $ipk_target
ar -r $ipk_target $plugin_dir/debian-binary $plugin_dir/control.tar.gz $plugin_dir/data.tar.gz

#### cleaning all three temporary files + 'CONTROL' directory:
rm -f $plugin_dir/control.tar.gz $plugin_dir/data.tar.gz $plugin_dir/debian-binary
rm -rf $plugin_dir/CONTROL


exit
