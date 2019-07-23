Switching on and off the LG TV via RS-232 serial interface
==========================================================

- command to display basic serial interfaces under LINUX systems:
  - `setserial -g -a /dev/ttyS[0123]`

- command for listing of all available serial interfaces and especially access rights to them:
  - `ls -l /dev/ttyS*`

- there are two echo commands for direct sending of codes (ASCII characters) to LG-TV serial interface, so, as first use the following commands to test the functionality of the RS-232 communication, after connecting the null-modem cable between the set-top-box and the LG-TV (https://www.opena.tv/english-section/32512-solution-standby-mode-lg-tv-hdmi-cec-simplink.html):
  - turning off LG-TV:     `echo "ka 01 00" > /dev/ttyS0`
  - turning on LG-TV:      `echo "ka 01 01" > /dev/ttyS0`

- if your LG-TV has not turned off via the serial interface with the help of an echo command, then it is possible that you do not have access rights to the serial interface (write)... so try setting up serial interface access rights if necessary:
  - `chmod o+rw /dev/ttyS0`

- if the TV is still not communicating (TV turn off and on), it would have to try to configure the interface
  RS-232 to a slower speed, e.g. 9600 (for older LG TV)
  - display the current configuration of the "S0" interface:  `stty -F /dev/ttyS0 -a`
  - set the speed of the "S0" interface to 9600 bps:  `stty -F /dev/ttyS0 9600`
  
- for some linux distributions it seems to have a separate setup for output and input, as follows:
  - `stty -F /dev/ttyS0 ispeed 9600 ospeed 9600`

- the `cat` command is normally used to display the contents of a file to standard output `stdout` but we can also display the serial interface input ... here's how to use it to extract content from input on the set-top-box:
  - `cat < /dev/ttyS0`
- another example of reading a serial port input and displaying results on stdout (in hexadecimal, i.e. byte - one by one):
  - `od -x < /dev/ttyS0`

A note
======
After restarting the set-top box, the bash script will be run via the code in "Standby.py" only after the second activation of standby mode. I haven't found out yet why it is. So don't worry if the TV doesn't turn off after the set-top box is restarted. Try it again and then it will still work.
