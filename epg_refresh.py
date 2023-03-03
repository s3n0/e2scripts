#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################
# EPG Refresh - python script for Enigma2
# written by s3n0, 2019-2023
###############################################
# - simple python-script for Enigma2 based set-top-box, for refresh EPG data
# - the script will find the necessary transponders depending on the available channels in the userbouquet files
# - then the script gradually zaps these transponders (only some channels), to read EPG data from DVB stream
###############################################
# - be sure to set the file attributes (chmod 755 /usr/script/epg_refresh.py)
# - the best way to use EPG refresh is to add a new task to the CRON scheduler
# - for example, to run the python script every 2nd day, at 03:00, as the background process, use the following crontab line:
#       00 03 */2 * *      /usr/bin/python /usr/script/epg_refresh.py > /dev/null 2>&1
###############################################

#### change the path to your own userbouquet file(s), containing the satellite channels, for which you want to refresh EPG data :
#BOUQUET_FILES = ['userbouquet.sat-skylink-sk-komplet-vcetne-cz.tv']
BOUQUET_FILES = ['userbouquet.sat-skylink-sk-komplet-vcetne-cz.tv', 'userbouquet.sat-skylink-vhannibal.tv']
#BOUQUET_FILES = ['userbouquet.skylink.tv', 'userbouquet.freesat.tv', 'userbouquet.orange.tv']

LOG_FILE_PATH = '/tmp/epg_refresh.log'      # epg_refresh log (path to directory + file name)

DELAY_TIME = 15                             # waiting time after zapping each channel (transponder)

###############################################

from datetime import datetime
from time import sleep
from os.path import getsize as os_path_getsize

from sys import version_info as py_version
if py_version.major == 3:           # data of this object type:   sys.version_info(major=3, minor=8, micro=5, releaselevel='final', serial=0)
    import urllib.request as urllib2
else:
    import urllib2

###############################################

def writeLOG(msg):
    print(msg)
    with open(LOG_FILE_PATH, 'a') as f:
        f.write('[ %s ] %s\n' % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))
    if os_path_getsize(LOG_FILE_PATH) > 255000:     # [Bytes] - maximum allowed file size
        with open(LOG_FILE_PATH, 'r') as f:
            cache = f.readlines()
        with open(LOG_FILE_PATH, 'w') as f:
            f.writelines( cache[ len(cache)/2 : ] )

def zapChannel(src='0:0:0:0:0:0:0:0:0:0:'):     # zap channel (using the Enigma2 Open-Webif)
    response = urllib2.urlopen('http://127.0.0.1/web/zap?sRef=' + src)
    web_content = response.read()
    if isinstance(web_content, bytes):
        web_content = web_content.decode()

def enigmaInStandby():                      # checking standby mode (using the Enigma2 Open-Webif)
    response = urllib2.urlopen('http://127.0.0.1/web/powerstate')
    web_content = response.read()
    if isinstance(web_content, bytes):
        web_content = web_content.decode()
    if 'true' in web_content.lower():
        return True
    else:
        writeLOG("Enigma2 is not switched to standby mode. The script 'epg_refresh.py' will be canceled.")
        return False

def saveEPG():                              # save EPG cache to disk - as the file "epg.dat" (using the Enigma2 Open-Webif)
    response = urllib2.urlopen('http://127.0.0.1/web/saveepg')
    web_content = response.read()
    if isinstance(web_content, bytes):
        web_content = web_content.decode()
    if 'true' in web_content.lower():
        writeLOG("...saving the EPG file to disk was successful")
    else:
        writeLOG("...ERROR ! saving the EPG file to disk failed !")

