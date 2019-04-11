#!/usr/bin/env python

#################################
###       s3n0 - 2019         ###
###  .PNG to .TPL converter   ###
###  https://github.com/s3n0  ###
#################################

#############################################################################
# simple script to finding and converting PNG to TPL picons (for Oscam Webif)
#############################################################################
# EXAMPLE OF USE:
# - upload the script into the set-top-box, for example into the '/tmp' folder
# - then start the script via command-line Shell:
# python /tmp/OscamPiconsConverter.py [OPTIONS] PNG_directory TPL_directory
#############################################################################

from PIL import Image
from io import BytesIO
import base64

from sys import argv as sys_argv
from os import path as os_path
import glob
import re

global CAIDS_FILTER, DIR_TPL, DIR_PNG, DIR_OSCAMCFG

#############################################################################

def table_from_srvid(caidsFilter = []):
    global CAIDS_FILTER, DIR_TPL, DIR_PNG, DIR_OSCAMCFG
    print('Making a table from .srvid file...')
    with open(DIR_OSCAMCFG + '/oscam.srvid','r') as f:
        data = re.findall(r'([0-9a-fA-F\,\:]+)\|.*', f.read()  )         # [ '0D02,1815,0D97,0653:760d' , '0D02,1815,0D97,0653:7669' , '0D02,1815,0D97,0653:766a' , '0D02,1815,0D97,0653:0000' ,  ...... ]
    d = {}
    for line in data:
        caids, sid = line.upper().split(':')                             # split the whole part via ":" character
        caidsToAdd = list(set(caids.split(',')))
        if caidsFilter:
            caidsToAdd = list( set(caidsToAdd)  &  set(caidsFilter)  )   # checking CAIDs by user defined CAIDS_FILTER
        if caidsToAdd:
            #d.setdefault(sid, []).append(caidsToAdd)
            if sid in d.keys():
                d[sid] = d[sid] + caidsToAdd
            else:
                d[sid] = caidsToAdd
    for key, values in d.iteritems():
        d[key] = list(set(values))                      # remove duplicated caids in dictionary variables (browsing through all dict.values for each one dict.key)
    print('...done.')
    return d             # { '1807': ['0D03', '0D70', '0D96', '0624'],  '00CD': ['0B00', '09AF'],  '00CA': ['1833', '1834', '1702', '1722', '09C4', '09AF'],  '00CB': ['0B00', '09AF'], ..... }

def table_from_srvid2(caidsFilter = []):
    global CAIDS_FILTER, DIR_TPL, DIR_PNG, DIR_OSCAMCFG
    print('Making a table from .srvid2 file...')
    with open(DIR_OSCAMCFG + '/oscam.srvid2','r') as f:
        data = f.read().splitlines()
    d = {}
    for line in data:
        if line.startswith('#') or line == '':
            continue
        sid, caids = line.upper().split('|')[0].split(':')               # remove all chars from "|" to the end of line, and split the whole part via ":" character
        caids = re.sub('@[0-9a-fA-F]+', '', caids)                       # remove all strings such as "@0000A1CF" from the line
        caidsToAdd = list(set(caids.split(',')))
        if caidsFilter:    
            caidsToAdd = list( set(caidsToAdd)  &  set(caidsFilter)  )   # checking CAIDs by user defined CAIDS_FILTER
        if caidsToAdd:
            #d.setdefault(sid, []).append(caidsToAdd)
            if sid in d.keys():
                d[sid] = d[sid] + caidsToAdd
            else:
                d[sid] = caidsToAdd
    for key, values in d.iteritems():
        d[key] = list(set(values))                      # remove duplicated caids in dictionary variables (browsing through all dict.values for each one dict.key)
    print('...done.')
    return d             # { '1807': ['0D03', '0D70', '0D96', '0624'], '00CD': ['0B00', '09AF'], '00CA': ['1833', '1834', '1702', '1722', '09C4', '09AF'], '00CB': ['0B00', '09AF'], ..... }

def table_from_png_only(caidsFilter = []):
    """
    To make the TPL picons from PNG files for only certain CAIDs (in the user configured value = CAIDS_FILTER)
    """
    global CAIDS_FILTER, DIR_TPL, DIR_PNG, DIR_OSCAMCFG
    print('Making a table from all PNG files...')
    d = {}
    dir_list = glob.glob(DIR_PNG + '/*.png')
    for path_to_png in dir_list:
        sref   = path_to_png.split('/')[-1].split('.')[0].upper().split('_')
        sid    = sref[3].rjust(4,'0')
        d[sid] = caidsFilter
    print('...done.')
    return d

def table_from_png_and_lamedb(caidsFilter = []):
    """
    This function is experimental only, it's for a testing purpose only
    To make the TPL picons from PNG files for user selected CAIDs + filtered with the 'lamedb' database file
    """
    global CAIDS_FILTER, DIR_TPL, DIR_PNG, DIR_OSCAMCFG
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
            caids = list(set(  lamedb[idx+2].replace('C:','').split(',')[1:]  )   &   set(caidsFilter)  )
            if caids:
                d[sid] = caids
    return d

#############################################################################

