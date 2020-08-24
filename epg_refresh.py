#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################
# EPG Refresh
# by s3n0, 2019-08-24
###############################################
# - simple python-script for Enigma2 based set-top-box, for refresh EPG data on all DVB channels
# - the script will find all the necessary transponders what you need to zapping
# - transponders are selected from the userbouquet and zap only once
###############################################
# - be sure to set the file attributes (chmod 755 /usr/script/epg_refresh.py)
# - the best way to use EPG refresh is to add a new task to the CRON scheduler
# - for example, to run the python script every 2nd day, at 03:00, as the background process, use the following crontab line:
#       00 03 */2 * *      /usr/bin/python /usr/script/epg_refresh.py &
###############################################

#### change the path to your own userbouquet file(s) containing the satellite channels for which you want to refresh EPG data :
BOUQUET_FILES = ['userbouquet.sat-skylink-sk-komplet-vcetne-cz.tv']

#### if you need more than one userbouquet, use the following syntax :
#BOUQUET_FILES = ['userbouquet.skylink.tv', 'userbouquet.freesat.tv', 'userbouquet.orange.tv']

from datetime import datetime
from time import sleep
from urllib2 import urlopen

###############################################

def writeLOG(msg):
    print(msg)    
    with open('/tmp/epg_refresh.log', 'a') as f:
        f.write(msg + '\n')

def zapChannel(channel = '0:0:0:0:0:0:0:0:0:0:'):       # zap channel (using the Enigma2 Open-Webif)
    response = urlopen('http://127.0.0.1/web/zap?sRef=' + channel)
    web_content = response.read()

def enigmaInStandby():                      # checking standby mode (using the Enigma2 Open-Webif)
    response = urlopen('http://127.0.0.1/web/powerstate')
    web_content = response.read()
    if 'true' in web_content.lower():
        return True
    else:
        writeLOG("Enigma2 is not in standby mode. The 'epg_refresh.py' script will not be executed.")
        return False

def saveEPG():                              # save EPG cache to disk - as the file "epg.dat" (using the Enigma2 Open-Webif)
    response = urlopen('http://127.0.0.1/web/saveepg')
    web_content = response.read()

###############################################
###############################################

if __name__ == "__main__" and enigmaInStandby():
    
    writeLOG('%s %s' % ( datetime.now().strftime("%Y-%m-%d %H:%M:%S") ,  '=' * 50 )  )
    
    bouquet_SRC = []
    for fname in BOUQUET_FILES:
        with open('/etc/enigma2/' + fname, 'r') as f:
            bouquet_data = f.read().upper().split('\n')
            # remove all lines startswith '#NAME', '#SERVICE 1:64', '#DESCRIPTION'
            # and return the values from index 9 to right i.e. without the prefix '#SERVICE ' and also without the URL link (http: ..... string) if does it exist
            refs = [ ':'.join(s[9:].split(':')[0:10]) + ':' for s in bouquet_data if not (s.startswith('#NAME') or s.startswith('#SERVICE 1:64') or s.startswith('#DESCR'))  ]
            bouquet_SRC += refs[:-1]       # the last entry ':' in the list variable must to be removed (created in the for-loop before)
    
    with open('/etc/enigma2/blacklist', 'r') as f:
        blacklist_data = f.read().upper().split('\n')
        blacklist_SRC = [ ':'.join(k.split(':')[0:10]) + ':' for k in blacklist_data ][:-1]     # remove all http:// and other unwanted text from the end of lines
    
    tuned_SRC = []
    for SRC in bouquet_SRC:
        # --- bouquet format for ServRefCode = service_type : 0 : service_quality : ServiceID : TransponderID : NetworkID : Namespace : 0 : 0 : 0 :
        # --- index of the ServRefCode =              0       1          2              3             4             5            6      7   8   9    ...
        # --- real example = '1:0:16:3725:C8E:3:EB0000:0:0:0:'
        fields = SRC.split(':')
        if not [ s for k in tuned_SRC if fields[4] +':'+ fields[5] in k ]:   # if *:TransponderID:NetworkID:* is already included in the tuned_SRC list, then continue to search of another value
            if not SRC in blacklist_SRC:
                tuned_SRC.append(SRC)
    
    writeLOG('Number of channels/transponders to tune: %s' % len(tuned_SRC))
    writeLOG('Zapping the neccessary channels/transponders...')
    
    for i, SRC in enumerate(tuned_SRC, 1):
        zapChannel(SRC)
        writeLOG('{:03d} / {:03d} - {}'.format(i, len(tuned_SRC), SRC))
        sleep(20)           # waiting 20 sec. for receiving and retrieving all EPG data from the stream (from the currently tuned transponder)
    
    writeLOG('...done.')
    zapChannel()            # shut down the tuner / stop watching DVB channel
    saveEPG()               # save EPG cache to disk, if we need to upload the file "epg.dat" to another set-top box or to some server on the internet
 
