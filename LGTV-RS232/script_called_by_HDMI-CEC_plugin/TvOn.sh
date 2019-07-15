#!/bin/sh

# if directory does not exist, must be created the new one /usr/script/
# bash-script files must be located at this place: /usr/script/*.sh
# new script files in your Enigma2 must to have a execution rights: $ chmod 755 /usr/script/*.sh

# shell command to Turning On the LG-TV through RS232 interface:

echo "ka 01 01" > /dev/ttyS0
