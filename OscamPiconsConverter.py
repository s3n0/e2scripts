#!/usr/bin/env python

#################################
###       s3n0 - 2019         ###
###  .PNG to .TPL converter   ###
###  https://github.com/s3n0  ###
#################################

#############################################################################
# simple script to finding and converting PNG to TPL picons (for Oscam Webif)
#############################################################################
# EXAMPLE OF USE:   python /tmp/OscamPiconsConverter.py
#############################################################################
# USER CONFIGURATION:
#############################################################################
OSCAM_SRVID  = '/etc/tuxbox/config/oscam/oscam.srvid2'
DIR_TPL      = '/etc/tuxbox/config/oscam/piconTPL'
DIR_PNG      = '/usr/share/enigma2/picon'
CAIDS_FILTER = ['0D96', '0624']
#CAIDS_FILTER = []         # blank variable (empty list) means that all found CAIDs will be included for new TPL picons - don't recommend !
#############################################################################

from PIL import Image
from io import BytesIO
import base64

from os import path as os_path
import glob
import re


def check_folders():
    print("Verifying all neccessary folders:\n{0}\n{1}\n{2}".format(OSCAM_SRVID, DIR_TPL, DIR_PNG))
    if not (os_path.isfile(OSCAM_SRVID) and os_path.isdir(DIR_TPL) and os_path.isdir(DIR_PNG)):
        print("...WARNING - some directories does not exists !!!")
        return False
    else:
        print("...all done.")
        return True


def png2tpl(sid_table):
    print('Converting PNG picons to TPL files (Base64/template format)...')
    dir_list = glob.glob(DIR_PNG + '/*.png')
    for path_to_png in dir_list:
        sid = path_to_png.split('/')[-1].split('_')[3].rjust(4,'0').upper()
        if sid in sid_table:
            for caid in sid_table[sid]:
                img = Image.open(path_to_png)
                #im.thumbnail((100,60))
                img = img.resize( (100,60), Image.ANTIALIAS )
                output = BytesIO()
                img.save(output, format='PNG')         # im.save('/tmp/temp.png', format='PNG')
                img_data = output.getvalue()
                img_data_b64 = 'data:image/png;base64,' + base64.b64encode(img_data)
                with open('{0}/IC_{1}_{2}.tpl'.format(DIR_TPL,caid,sid), 'w') as f:
                    f.write(img_data_b64)
    print('...done.')


def table_from_srvid(caidfilter = []):
    print('Making a table from .srvid file...')
    with open(OSCAM_SRVID, 'r') as f:
        data = re.findall(r'([0-9a-fA-F\,\:]+)\|.*', f.read()  )         # [ '0D02,1815,0D97,0653:760d' , '0D02,1815,0D97,0653:7669' , '0D02,1815,0D97,0653:766a' , '0D02,1815,0D97,0653:0000' ,  ...... ]
    d = {}
    for line in data:
        caids, sid = line.upper().split(':')                             # split the whole part via ":" character
        caidsAdd = list( set(caids.split(','))  &  set(caidfilter)  )    # checking CAIDs by user defined CAIDS_FILTER
        if caidsAdd:
            #d.setdefault(sid, []).append(caidsAdd)
            if sid in d.keys():
                d[sid] = d[sid] + caidsAdd
            else:
                d[sid] = caidsAdd
    for key, values in d.iteritems():
        d[key] = list(set(values))                      # remove duplicated caids in dictionary variables (browsing through all dict.values for each one dict.key)
    print('...done.')
    return d             # { '1807': ['0D03', '0D70', '0D96', '0624'], '00CD': ['0B00', '09AF'], '00CA': ['1833', '1834', '1702', '1722', '09C4', '09AF'], '00CB': ['0B00', '09AF'], ..... }

def table_from_srvid2(caidfilter = []):
    print('Making a table from .srvid2 file...')
    d = {}
    with open(OSCAM_SRVID, 'r') as f:
        data = f.read().splitlines()
    for line in data:
        if line.startswith('#') or line == '':
            continue
        sid, caids = line.upper().split('|')[0].split(':')               # remove all chars from "|" to the end of line, and split the whole part via ":" character
        ctemp = re.sub('@[0-9a-fA-F]+', '', caids)                       # remove all strings such as "@0000A1CF" from the line
        caidsAdd = list( set(ctemp.split(','))  &  set(caidfilter)  )    # checking CAIDs by user defined CAIDS_FILTER
        if caidsAdd:
            #d.setdefault(sid, []).append(caidsAdd)
            if sid in d.keys():
                d[sid] = d[sid] + caidsAdd
            else:
                d[sid] = caidsAdd
    for key, values in d.iteritems():
        d[key] = list(set(values))                      # remove duplicated caids in dictionary variables (browsing through all dict.values for each one dict.key)
    print('...done.')
    return d             # { '1807': ['0D03', '0D70', '0D96', '0624'], '00CD': ['0B00', '09AF'], '00CA': ['1833', '1834', '1702', '1722', '09C4', '09AF'], '00CB': ['0B00', '09AF'], ..... }


def table_from_png_and_lamedb(caidfilter):
"""
This function is experimental for now
It's for a testing purpose only
"""
    with open('/etc/enigma2/lamedb', 'r') as f:
        lamedb = f.read().upper().splitlines()
    d = {}
    dir_list = glob.glob(DIR_PNG + '/*.png')
    for path_to_png in dir_list:
        sref  = path_to_png.split('/')[-1].split('.')[0].upper().split('_')
        sid   = sref[3].rjust(4,'0')
        match = ':'.join((sid, sref[6].rjust(8,'0'), sref[4].rjust(4,'0'), sref[5].rjust(4,'0'), str(int(sref[2],16)), '0', '0'))
        idx   = [ i for i,e in enumerate(lamedb) if match in e ]
        if idx:
            idx = idx[0]
            caids = list(set(  lamedb[idx+2].replace('C:','').split(',')[1:]  )   &   set(caidfilter)  )
            if caids:
                d[sid] = caids
    return d



if __name__ == "__main__" and check_folders():
    
    if CAIDS_FILTER == []:
        clist = []
        print('User-selected CAIDs: <blank/empty>  (all found CAIDs will be included)')
    else:
        clist = [ s.upper().rjust(4,'0') for s in CAIDS_FILTER ]
        print('User-selected CAIDs that will be considered: %s' % clist)
    
    if OSCAM_SRVID.endswith('.srvid'):
        table = table_from_srvid(clist)
    elif OSCAM_SRVID.endswith('.srvid2'):
        table = table_from_srvid2(clist)
    else:
        print('...error - the file "%s" must be format srvid or srvid2.' % OSCAM_SRVID)
    
    png2tpl(table)
    
    print('Good Bye')


