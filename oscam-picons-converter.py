#!/usr/bin/env python

#################################
###  .PNG to .TPL converter   ###
###    by s3n0 , 2019-2020    ###
###  https://github.com/s3n0  ###
#################################

#############################################################################
# simple python script for converting PNG to TPL picons (for Oscam-Webif)
#############################################################################
# USAGE:
# ---- Upload the script into the set-top-box, for example into the '/tmp'
#      folder or download the script directly via the Shell:
#           wget -O /tmp/oscam-picons-converter.py --no-check-certificate https://github.com/s3n0/e2scripts/raw/master/oscam-picons-converter.py
# ---- Then start the script via command-line Shell:
#           python /tmp/oscam-picons-converter.py <OPTIONS> <PNG-directory> <TPL-directory>
# ---- Start the script without arguments for show the man-page:
#           python /tmp/oscam-picons-converter.py
# ---- Of course, the script can also be started directly from the internet (from github):
#           wget -qO- --no-check-certificate https://github.com/s3n0/e2scripts/raw/master/oscam-picons-converter.py | python -- - <OPTIONS> <PNG-directory> <TPL-directory>
#############################################################################

import os
import sys
import glob
import re

from io import BytesIO
import base64

try:
    from PIL import Image
except:
    os.system("opkg update && opkg install python-imaging")
    from PIL import Image

#############################################################################

def table_from_srvid(caidsFilter = []):
    global DIR_OSCAMCFG
    print('Making a table from .srvid file...')
    with open(DIR_OSCAMCFG + '/oscam.srvid', 'r') as f:
        data = re.findall(r'([0-9a-fA-F@\,\:]+)\|.*', f.read()  )       # the result will [ '0D02,1815,0D97,0653:760d' , '0D96@000004@000008,1815,0966@005123,0653:766a' , '0D02,1815,0D97,0653:0000' ,  ..... ]
    d = {}
    for line in data:
        while '@' in line:                                              # remove all PROVIDs (6 digits with the "@" character at the begin => i.e. 7 places together)
            i = line.find('@')
            line = line[:i] + line[i+7:]
        caids, sid = line.upper().split(':')                            # split the whole part via ":" character
        caidsToAdd = list(set(caids.split(',')))
        if caidsFilter:
            caidsToAdd = list( set(caidsToAdd)  &  set(caidsFilter)  )  # checking CAIDs by user defined CAIDS_FILTER
        if caidsToAdd:
            #d.setdefault(sid, []).append(caidsToAdd)
            if sid in d.keys():
                d[sid] = d[sid] + caidsToAdd
            else:
                d[sid] = caidsToAdd
    for key in d:               # for key, values in d.iteritems():     # changed due to compatiblity with Python 3 .... because the class .iteritems() only works in Python 2
        values = d[key]
        d[key] = list(set(values))                                      # remove duplicated caids in dictionary variables (browsing through all dict.values for each one dict.key)
    print('...done.\n')
    return d                    # { '1807': ['0D03', '0D70', '0D96', '0624'],  '00CD': ['0B00', '09AF'],  '00CA': ['1833', '1834', '1702', '1722', '09C4', '09AF'],  '00CB': ['0B00', '09AF'], ..... }

