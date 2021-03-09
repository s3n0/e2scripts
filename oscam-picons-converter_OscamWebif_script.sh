#!/bin/sh

PYSCRIPT="/usr/script/oscam-picons-converter.py"
PARAMS="-d -q -1 -c 0624,0D96"

/usr/bin/python $PYSCRIPT $PARAMS > /tmp/oscam-picons-converter.log 2>&1 &

echo "The python script 'oscam-picons-converter.py' has been started ... it will run in the background."

exit 0
