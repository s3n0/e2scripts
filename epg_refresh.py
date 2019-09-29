#!/usr/bin/env python
# -*- coding: utf-8 -*-

#### change the path to your own userbouquet file(s) containing the satellite channels for which you want to refresh EPG data :
BOUQUET_FILES = ['userbouquet.sat-skylink-sk-komplet-vcetne-cz.tv']
#### if you need more than one userbouquet, use the following syntax :
#BOUQUET_FILES = ['userbouquet.skylink.tv', 'userbouquet.freesat.tv', 'userbouquet.orange.tv']

###############################################
# EPG Refresh
# by s3n0, 2019-08-24
###############################################
# - simple python-script for Enigma2 based set-top-box, for refresh EPG data on all channels
# - the script will find all the necessary transponders what you need to zapping
# - transponders are selected from the userbouquet and zap only once
###############################################
# - be sure to set the file attributes (chmod 755 /usr/script/epg_refresh.py)
# - the best way to use EPG refresh is to add a new task to the CRON scheduler
# - for example, to run the python script every 5th day at 03:00, use the following crontab line:
#   0 3 */5 * *     python /usr/script/epg_refresh.py > /dev/null 2>&1
###############################################

from time import sleep
from urllib2 import urlopen

###############################################

def zapChannel(channel = '""'):               # zap channel using the OpenWebif
    if channel == ' ' or channel == '':
        channel = '""'
    response = urlopen('http://127.0.0.1/web/zap?sRef=' + channel)
    web_content = response.read()

def enigmaInStandby():
    response = urlopen('http://127.0.0.1/web/powerstate')
    web_content = response.read()
    if 'true' in web_content.lower():
        return True
    else:
        print("Enigma2 is not in standby mode. The 'epg_refresh.py' script will not be executed.")
        return False

###############################################
###############################################

if __name__ == "__main__" and enigmaInStandby():
    
    bouquet_src = []
    for fname in BOUQUET_FILES:
        with open('/etc/enigma2/' + fname, 'r') as f:
            bouquet_data = f.read().upper().split('\n')
            # remove all lines startswith '#NAME', '#SERVICE 1:64', '#DESCRIPTION'
            # and return the values from index 9 to right i.e. without the prefix '#SERVICE ' and also without the URL link (http: ..... string) if does it exist
            refs = [ ':'.join(s[9:].split(':')[0:10]) + ':' for s in bouquet_data if not (s.startswith('#NAME') or s.startswith('#SERVICE 1:64') or s.startswith('#DESCR'))  ]
            bouquet_src += refs[:-1]       # the last entry ':' in the list variable must to be removed (created in the for-loop before)
    
    with open('/etc/enigma2/blacklist', 'r') as f:
        blacklist_data = f.read().upper().split('\n')    
        blacklist_src = [ ':'.join(k.split(':')[0:10]) + ':' for k in blacklist_data ][0]        # remove all http:// and other unwanted text from the end of lines
    
    tuned_src = []
    for src in bouquet_src:
        # --- bouquet format for ServRefCode = service_type : 0 : service_quality : ServiceID : TransponderID : NetworkID : Namespace : 0 : 0 : 0 :
        # --- index of the ServRefCode =              0       1          2              3             4             5            6      7   8   9    ...
        # --- real example = '1:0:16:3725:C8E:3:EB0000:0:0:0:'
        field = src.split(':')
        if not [ s for k in tuned_src if field[4] + ':' + field[5] in k ]:
            if not src in blacklist_src:
                tuned_src.append(src)
    
    print('Number of channels/transponders to tune: %s' % len(tuned_src))
    print('Zapping the neccessary channels/transponders...')
    
    for i, srefcode in enumerate(tuned_src, 1):
        zapChannel(srefcode)
        print('{:03d} / {:03d} - {}'.format(i, len(tuned_src), srefcode))
        sleep(20)       # waiting 20 sec. for receiving and retrieving all EPG data from the stream (from the currently tuned transponder)
    
    print('...done.')
    zapChannel('')


