#!/usr/bin/env python

#################################
###       s3n0 - 2019         ###
###  .PNG to .TPL converter   ###
###  https://github.com/s3n0  ###
#################################

#############################################################################
# simple python script for converting PNG to TPL picons (for Oscam-Webif)
#############################################################################
# USAGE:
# - upload the script into the set-top-box, for example into the '/tmp' folder
#   or download the script directly via the Shell:
# wget -O /tmp/OscamPiconsConverter.py --no-check-certificate https://github.com/s3n0/e2scripts/raw/master/OscamPiconsConverter.py
# - then start the script via command-line Shell:
# python /tmp/OscamPiconsConverter.py OPTIONS PNG-directory TPL-directory
# - start the script without arguments for show the man-page:
# python /tmp/OscamPiconsConverter.py
#############################################################################

from sys import argv as sys_argv, stdout as sys_stdout
from os import path as os_path, system as os_system
import glob
import re

from io import BytesIO
import base64

try:
    from PIL import Image
except:
    os_system("opkg update && opkg install python-imaging")
    from PIL import Image

#############################################################################

def table_from_srvid(caidsFilter = []):
    global DIR_OSCAMCFG
    print('Making a table from .srvid file...')
    with open(DIR_OSCAMCFG + '/oscam.srvid','r') as f:
        data = re.findall(r'([0-9a-fA-F@\,\:]+)\|.*', f.read()  )         # the result will [ '0D02,1815,0D97,0653:760d' , '0D96@000004@000008,1815,0966@005123,0653:766a' , '0D02,1815,0D97,0653:0000' ,  ..... ]
    d = {}
    for line in data:
        while '@' in line:                                               # remove all PROVIDs (6 digits with the "@" character at the begin => i.e. 7 places together)
            i = line.find('@')
            line = line[:i] + line[i+7:]
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
    print('...done.\n')
    return d             # { '1807': ['0D03', '0D70', '0D96', '0624'],  '00CD': ['0B00', '09AF'],  '00CA': ['1833', '1834', '1702', '1722', '09C4', '09AF'],  '00CB': ['0B00', '09AF'], ..... }

def table_from_srvid2(caidsFilter = []):
    global DIR_OSCAMCFG
    print('Making a table from .srvid2 file...')
    with open(DIR_OSCAMCFG + '/oscam.srvid2','r') as f:
        data = f.read().splitlines()
    d = {}
    for line in data:
        if line.startswith('#') or line == '':
            continue
        while '@' in line:                                               # remove all PROVIDs (6 digits with the "@" character at the begin => i.e. 7 places together)
            i = line.find('@')
            line = line[:i] + line[i+7:]
        sid, caids = line.upper().split('|')[0].split(':')               # remove the string from "|" to the end of line, and split the remaining part with the ":" character
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
    print('...done.\n')
    return d             # { '1807': ['0D03', '0D70', '0D96', '0624'], '00CD': ['0B00', '09AF'], '00CA': ['1833', '1834', '1702', '1722', '09C4', '09AF'], '00CB': ['0B00', '09AF'], ..... }

def table_from_png_only(caidsFilter = []):
    """
    To make the TPL picons from PNG files for only certain CAIDs (in the user configured value = CAIDS_FILTER)
    """
    global DIR_PNG
    print('Making a table from all PNG files...')
    d = {}
    dir_list = glob.glob(DIR_PNG + '/*.png')
    for path_to_png in dir_list:
        sref   = path_to_png.split('/')[-1].split('.')[0].upper().split('_')
        sid    = sref[3].rjust(4,'0')
        d[sid] = caidsFilter
    print('...done.\n')
    return d

def table_from_png_and_lamedb(caidsFilter = []):
    """
    This function is experimental only, it's for a testing purpose only
    To make the TPL picons from PNG files for user selected CAIDs + filtered with the 'lamedb' database file
    """
    global DIR_PNG
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
    global DIR_TPL, DIR_PNG
    print('Converting PNG to TPL images (Base64/template format)...')
    counter = 0
    for path_to_png in glob.glob(DIR_PNG + '/*.png'):
        sid = path_to_png.split('/')[-1].split('_')[3].rjust(4,'0').upper()
        if sid in sid_table:
            for caid in sid_table[sid]:
                img = Image.open(path_to_png)
                if '-q' in sys_argv:
                    img = img.resize( (100,60), Image.ANTIALIAS )
                else:
                    img.thumbnail((100,60))
                buffer = BytesIO()
                img.save(buffer, format='PNG')           # img.save('/tmp/temp.png', format='PNG')
                data_bin = buffer.getvalue()
                data_string = 'data:image/png;base64,' + base64.b64encode(data_bin)
                with open('{0}/IC_{1}_{2}.tpl'.format(DIR_TPL, caid, sid),'w') as f:
                    f.write(data_string)
                counter += 1
                sys_stdout.write('> %s\r' % counter)
                sys_stdout.flush()
                #with open('/tmp/created_tpl_picons.log','a+') as f:
                #    f.write('{0}/IC_{1}_{2}.tpl\n'.format(DIR_TPL, caid, sid))
            del sid_table[sid]    
    print('\n...done.\n')

