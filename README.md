## Simple scripts for Enigma 2, focused on OpenATV and OpenPLi.

+ **LGTV-RS232 directory**
   > - switching on and off the LG TV via RS-232 interface

+ **softcam**
   > - OSCam startup bash script '/etc/init.d/softcam' for Enigma2 based set-top-box
   > - the script also verifies that Oscam has been successfully started / stopped
   > - it also records its activity in a temporary LOG-file
   > - more info can be found in the script
   > - if you need to use this script for CCCam, please use the following 'sed' command:
   ``` 
       sed -i -e 's/oscam/cccam/I' -e 's/OSCam/CCCam/I' -e 's/-b -r 2 -c/-C/I' /etc/init.d/softcam
   ```
+ **make_ipk_by_s3n0_for_ProjectXYZ.py**
   > - IPK creation tool for Enigma2, debugged and tested on OpenATV

+ **oscam-picons-converter.py**
   > - simple script to convert PNG picons to TPL picons - for the needs of Oscam Webif (Oscam WebGUI)
   > - TPL picon names are determined by srvid or srvid2 databases

+ **epg_refresh.py**
   > - simple python script for Enigma2 based set-top-box, for refresh EPG data on all DVB channels
   > - the script will find all the necessary transponders what you need to zapping
   > - transponders are selected from the userbouquet and zap only once
   > - the best way to use EPG refresh is to add a new task to the CRON scheduler ... be sure to set the file attributes (`chmod 755 /usr/script/epg_refresh.py`) ... for example, to run the python script every 2th day at 03:00, as the background process, use the following line:
   
   ```
       0 3 */2 * *        python /usr/script/epg_refresh.py &
   ```

+ **backrest**
   > - simple bash script for backing up and restoring user-defined settings, files or folders in Enigma2
   > - disadvantage is the need to manually edit this script after each new function is added to Enigma (plugins, binary files, scripts, etc.) for full backup or restore

+ **picons-downloader.sh**
   > - simple bash script for download & extract picons from Google-Drive server, which are compressed with 7zip (i.e. 7zip archivator is required)

+ **oscam-new-version-updater.sh**
   > - script checks if there is a newer version on the internet and if so, updates the binary file extracted from the downloaded IPK package
   > - 7zip archiver is required since 'ar' tool is a problematic ('ar' is part of the limited [BusyBox](https://busybox.net/) in most cases) when splitting files from IPK packages

+ **oscam_emm_refresh.sh**
   > - script for re-refreshing EMM packets by tuning a specific DVB channel for a short time (1 minute) while the device is in Standby mode ... after this short time the DVB channel stops again (DVB reception stops again)
   > - to tune and stop the DVB channel is used the Enigma Webif interface
   > - to determine the duration of Standby mode is used the Oscam Webif interface

+ **bouquetx.sh**
   > - shell script to download userbouquet file from internet and overwrite local userbouquet file, but only if there is a change in the file (tested for file content differences)
   > - it is based on "init 4" and "init 3" reboots of Enigma as the most reliable method for all Enigma distributions
