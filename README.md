## Simple scripts for Enigma 2, focused on OpenATV.

+ **LGTV-RS232 directory**
   > - switching on and off the LG TV via RS-232 interface

+ **softcam**
   > - OSCam startup bash script '/etc/init.d/softcam' for Enigma2 based set-top-box
   > - the script verifies that Oscam has been successfully started or stopped
   > - it also records its activity in a temporary LOG file
   > - if you need to use this script for CCCam, please use the following 'sed' command:
   ``` 
       sed -i -e 's/oscam/cccam/I' -e 's/OSCam/CCCam/I' -e 's/-b -r 2 -c/-C/I' /etc/init.d/softcam
   ```
+ **make_ipk_by_s3n0_for_ProjectXYZ.py**
   > - IPK creation tool for Enigma2, debugged and tested on OpenATV

+ **oscam-picons-converter.py**
   > - simple python script for converting PNG to TPL picons (for Oscam-Webif)

+ **epg_refresh.py**
   > - simple python script for Enigma2 based set-top-box, for refresh EPG data on all channels
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