#############################################################################

def table_size_checking(tbl):
    dict_length = sum( [len(x) for x in tbl.values()] )
    print('Total number of CAIDs for certain SIDs in conversion table: %s' % dict_length)
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
    python {0} OPTIONS SOURCE-PNG-DIR TARGET-TPL-DIR

OPTIONS:
    -a \t\t\t make TPL picons from all PNG files, created just for user-selected CAIDs only
       \t\t\t WARNING: the argument '-a' must also be specified with the argument '-c CAIDs'!
       \t\t\t          the arguments '-1' and '-2' will also be ignored here!
    -1 \t\t\t make TPL picons from 'oscam.srvid' file, filtered by user-selected CAIDs (if they are specified)
    -2 \t\t\t make TPL picons from 'oscam.srvid2' file, filtered by user-selected CAIDs (if they are specified)
       \t\t\t the 'oscam.srvid2' file can also contain FTA channels with CAID = FFFE, which could also be included as TPL picons
    -c CAID[,CAID,...] \t user-selected CAIDs (which are the only ones to be considered)
       \t\t\t if you do not specify the argument '-c' then all found CAIDs will be used! beware of the large number of CAIDs (TPL files)!
    -o PATH \t\t path to oscam config dir (.srvid and .srvid2 files), if the script did not find the Oscam configuration dir automatically
    -q \t\t\t higher quality image processing with antialiasing filter (higher quality means a larger file size)
    -d \t\t\t delete the whole target TPL-directory before processing

EXAMPLES:
    python {0} -a -c 0624 -d /tmp/transparent-png-220x132 /etc/tuxbox/config/oscam/piconTPL
    python {0} -2 -c 0624,0D96,FFFE /usr/share/enigma2/picon /etc/tuxbox/config/oscam/piconTPL
    python {0} -1 -2 /tmp/png_images /etc/tuxbox/config/oscam/piconTPL
    python {0} -o /etc/tuxbox/config -q -1 /media/hdd/picon /media/hdd/piconTPL

RECOMMENDED:
    python {0} -1 -2 -d -c <your_CAIDs_with_FFFE_included> /usr/share/enigma2/picon /etc/tuxbox/config/oscam/piconTPL
    '''.format(sys_argv[0])  )

def prepare_arguments():    
    global CAIDS_FILTER, DIR_TPL, DIR_PNG, DIR_OSCAMCFG
    
    if len(sys_argv) <= 2 or ('-a' in sys_argv and '-c' not in sys_argv):
        show_man_page()
        return False
    
    if '-a' not in sys_argv:
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
            return False
        if '-2' in sys_argv and not os_path.isfile(DIR_OSCAMCFG + '/oscam.srvid2'):
            print('ERROR ! The oscam.srvid2 file does not exist !')
            return False
    
    if '-c' in sys_argv:
        clist = sys_argv[ sys_argv.index('-c') + 1 ].upper().split(',')
        CAIDS_FILTER = [s.rjust(4, '0') for s in clist]
        print('User-selected CAIDs that will be considered: %s' % ', '.join(CAIDS_FILTER) )
    else:
        CAIDS_FILTER = []
        print('User-selected CAIDs: <blank/empty>  (all found CAIDs will be included !)')
    
    DIR_TPL = sys_argv[-1]
    DIR_PNG = sys_argv[-2]
    
    if not (os_path.isdir(DIR_TPL) and os_path.isdir(DIR_PNG)):
        print('ERROR ! TPL or PNG directory does not exist !')
        return False
    
    return True

#############################################################################

if __name__ == "__main__" and prepare_arguments():
    
    global CAIDS_FILTER, DIR_TPL, DIR_PNG, DIR_OSCAMCFG    
    
    if '-d' in sys_argv:
        os_system('rm -f %s' % (DIR_PNG + '/*.tpl'))
    
    if '-1' in sys_argv and '-a' not in sys_argv:
        table = table_from_srvid(CAIDS_FILTER)
        #import json
        #with open('/tmp/table-1.dat','w') as f:
        #    f.write(json.dumps(table))
        if table_size_checking(table):
            png2tpl(table)
    
    if '-2' in sys_argv and '-a' not in sys_argv:
        table = table_from_srvid2(CAIDS_FILTER)
        #import json
        #with open('/tmp/table-2.dat','w') as f:
        #    f.write(json.dumps(table))
        if table_size_checking(table):
            png2tpl(table)
    
    if '-a' in sys_argv:
        table = table_from_png_only(CAIDS_FILTER)
        if table_size_checking(table):
            png2tpl(table)
    
    print('Good bye')


