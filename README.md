+ **softcam.sh**
   > - OSCam startup script '/etc/init.d/softcam' for Enigma2 based set-top-box
   > - the script verifies that Oscam has been successfully started or stopped
   > - it also records its activity in a temporary LOG file
   > - if you need to use this script for CCCam, please use the following 'sed' commands:
   ``` 
       sed -i 's/oscam/cccam/I' /etc/init.d/softcam 
       sed -i 's/OSCam/CCCam/I' /etc/init.d/softcam
       sed -i 's/-c \//-C \//I' /etc/init.d/softcam
   ```

+ **make_ipk_by_s3n0_for_ProjectXYZ.py**
   > - IPK plugin-package creation tool for Enigma2, debugged and tested on Enigma2/OpenATV

+ **OscamPiconsConverter.py**
   > - PNG to TPL picons converter (TPL picons for Oscam Webif in Enigma2)
