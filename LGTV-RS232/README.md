RS-232 Basics
=============

- command to display available serial interfaces under UNIX / LINUX systems:
  `setserial -g /dev/ttyS[0123]`

- command for listing of available serial ports and especially access rights to them:
  `ls -l /dev/ttyS*`

- if you cannot turn off the LG-TV with the echo command, it is quite possible that you do not have write access rights to the serial port
- so try setting up serial port access rights if necessary:
  `chmod o+rw /dev/ttyS0`

- use the following commands to test the functionality of the RS-232 communication, after connecting the null-modem cable between the set-top-box and the LG-TV
- these are echo commands, for direct sending of codes (ASCII characters) to LG-TV serial interface or serial port in system:
- turning off LG-TV:    `echo "ka 01 00" > /dev/ttyS0`
- turning on LG-TV:     `echo "ka 01 01" > /dev/ttyS0`

- if the TV is still not communicating or not wanting to turn it off or on, it would have to try to configure the interface
  RS-232 in a slower speed box, e.g. to 9600 (for older LG-TV)
- to print the current configuration of the first port "S0" enter the command:
  `stty -F /dev/ttyS0 -a`
- the speed of the "S0" port interface to 9600bps can be changed by the following command:
  `stty -F /dev/ttyS0 9600`
- for some linux distributions it seems to have a separate setup for output and input, as follows:
  `stty -F /dev/ttyS0 ispeed 9600 ospeed 9600`

- the CAT command is normally used to dump the contents of a file to standard output (stdout = in the case of a terminal, it is the screen of your monitor / terminal)
- here's how to use it to extract content from input on the set-top-box:
  `cat < /dev/ttyS0`
- another example of reading a serial port input and displaying results on stdout (in hexadecimal, i.e. byte - one by one):
  `od -x < /dev/ttyS0`

Note:
=====
After restarting the set-top box, the Standby.py script starts to work only after it is activated (except for the second shutdown + TV on). I haven't found out yet why it is. So don't worry if the TV doesn't turn off after the set-top box is restarted. Try it again and then it will still work.