def table_from_srvid2(caidsFilter = []):
    global DIR_OSCAMCFG
    print('Making a table from .srvid2 file...')
    with open(DIR_OSCAMCFG + '/oscam.srvid2', 'r') as f:
        data = f.read().splitlines()
    d = {}
    for line in data:
        if line.startswith('#') or line == '':
            continue
        while '@' in line:                                              # remove all PROVIDs (6 digits with the "@" character at the begin => i.e. 7 places together)
            i = line.find('@')
            line = line[:i] + line[i+7:]
        sid, caids = line.upper().split('|')[0].split(':')              # remove the string from "|" to the end of line, and split the remaining part with the ":" character
        caids = re.sub('@[0-9a-fA-F]+', '', caids)                      # remove all strings such as "@0000A1CF" from the line
        caidsToAdd = list(set(caids.split(',')))
        if caidsFilter:    
            caidsToAdd = list( set(caidsToAdd)  &  set(caidsFilter)  )  # checking CAIDs by user defined CAIDS_FILTER
        if caidsToAdd:
            #d.setdefault(sid, []).append(caidsToAdd)
            if sid in d.keys():
                d[sid] = d[sid] + caidsToAdd
            else:
                d[sid] = caidsToAdd
    for key in d:               # for key, values in d.iteritems():     # changed due to compatiblity with Python 3 .... because the class .iteritems() only works in Python 2
        values = d[key]
        d[key] = list(set(values))                                      # remove duplicated caids in dictionary variables (browsing through all dict.values for each one dict.key)
    print('...done.\n')
    return d                    # { '1807': ['0D03', '0D70', '0D96', '0624'], '00CD': ['0B00', '09AF'], '00CA': ['1833', '1834', '1702', '1722', '09C4', '09AF'], '00CB': ['0B00', '09AF'], ..... }

def table_from_png_only(caidsFilter = []):
    """
    To make the TPL picons from PNG files for only certain CAIDs (in the user configured value = CAIDS_FILTER)
    """
    global DIR_PNG
    print('Making a table from all PNG files, with user defined CAIDs...')
    d = {}
    for path_to_png in glob.glob(DIR_PNG + '/*0_0_0.png'):
        sref   = path_to_png.split('/')[-1].split('.')[0].upper().split('_')
        sid    = sref[3].rjust(4,'0')
        d[sid] = caidsFilter
    print('...done.\n')
    return d

#def table_from_png_and_lamedb(caidsFilter = []):
#    """
#    This function is experimental only, it's for a testing purpose only
#    To make the TPL picons from PNG files for user selected CAIDs + filtered with the 'lamedb' database file
#    """
#    global DIR_PNG
#    with open('/etc/enigma2/lamedb', 'r') as f:
#        lamedb = f.read().upper().splitlines()
#    d = {}
#    for path_to_png in glob.glob(DIR_PNG + '/*0_0_0.png'):
#        sref  = path_to_png.split('/')[-1].split('.')[0].upper().split('_')
#        sid   = sref[3].rjust(4,'0')
#        match = ':'.join((sid, sref[6].rjust(8,'0'), sref[4].rjust(4,'0'), sref[5].rjust(4,'0'), str(int(sref[2],16)), '0', '0'))
#        idx   = [ i for i,e in enumerate(lamedb) if match in e ]
#        if idx:
#            idx = idx[0]
#            caids = list(set(  lamedb[idx+2].replace('C:','').split(',')[1:]  )   &   set(caidsFilter)  )
#            if caids:
#                d[sid] = caids
#    return d

#############################################################################

def convert_png2tpl(sid_table):
    global DIR_TPL, DIR_PNG
    print('Converting PNG-picons (files that must exist on disk) to TPL-picons (Base64/template format)...')
    counter = 0
    for path_to_png in glob.glob(DIR_PNG + '/*0_0_0.png'):
        sid = path_to_png.split('_')[-7].rjust(4,'0').upper()
        if sid in sid_table:
            for caid in sid_table[sid]:
                img = Image.open(path_to_png)
                if '-q' in sys.argv:
                    img = img.resize( (100,60), Image.ANTIALIAS )
                else:
                    img.thumbnail((100,60))
                buffer = BytesIO()
                img.save(buffer, format = 'PNG')      # img.save('/tmp/temp.png', format = 'PNG')
                data_tmp = buffer.getvalue()
                data_bytes = b'data:image/png;base64,' + base64.b64encode(data_tmp)
                with open('{0}/IC_{1}_{2}.tpl'.format(DIR_TPL, caid, sid), 'wb') as f:                  # write bytes to file (so, the file must be opened in binary mode)
                    f.write(data_bytes)
                counter += 1
                sys.stdout.write('> %s\r' % counter)
                sys.stdout.flush()
                #with open('/tmp/created_tpl_picons.log','a+') as f:
                #    f.write('{0}/IC_{1}_{2}.tpl\n'.format(DIR_TPL, caid, sid))
            del sid_table[sid]    
    print('\n...done.\n')

