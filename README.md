+ **softcam**
   > - OSCam startup bash-script '/etc/init.d/softcam' for Enigma2 based set-top-box
   > - the script verifies that Oscam has been successfully started or stopped
   > - it also records its activity in a temporary LOG file
   > - if you need to use this script for CCCam, please use the following 'sed' command:
   ``` 
       sed -i -e 's/oscam/cccam/I' -e 's/OSCam/CCCam/I' -e 's/-b -r 2 -c/-C/I' /etc/init.d/softcam
   ```
+ **make_ipk_by_s3n0_for_ProjectXYZ.py**
   > - IPK plugin-package creation tool for Enigma2, debugged and tested on Enigma2/OpenATV

+ **OscamPiconsConverter.py**
   > - PNG to TPL picons converter (TPL picons for Oscam Webif in Enigma2)

+ **LGTV-RS232 directory**
   > - Switching on and off the LG TV via RS-232 interface

+ **epg_refresh.py**
   > - simple python-script for Enigma2 based set-top-box, for refresh EPG info
   > - the script will find all the necessary transponders you need to zap
   > - transponders are selected from the userbouquet and zap only once
   > - the best way how to use the refresh is add the python-script into the CRON scheduler:
   ```
       # to run the python-script every 5th day at 03:00 pm, add this new line into the CRON config file:
       0 3 */5 * *      python /usr/script/epg_refresh.py > /dev/null 2>&1
   ```
       
       
 
