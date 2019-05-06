+ **softcam.sh**
   > - OSCam startup script '/etc/init.d/softcam' for Enigma2 based set-top-box
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

+ **softcam-feed-universal_3.0_setup_script.sh**
   > - script to add another feed source with softcam packages
   > - the script was pulled from IPK package "softcam-feed-universal_3.0_all.ipk"
   > - beware, this is not an IPK-package which is useless I think, but it's a bash script only