#############################################################################

def table_size_checking(tbl):
    dict_length = sum( [len(x) for x in tbl.values()] )
    print('Total number of all CAIDs:SIDs in retrieved table: %s' % dict_length)
    if dict_length > 3000:
        while True:
            answer = user_input('Warning !\nTotal number of all SrvIDs is too high !\nA lot of TPL-picons will be created !\nDo you really want to continue ?\n(y/n)\n>')
            if answer.lower() == 'y':
                return True
            elif answer.lower() == 'n':
                return False
    return True

def show_man_page():
    script_path = "/path_to_script/oscam-picons-converter.py" if len(sys.argv) == 0 or sys.argv[0] == "" else sys.argv[0]
    print("""
python {0} <COMMANDS> <SKIN-PICON-DIRECTORY>

=== BASIC INFO:

    Python script developed to convert PNG-picons (taken from Enigma2-SKIN) to TPL-picons (to Oscam-Webif format).

    The algorithm processes all found PNG-picons belonging to Enigma2-SKIN.

    The TPL-picon name format consists of 'IC_<CAID>_<SID>.tpl' so therefore it is necessary to
    create a table of all CAID:SID as the first.

    I also recommend using the CAID filter, i.e. argument '-c CAIDs' for argument '-a',
    to avoid very many TPL-picons belonging to all existing CAIDs in the Enigma !

=== COMMANDS:

    Method of creating table SID:CAIDs (choose it carefully):
    ---------------------------------------------------------
-a  make a table of SIDs found in all picon names (SIDs obtained from all PNG file names)
    in this case, no CAIDs will be detected / searched !
    only user-defined CAIDs will be used !
        '-c CAIDs' argument is necessary
        '-1' and '-2' will be ignored

-1  make a table from all available SID:CAIDs in 'oscam.srvid' file
        '-c CAIDs' argument is not necessary, but can be used (as filter)
        may be used in combination with '-2'

-2  make a table from all available SID:CAIDs in 'oscam.srvid2' file
        '-c CAIDs' argument is not necessary, but can be used (as filter)
        may be used in combination with '-1'
        
        NOTE: the 'oscam.srvid2' file can also contain FTA channels with CAID = FFFE,
              which could also be included as TPL-picons, automatically in the generated table of CAIDs

    Filter:    (it's important in case of the argument '-a')
    ---------------------------------------------------------
-c <CAID[,CAID,...]>
        user-defined CAIDs separated by a comma (which are the only ones to be considered)...
        if you do not specify the argument '-c' then all found CAIDs will be used in the case
        of '-1' and '-2' arguments ! beware of the large number of CAIDs (TPL files) !!!

    Additional options:
    ---------------------------------------------------------
-o <PATH>    path to oscam config dir, if the script did not find the Oscam configuration dir automatically
-q           higher quality image processing with antialiasing filter (higher quality means a larger file size!)
-d           delete the whole target TPL-directory before processing

=== EXAMPLES:

python {0} -d -a -c 0624 /media/hdd/picon
python {0} -2 -c 0624,0D96,FFFE /usr/share/enigma2/picon
python {0} -1 -2 /media/mmc/picon
python {0} -1 -q -o /etc/tuxbox/config /media/hdd/picon

=== RECOMMENDED USAGE:

python {0} -d -a -c <your_CAIDs_with_FFFE_included> /usr/share/enigma2/picon

""".format(script_path)   )

def user_input(question = ''):          # this user std-in function is compatible both Python 2 and Python 3 (better than function `raw_input` and/or `input`)
    print(question)
    s = sys.stdin.readline()
    return s.rstrip('\n')

