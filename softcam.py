#!/bin/bash

# 2011/01/26:
# - OSCam Start/Stop/Restart example script - http://www.streamboard.tv/wiki/OSCam/en/ShellCommands#Starting_and_stopping_OSCam

# 2018/07/16:
# - s3n0 edit (OpenATV target file:  /etc/init.d/softcam)
# - in many Enigmas, the /etc/init.d/softcam startup script is directly supported through the embedded source code
#   (for example, the OpenATV source code: /lib/python/Plugins/Extensions/Infopanel/plugin.py)
# - so just copy the bash-script into the /etc/init.d folder and nothing else is needed (symbolic links to /etc/rc3.d and /etc/rc4.d are not necessary)
# - please do not forget to set the execution rights for bash script:  chmod +x /etc/init.d/softcam
# - if the softcam autostart script is not supported directly in your Enigma2, then you must additionally create a symbolic link:
#      ln -sf /etc/init.d/softcam /etc/rc3.d/S90softcam 
#   ...or use the tools :
#      update-rc.d softcam defaults 90

# 2019/03/24
# - s3n0 edit - remake the logging concept (logging output via function)

# ####################  USER SETUP  ########################
# ----------------------------------------------------------
# SOFTCAM BINARY DIRECTORY:
softcam_dir='/usr/bin'
# ----------------------------------------------------------
# SOFTCAM PROCESS NAME (BINARY FILE NAME):
softcam_exec='oscam'
# ----------------------------------------------------------
# SOFTCAM ARGUMENTS:    (a note: argument "-c" for OSCam determines a configuration directory, for more info use "/usr/bin/oscam --help")
softcam_args='-b -r 2 -c /etc/tuxbox/config/oscam'
# ----------------------------------------------------------
# Waiting time to kill the softcam process by standard SIGTERM (-15). Then softcam process will be killed with force SIGKILL (-9).
softcam_kill_waiting=5
# ----------------------------------------------------------
# SOFTCAM LOG DIR & FILE NAME:
softcam_logfile='/tmp/oscam_handling.log'
# ----------------------------------------------------------
# PRIVATE VARIABLES:
hrline='------------------------------------------------------------'
helptext="USAGE:    bash /etc/init.d/softcam <ARGUMENT>
ARGUMENT: start|restart|reload......start the process (if the process is still running then will stopped or killed... then it will start again)
          stop......................stop and unload the $softcam_exec service from memory"
# ----------------------------------------------------------
# ###############  END OF THE USER SETUP  ##################




# FUNCTIONS ************************************************

fLog() {
    #echo `date '+%Y-%m-%d %H:%M:%S'`" $1" > /dev/null                          ### null device   <---  log will disabled (do nothing)
    #echo `date '+%Y-%m-%d %H:%M:%S'`" $1" >> $softcam_logfile                  ### file
    #echo `date '+%Y-%m-%d %H:%M:%S'`" $1" >> $softcam_logfile 2>&1             ### file + stderr
    #echo `date '+%Y-%m-%d %H:%M:%S'`" $1" | tee -a $softcam_logfile            ### file + stdout(display)
    echo `date '+%Y-%m-%d %H:%M:%S'`" $1" 2>&1 | tee -a $softcam_logfile       ### file + stdout(display) + stderr
}

fStop() {
    if ! pidof $1 > /dev/null; then
        fLog "No $1 process is running!"
    else
        fLog "Stopping $1..."
        fLog "...sending a default SIGTERM signal to PID $(pidof $1)"
        kill -15 $(pidof $1) > /dev/null
        sleep 1
        if pidof $1 > /dev/null; then
            i=$softcam_kill_waiting
            while expr $i != 0 > /dev/null
            do
                if pidof $1 > /dev/null; then
                    fLog "...waiting for termination: $i seconds"
                    sleep 1
                else
                    fLog "...$1 was terminated using the default SIGTERM signal."
                    break
                fi
                i=`expr $i - 1`
            done
        else
            fLog "...$1 was terminated using the default SIGTERM signal."
        fi
        if pidof $1 > /dev/null; then
            fLog "...sending a forced SIGKILL signal to $1 process"
            killall -9 $1 > /dev/null
            if pidof $1 > /dev/null; then
                fLog "...$1 was not killed by a forced SIGKILL signal! This is probably a system error!"
            else
                fLog "...$1 was killed using the forced SIGKILL signal."
            fi
        fi
    fi
}

fStopAndStart() {
    if pidof $1 > /dev/null; then fStop $1; fi
    fLog "Starting $1..."
    fLog "CMD-line:  $softcam_dir/$1 $softcam_args"
    $softcam_dir/$1 $softcam_args > /dev/null
    sleep 1
    if pidof $1 > /dev/null; then
        fLog "...$1 was successfully started."
    else
        fLog "ERROR! $1 start failed!"
    fi
}







# CHECKING THE EXISTENCE OF THE BINARY/EXEC FILE

if [ ! -f "$softcam_dir/$softcam_exec" ]; then
    fLog "ERROR! Executable binary file '$softcam_dir/$softcam_exec' does not exist!"
    exit 1
fi



# CALLING A FUNCTION BY INPUT ARGUMENTS ************************************

case "$1" in
    stop)
        fLog "$hrline"
        fStop "$softcam_exec"
        ;;
    start|restart|reload|force-reload)
        fLog "$hrline"
        fStopAndStart "$softcam_exec"
        ;;
    *)
        fLog "$hrline"
        fLog "UNKNOWN OR MISSING PARAMETER !"
        echo "$helptext" >$(tty)
        exit 1
        ;;
esac



exit 0
