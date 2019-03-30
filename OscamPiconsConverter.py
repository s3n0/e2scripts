#!/usr/bin/env python

from PIL import Image
from io import BytesIO
import base64

from os import path as os_path
import glob
import re

#############################################################################
# PNG to TPL picons converter (TPL picons for Oscam Webif)
#############################################################################
# EXAMPLE OF USE:  python /tmp/OscamPiconsConverter.py
#############################################################################
# USER CONFIG:
#############################################################################
OSCAM_SRVID = '/etc/tuxbox/config/oscam/oscam.srvid'
DIR_TPL     = '/etc/tuxbox/config/oscam/piconTPL'
DIR_PNG     = '/usr/share/enigma2/picon'
CAIDS_INCLUDED = ['0D96','0624']
#CAIDS_INCLUDED = []    # empty list = all found CAIDs will be included
#############################################################################

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

def do_table_from_srvid(caidfilter):
    print('Making a table...')
    with open(OSCAM_SRVID, 'r') as f:
        data = re.findall(r'([0-9a-fA-F\,\:]+)\|.*', f.read()  )         # ['0D02,1815,0D97,0653:760d', '0D02,1815,0D97,0653:7669', '0D02,1815,0D97,0653:766a', '0D02,1815,0D97,0653:0000', ....... ]
    d = {}
    for entry in data:
        caids, sid = entry.upper().split(':')
        filtered = list( set(caids.split(','))  &  set(caidfilter)  )
        if filtered:
            d[sid] = filtered
    print('...done.')
    return d
    # { '1807': ['0D03', '0D70', '0D96', '0624'], '00CD': ['0B00', '09AF'], '00CA': ['1833', '1834', '1702', '1722', '09C4', '09AF'], '00CB': ['0B00', '09AF'], ..... }

#### this is a experimental function only :-)
"""
def do_table_from_png_N_lamedb(caidfilter):
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
"""

if __name__ == "__main__" and check_folders():
    if CAIDS_INCLUDED:
        clist = [ s.rjust(4,'0') for s in CAIDS_INCLUDED ]
        print('Your selected CAIDs: %s' % clist)
    else:
        clist = []
        print('Your selected CAIDs: <empty> (all found CAIDs will be included)')
    table = do_table_from_srvid(clist)
    png2tpl(table)
    print('Good Bye')
