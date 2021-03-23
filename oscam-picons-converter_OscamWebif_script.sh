#!/bin/sh

PYSCRIPT="/usr/script/oscam-picons-converter.py"
#PARAMS="-d -q -1 -c 0624,0D96,FFFE"
PARAMS="-d -q -a -c 0624,0D96,FFFE"               # 0624,0D96 = Skylink sat-provider, FFFE = Free-To-Air channels (for dvbapi user in OscamWebif)

/usr/bin/python $PYSCRIPT $PARAMS > /tmp/oscam-picons-converter.log 2>&1 &

echo "The python script 'oscam-picons-converter.py' has been started - it will run in the background."
echo "To verify that the script is working properly, you can check the '/tmp/oscam-picons-converter.log' file,"
echo "after a few minutes or seconds (depending on the picons generation speed)."
echo "Bye."

exit 0
