#!/usr/bin/env python
# -*- coding: utf-8 -*-

#### change the path to your own userbouquet file(s) containing the satellite channels for which you want to refresh EPG data :
BOUQUET_FILES = ['userbouquet.sat-skylink-only.tv']
#### if you need more than one userbouquet, use the following syntax :
#BOUQUET_FILES = ['userbouquet.skylink.tv', 'userbouquet.free-sat.tv', 'userbouquet.orange.tv']

###############################################
# EPG Refresh
# Python script
# developed for linux set-top-box / Enigma2
# by s3n0, 2019-08-24
###############################################

import time, urllib2

###############################################

def zapChannel(channel = '""'):               # zap channel using the OpenWebif
    if channel == ' ' or channel == '':
        channel = '""'
    response = urllib2.urlopen('http://127.0.0.1/web/zap?sRef=' + channel)
    web_content = response.read()

###############################################
###############################################

if __name__ == "__main__":
    
    bouquet_src = []
    for fname in BOUQUET_FILES:
        with open(fname, 'r') as f:
            bouquet_data = f.read().upper().split('\n')
            # remove all lines startswith '#NAME', '#SERVICE 1:64', '#DESCRIPTION'
            # and return the values from index 9 to right i.e. without the prefix '#SERVICE ' and also without the URL link (http: ..... string) if does it exist
            refs = [ ':'.join(s[9:].split(':')[0:10]) + ':' for s in bouquet_data if not (s.startswith('#NAME') or s.startswith('#SERVICE 1:64') or s.startswith('#DESCR'))  ]
            bouquet_src += refs[:-1]            # ':' as the last entry in list must to be removed (created in the loop before)
    
    with open('/etc/enigma2/blacklist', 'r') as f:
        blacklist_data = f.read().upper().split('\n')    
        blacklist_src = [ ':'.join(k.split(':')[0:10]) + ':' for k in blacklist_data ][0]        # remove all http:// and other unwanted text from the end of lines
    
    to_tune = []
    for src in bouquet_src:
        # --- bouquet format for ServRefCode = service_type : 0 : service_quality : ServiceID : TransponderID : NetworkID : Namespace : 0 : 0 : 0 :
        # --- index of the ServRefCode =              0       1          2              3             4             5            6      7   8   9    ...
        # --- real example = '1:0:16:3725:C8E:3:EB0000:0:0:0:'
        field = src.split(':')
        if not [ s for k in to_tune if field[4] + ':' + field[5] in k ]:
            if not src in blacklist_src:
                to_tune.append(src)
    
    print('Number of channels to tune: %s' % len(to_tune))
    print('Zapping the neccessary channels...')
    
    for i, srefcode in enumerate(to_tune):
        zapChannel(srefcode)
        print('{:03d} / {:03d} - {}'.format(i, len(to_tune), srefcode))
        time.sleep(20)
    
    print('...done.')
    zapChannel('')