def png2tpl(sid_table):
    global CAIDS_FILTER, DIR_TPL, DIR_PNG, DIR_OSCAMCFG
    print('Converting PNG to TPL images (Base64/template format)...')
    dir_list = glob.glob(DIR_PNG + '/*.png')
    for path_to_png in dir_list:
        sid = path_to_png.split('/')[-1].split('_')[3].rjust(4,'0').upper()
        if sid in sid_table:
            for caid in sid_table[sid]:
                img = Image.open(path_to_png)
                if '-q' in sys_argv:
                    img = img.resize( (100,60), Image.ANTIALIAS )
                else:
                    img.thumbnail((100,60))
                buffer = BytesIO()
                img.save(buffer, format='PNG')       # img.save('/tmp/temp.png', format='PNG')
                data_bin = buffer.getvalue()
                data_string = 'data:image/png;base64,' + base64.b64encode(data_bin)
                with open('{0}/IC_{1}_{2}.tpl'.format(DIR_TPL, caid, sid),'w') as f:
                    f.write(data_string)
    print('...done.')

#############################################################################

def table_size_checking(tbl):
    dict_length = sum( [len(x) for x in tbl.values()] )
    print('Total picons and CAIDs found: %s' % dict_length)    
    if dict_length > 2000:
        while True:
            answer = raw_input('Warning !\nTotal number of all SrvIDs is too high !\nA lot of TPL-picons will be created !\nDo you really want to continue ?\n(y/n)\n>')
            if answer.lower() == 'y':
                return True
            elif answer.lower() == 'n':
                return False
    return True

def show_man_page():
    print('''
USAGE:
    python {0} [OPTIONS] PNG_FOLDER TPL_FOLDER

OPTIONS:
    -i \t\t\t make TPL picons from all images, the -1 and -2 argument are ignored, but the -c argument must be specified !
    -c CAID[,CAID,...] \t user-selected CAIDs (which are the only ones to be considered), if the argument -c is not used, all found CAIDs will be used
    -1 \t\t\t make TPL picons by '.srvid' file
    -2 \t\t\t make TPL picons by '.srvid2' file (created by Oscam, the file may contains a FFA channels with CAID = FFFE)
    -o PATH \t\t oscam.srvid file directory if the script did not find the Oscam folder
    -q \t\t\t higher quality image processing with antialiasing filter (higher quality means a bit larger file size), the default is "thumbnail" quality

EXAMPLES:
    python {0} -i -c 0624 /tmp/png_images /etc/tuxbox/config/oscam/piconTPL
    python {0} -2 -c 0624,0D96,FFFE /usr/share/enigma2/picon /etc/tuxbox/config/oscam/piconTPL
    python {0} -1 -2 /tmp/png_images /etc/tuxbox/config/oscam/piconTPL
    python {0} -o /media/hdd/oscam -1 /media/hdd/picon /media/hdd/piconTPL

RECOMMENDED:
    python {0} -1 -2 -c <your_caids_included_the_FFFE_caid> /usr/share/enigma2/picon /etc/tuxbox/config/oscam/piconTPL
    '''.format(sys_argv[0])  )

def prepare_arguments():    
    global CAIDS_FILTER, DIR_TPL, DIR_PNG, DIR_OSCAMCFG
    
    if len(sys_argv) <= 2 or ('-i' in sys_argv and '-c' not in sys_argv):
        show_man_page()
        return False
    
    if '-i' not in sys_argv:
        if '-o' in sys_argv:
            DIR_OSCAMCFG = sys_argv[ sys_argv.index('-o') + 1 ]
        else:
            folder_list = ['/etc/tuxbox/config/oscam', '/etc/tuxbox/config', '/etc/tuxbox/oscam', '/usr/keys/oscam', '/usr/local/etc', '']
            DIR_OSCAMCFG = [x for x in folder_list if os_path.isfile(x + '/oscam.server')][0]
            if DIR_OSCAMCFG == '':
                show_man_page()
                print('ERROR ! The Oscam configration folder was not found ! Please use the "-o" argument.')
                return False
        if '-1' in sys_argv and not os_path.isfile(DIR_OSCAMCFG + '/oscam.srvid'):
            print('ERROR ! The oscam.srvid file does not exist !')
        if '-2' in sys_argv and not os_path.isfile(DIR_OSCAMCFG + '/oscam.srvid2'):
            print('ERROR ! The oscam.srvid2 file does not exist !')
    
    if '-c' in sys_argv:
        clist = sys_argv[ sys_argv.index('-c') + 1 ].upper().split(',')
        CAIDS_FILTER = [s.rjust(4, '0') for s in clist]
        print('User-selected CAIDs that will be considered: %s' % ', '.join(CAIDS_FILTER) )
    else:
        CAIDS_FILTER = []
        print('User-selected CAIDs: <blank/empty>  (all found CAIDs will be included)')
    
    DIR_TPL = sys_argv[-1]
    DIR_PNG = sys_argv[-2]
    if not (os_path.isdir(DIR_TPL) and os_path.isdir(DIR_PNG)):
        print('ERROR ! TPL or PNG directory does not exist !')
        return False
    
    return True

#############################################################################

if __name__ == "__main__" and prepare_arguments():
        global CAIDS_FILTER, DIR_TPL, DIR_PNG, DIR_OSCAMCFG
        
        if '-1' in sys_argv and '-i' not in sys_argv:
            table = table_from_srvid(CAIDS_FILTER)
            if table_size_checking(table):
                png2tpl(table)
        
        if '-2' in sys_argv and '-i' not in sys_argv:
            table = table_from_srvid2(CAIDS_FILTER)
            if table_size_checking(table):
                png2tpl(table)
        
        if '-i' in sys_argv:
            table = table_from_png_only(CAIDS_FILTER)
            if table_size_checking(table):
                png2tpl(table)
        
        print('Good bye')