def findChannelName(src='0:0:0:0:0:0:0:0:0:0:'):
    # index...................       0       1         2          3     4     5        6       7 8 9
    # userbouquet SRC  =======  ServSource : 0 : ServType[hex] : SID : TID : NID : NameSpace : 0:0:0:    ==>   example for Markiza channel (2022-May) = 1:0:19:3731:C8E:3:EB0000:0:0:0:
    ch_name = "UNKNOWN!"
    src = src.split(":")
    # lameDB stream data   ===     SID          :     NameSpace       :         TID         :        NID          :   ServType[dec]
    match = ":".join((      src[3].rjust(4,"0") , src[6].rjust(8,"0") , src[4].rjust(4,"0") , src[5].rjust(4,"0") , str(int(src[2],16))    )).upper()
    for i, line in enumerate(LAME_DB, 0):
        if line.upper().startswith(match):
            ch_name = LAME_DB[ i + 1 ]
            break
    return ch_name

###############################################
###############################################

writeLOG(' ')
writeLOG('==== BEGINNING OF THE SCRIPT ' + '=' * 44)

if __name__ == "__main__" and enigmaInStandby():
    
    with open('/etc/enigma2/lamedb', 'r') as f:
        LAME_DB = f.read().split('services')[2].splitlines()
    
    bouquet_SRC = []
    for fname in BOUQUET_FILES:
        with open('/etc/enigma2/' + fname, 'r') as f:
            bouquet_data = f.read().upper().split('\n')
        # remove all lines startswith '#NAME', '#SERVICE 1:64', '#DESCRIPTION'
        # and take the values from index 9 to right side, i.e. lines without the prefix '#SERVICE ' and also without the URL link (http: ..... string) if does it exist
        refs = [':'.join(s[9:].split(':')[0:10]) + ':' for s in bouquet_data if not (s.startswith('#NAME') or s.startswith('#SERVICE 1:64') or s.startswith('#DESCR'))]
        bouquet_SRC += refs[:-1]       # the last entry ':' in the list variable must to be removed (created in the for-loop before)
    
    with open('/etc/enigma2/blacklist', 'r') as f:
        blacklist_data = f.read().upper().split('\n')
        blacklist_SRC = [':'.join(k.split(':')[0:10]) + ':' for k in blacklist_data][:-1]     # remove all http:// and other unwanted text from the end of lines
    
    needs_SRC = []
    for SRC in bouquet_SRC:
        # --- bouquet format for ServRefCode = service_type : 0 : service_quality : ServiceID : TransponderID : NetworkID : Namespace : 0 : 0 : 0 :
        # --- index of the ServRefCode (fields) =     0       1          2              3             4             5            6      7   8   9
        # --- real example of the SRC variable  =  '1:0:16:3725:C8E:3:EB0000:0:0:0:'
        fields = SRC.split(':')
        if ':%s:%s:%s:' % tuple(fields[4:7]) not in ''.join(needs_SRC):     # if *:TransponderID:NetworkID:NameSpace:* is not in the needs_SRC list, then add the item to needs_SRC list
            if SRC not in blacklist_SRC:
                needs_SRC.append(SRC)
    
    writeLOG('Number of transponders to tune: %s' % len(needs_SRC))
    writeLOG('Zapping the neccessary transponders...')
    
    i = 0
    imax = len(needs_SRC)
    
    while enigmaInStandby() and i < imax:
        zapChannel(needs_SRC[i])    # if enigma2 is still in standby, the tuner switches to the next DVB channel
        writeLOG('{:03d} / {:03d} | {} | {}'.format(i + 1, imax, needs_SRC[i], findChannelName(needs_SRC[i])))
        sleep(DELAY_TIME)   # waiting a few of seconds - for receiving and retrieving all EPG data from the stream (from the currently tuned transponder)
        i += 1
    
    if i == imax:           # if enigma2 was not interrupted from standby, the script will be completed and the DVB tuner will be turned off
        zapChannel()        # shut down the tuner / stop watching DVB channel
        saveEPG()           # save EPG cache to disk, if we need to upload the file "epg.dat" to another set-top box or to some server on the internet
    
    writeLOG('...done.')

writeLOG('==== END OF THE SCRIPT ' + '=' * 50)
