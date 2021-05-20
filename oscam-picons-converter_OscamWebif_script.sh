#!/bin/bash

# First you need to add to the 'oscam.conf' file, an entry to specify the shell script directory ... for example:
#     httpscript = /usr/script
# Then you need to place the script in this folder, including the script for converting to OscamWebif picon format.
# Both shell-scripts must have execution attributes assigned to them ... for example:
#     chmod a+x /usr/script/oscam-picons*
# You can set the parameters for picon conversion according to yourself, i.e. $SCR_PARAMS variable.
# The script is run in OscamWebif via the 'Script' menu.

SCR_NAME="oscam-picons-converter.py"
#SCR_PARAMS="-d -q -1 -c 0624,0D96,FFFE"
SCR_PARAMS="-d -q -a -c 0624,0D96,FFFE"               # 0624,0D96 = Skylink sat-provider, FFFE = Free-To-Air channels (for dvbapi user in OscamWebif)
SCR_PATH="/usr/script"
LOG_FILE="/tmp/${SCR_NAME%.*}.log"

[ -f "${SCR_PATH}/${SCR_NAME}" ] || { echo "Error ! The script-file '${SCR_PATH}/${SCR_NAME}' was not found !"; exit 1; }

/usr/bin/python $SCR_PATH/$SCR_NAME $SCR_PARAMS > $LOG_FILE 2>&1 &

echo "The python script '${SCR_NAME}' has been started - it will run in the background."
echo "To verify that the script is working properly, you can check the '${LOG_FILE}' file,"
echo "after a few minutes or seconds (depending on the picons generation speed)."
echo "Bye."

exit 0