def prepare_arguments():    
    global CAIDS_FILTER, DIR_TPL, DIR_PNG, DIR_OSCAMCFG
    
    if len(sys.argv) <= 1 or ('-a' in sys.argv and '-c' not in sys.argv):
        show_man_page()
        return False
    
    DIR_OSCAMCFG = ''
    if '-o' in sys.argv:
        DIR_OSCAMCFG = sys.argv[ sys.argv.index('-o') + 1 ]
    else:
        folder_list = [
            '/etc/tuxbox/config',
            '/etc/tuxbox/config/oscam',
            '/var/tuxbox/config',
            '/usr/keys',
            '/var/keys',
            '/var/etc/oscam',
            '/var/etc',
            '/var/oscam',
            '/config/oscam' ]
        DIR_OSCAMCFG = [d for d in folder_list if os.path.isfile(d + '/oscam.server')]
        if DIR_OSCAMCFG:
            DIR_OSCAMCFG = DIR_OSCAMCFG[0]
            print('Oscam configuration directory found: %s' % DIR_OSCAMCFG)
        else:
            show_man_page()
            print('ERROR ! The Oscam configration folder was not found ! Please use the "-o" argument.')
            return False
    
    DIR_TPL = ''
    with open(DIR_OSCAMCFG + '/oscam.conf', 'r') as f:
        oscam_conf = f.read().split('\n')
    for line in oscam_conf:
        if line.lower().startswith('httptpl'):
            DIR_TPL = line.split('=')[1].strip()
    if DIR_TPL == '':
        print('ERROR ! The TPL-directory not found - in the %s file !' % DIR_OSCAMCFG + '/oscam.conf')
        return False
    else:
        print('TPL-directory found (retrieved from "oscam.conf" file): %s' % DIR_TPL)
    
    if '-a' not in sys.argv:
        if '-1' in sys.argv and not os.path.isfile(DIR_OSCAMCFG + '/oscam.srvid'):
            print('ERROR ! The oscam.srvid file does not exist !')
            return False
        if '-2' in sys.argv and not os.path.isfile(DIR_OSCAMCFG + '/oscam.srvid2'):
            print('ERROR ! The oscam.srvid2 file does not exist !')
            return False
    
    if '-c' in sys.argv:
        clist = sys.argv[ sys.argv.index('-c') + 1 ].upper().split(',')
        CAIDS_FILTER = [s.rjust(4, '0') for s in clist]
        print('User-selected CAIDs that will be considered: %s' % ', '.join(CAIDS_FILTER) )
    else:
        CAIDS_FILTER = []
        print('User-selected CAIDs: <empty/blank>   (all found CAIDs will be included !)')
    
    DIR_PNG = sys.argv[-1]
    
    if not (os.path.isdir(DIR_TPL) and os.path.isdir(DIR_PNG)):
        print('ERROR ! TPL directory "%s" or PNG directory "%s" does not exist !' % (DIR_TPL, DIR_PNG))
        return False
    
    return True

#############################################################################

if __name__ == "__main__" and prepare_arguments():
    
    global CAIDS_FILTER, DIR_TPL, DIR_PNG, DIR_OSCAMCFG    
    
    if '-d' in sys.argv:
        os.system('rm -f %s' % DIR_TPL + '/*.tpl')
    
    if '-1' in sys.argv and '-a' not in sys.argv:
        table = table_from_srvid(CAIDS_FILTER)
        #import json
        #with open('/tmp/table-1.dat','w') as f:
        #    f.write(json.dumps(table))
        if table_size_checking(table):
            convert_png2tpl(table)
    
    if '-2' in sys.argv and '-a' not in sys.argv:
        table = table_from_srvid2(CAIDS_FILTER)
        #import json
        #with open('/tmp/table-2.dat','w') as f:
        #    f.write(json.dumps(table))
        if table_size_checking(table):
            convert_png2tpl(table)
    
    if '-a' in sys.argv:
        table = table_from_png_only(CAIDS_FILTER)
        if table_size_checking(table):
            convert_png2tpl(table)
    
    print('Good bye')


