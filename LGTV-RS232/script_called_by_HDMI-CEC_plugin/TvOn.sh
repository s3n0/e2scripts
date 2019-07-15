#!/bin/sh

# if directory does not exist, must be created the new one /usr/script/
# bash-script files must be located at this place: /usr/script/*.sh
# new script files in your Enigma2 must to have a execution rights: $ chmod 755 /usr/script/*.sh

# https://github.com/openatv/enigma2/blob/DEV/lib/python/Components/HdmiCec.py
# https://www.opena.tv/english-section/32512-solution-standby-mode-lg-tv-hdmi-cec-simplink.html

# shell command to Turning On the LG-TV through RS232 interface:

echo "ka 01 01" > /dev/ttyS0
