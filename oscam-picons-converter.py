#!/usr/bin/env python

print("""
#####################################
###    Oscam Picons Converter     ###
###         .PNG to .TPL          ###
###      by s3n0 , 2019-2022      ###
###    https://github.com/s3n0    ###
#####################################
""")

#############################################################################
# Simple python-script for converting PNG to TPL picons (for Oscam-Webif)
#############################################################################
# GUIDE:
# ---- Upload the script into the set-top-box, for example into the '/tmp' folder
#      or download the script directly via the shell:
#           wget -O /tmp/oscam-picons-converter.py --no-check-certificate https://github.com/s3n0/e2scripts/raw/master/oscam-picons-converter.py
# ---- Then start the script via command-line / shell:
#           python /tmp/oscam-picons-converter.py <COMMANDS>
# ---- Start the script without arguments for show the man-page:
#           python /tmp/oscam-picons-converter.py
# ---- The script can also be started directly from the internet - from my github:
#           wget -qO- --no-check-certificate https://github.com/s3n0/e2scripts/raw/master/oscam-picons-converter.py | python -- - <COMMANDS>
#############################################################################

import sys, os, glob, re, base64

from io import BytesIO

def import_PIL():           # Python Imaging Library (PIL) - is required to convert picons - therefore, it is necessary to verify whether this module is available in the Enigma2/Python distribution
    global Image            # the imported 'Image' must be usable in the entire source code ... therefore, it must be declared as global
    try:
        from PIL import Image
    except:
        return False
    return True

#############################################################################

def table_from_srvid(caidsFilter = []):
    global DIR_OSCAMCFG
    print('Making a SID:CAIDs table from "oscam.srvid" file...')
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
            caidsToAdd = list( set(caidsToAdd)  &  set(caidsFilter)  )  # remove all CAIDs except user-defined CAIDs
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
    print('Making a SID:CAIDs table from "oscam.srvid2" file...')
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
            caidsToAdd = list( set(caidsToAdd)  &  set(caidsFilter)  )  # remove all CAIDs except user-defined CAIDs
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

def table_from_png_files(caidsFilter = []):
    """
    To make the SID:CAIDs table for only certain CAIDs (in the user configured value = CAIDS_FILTER)
    """
    global DIR_PNG
    print('Making a SID table from all *.PNG files (SKIN-picons) + adding the user-determined CAIDs...')
    d = {}
    for path_to_png in glob.glob(DIR_PNG + '/*0_0_0.png'):
        sref   = path_to_png.split('/')[-1].split('.')[0].upper().split('_')
        sid    = sref[3].rjust(4,'0')
        d[sid] = caidsFilter
    print('...done.\n')
    return d

def table_from_lamedb(caidsFilter = []):
    """
    To make the SID:CAIDs table from the '/etc/enigma2/lamedb' Enigma2-database file
    WARNINGs:
    The algorithm do not include the DVB-provider and SAT-TP frequency, so in this case it is ignored ! 
    So, if there are the same CAID for more Providers, it may cause a trouble !
    """
    PROVIDERS = sys.argv[sys.argv.index('-l') + 1].split(',')
    global DIR_PNG
    print('Making a SID table from the "lamedb" file and available *.PNG files + adding the user-determined CAIDs...')
    with open('/etc/enigma2/lamedb', 'r') as f:
        lamedb = f.read()
    if lamedb.count('services') == 2:
        lamedb = lamedb.split('services')[2]
    elif lamedb.count('SERVICES') == 2:
        lamedb = lamedb.split('SERVICES')[2]
    lamedb = lamedb.splitlines()
    d = {}
    for path_to_png in glob.glob(DIR_PNG + '/*0_0_0.png'):
        sref = path_to_png.split('/')[-1].split('.')[0].upper().split('_')
        sid  = sref[3].rjust(4,'0')
        match = ':'.join((sid, sref[6].rjust(8,'0'), sref[4].rjust(4,'0'), sref[5].rjust(4,'0'), str(int(sref[2],16)), '0', '0'))
        #match = ':'.join(( sid, sref[6].rjust(8,'0'), sref[4].rjust(4,'0'), sref[5].rjust(4,'0') ))
        idx = [ i for i, s in enumerate(lamedb) if match in s.upper() ]
        if idx:                 # if the service reference was found in the 'lamedb' file, then checking a existence of the DVB provider name...
            idx = idx[0]
            for provider in PROVIDERS:
                if lamedb[idx+2].startswith('p:%s' % provider.strip()):
                    d[sid] = caidsFilter
                    break
    print('...done.\n')
    return d

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
                    if 'P' in img.getbands():           # it is not possible to use a conversion "filter" when resizing the image, in the case of "P" color mode (when a specific color palette is defined)
                        img = img.convert(mode='RGB')   # so... we need to convert the color mode of the image to an RGB palette (which also means a larger image file on disk)
                    img = img.resize((100,60), Image.ANTIALIAS)
                else:
                    img.thumbnail((100,60))
                buffer = BytesIO()
                img.save(buffer, format='PNG')          # FOR TESTING PURPOSES:   img.save('/tmp/temp_picon.png', format='PNG')
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
        print('Warning !\nTotal number of all SrvIDs is too high !\nA lot of TPL-picons will be created !\n')
    return True
#def table_size_checking(tbl):
#    dict_length = sum( [len(x) for x in tbl.values()] )
#    print('Total number of all CAIDs:SIDs in retrieved table: %s' % dict_length)
#    if dict_length > 3000:
#        while True:
#            answer = user_input('Warning !\nTotal number of all SrvIDs is too high !\nA lot of TPL-picons will be created !\nDo you really want to continue ?\n(y/n)\n>')
#            if answer.lower() == 'y':
#                return True
#            elif answer.lower() == 'n':
#                return False
#    print('')
#    return True

def show_man_page():
    script_path = "/path_to_script/oscam-picons-converter.py" if len(sys.argv) == 0 or sys.argv[0] == "" else sys.argv[0]
    print("""=============================================================================
python {0} <COMMANDS>
=============================================================================

=== ABOUT:

    Python script developed to convert PNG-picons (taken from Enigma2-SKIN)
    to TPL-picons (Oscam-Webif image files, i.e. 'Base64/template' file format).

    The algorithm processes all found PNG-picons belonging to Enigma2-SKIN.
    This means that all necessary .PNG files must exist in the SKIN picon directory.

    The TPL-picon file name consists of 'IC_<CAID>_<SID>.tpl' so therefore
    it is necessary to create a table of all CAID:SID as the first.

    I also recommend using the CAID filter, i.e. argument '-c CAIDs' in the case of argument '-a',
    to avoid very many TPL-picons belonging to all existing CAIDs in the Enigma2.

=== COMMANDS:

    ---------------------------------------------------------
    Method of creating table SID:CAIDs (choose it carefully):
    ---------------------------------------------------------

-1  
    make a table from all available SID:CAIDs in the 'oscam.srvid' file
        '-c CAIDs' argument is not necessary, but it may be used (as a filter)
        may be used in combination with '-2'

-2
    make a table from all available SID:CAIDs in the 'oscam.srvid2' file
        '-c CAIDs' argument is not necessary, but it may be used (as a filter)
        may be used in combination with '-1'
        
        A NOTE:  the 'oscam.srvid2' file especially may also contain FTA channels with CAID = FFFE,
                 which could also be included as TPL-picons, automatically in the generated table of CAIDs

    --------------------------------------
    USE THE -a OR USE THE -l ARGUMENT ONLY
    --------------------------------------

-a  
    make a table of SIDs obtained from all '*.PNG' files (from SKIN-picon directory),
    in this case there are no CAIDs,
    so the user-determined CAIDs will be added
        '-c CAIDs' argument is necessary ! to specify the user's own CAIDs !
        '-1' and '-2' arguments will be ignored here

-l "PROVIDER NAME 1[, PROVIDER NAME 2, ...]"
    
    make a table of SIDs obtained from all '*.PNG' files (from SKIN-picon directory),
    but according to the DVB-provider name, found in the `lamedb` file
        "PROVIDER-NAME" = the name(s) of your DVB-provider in quotation marks, separated by commas,
                          for example:  -l "SKY DE,M7 Group,Polsat"
        '-c CAIDs' argument is necessary ! to specify the user's own CAIDs ! 
                   because the `lamedb` file, unfortunately, does not always contain CAIDs
        '-1' and '-2' arguments will be ignored here

    -----------------------------------------------------------------------------------------
    Filtering or determining of CAIDs (important, in the case of the argument '-a' and '-l'):
    -----------------------------------------------------------------------------------------

-c CAID[,CAID,...]

     user-determined CAIDs separated by a comma (specifying user-defined CAIDs)
   --OR--
     filtered CAIDs - selecting the only required CAIDs what will retrieved from '.srvid' and/or '.srvid2' file
        
   --WARNING--
     if you do not specify the argument '-c' in the case of '-1' and '-2' arguments,
     then all found CAIDs will be used ! beware of the large number of CAIDs (TPL files) !

-------------------
Optional arguments:
-------------------

-o <PATH>   path to the Oscam cfg-directory, if the script did not find the Oscam cfg-directory automatically
-p <PATH>   path to the SKIN-picon directory, if the default '/usr/share/enigma2/picon' directory was not found
-q          higher quality TPL-image processing with antialiasing filter (higher quality means a larger .tpl file size!)
-d          delete the whole TPL-directory before processing

=== RECOMMENDED USAGE:

python {0} -d -a -c <all_your_CAIDs_with_FFFE_included>
python {0} -d -a -c <all_your_CAIDs_with_FFFE_included> -p <SKIN-PICON-DIRECTORY>

=== EXAMPLES:

python {0} -a -c 0624 -p /media/hdd/picon
python {0} -a -c 0624,0D96,FFFE -d
python {0} -1 -c 0624,0D96,FFFE -p /mnt/autofs/nas/picon
python {0} -1 -2 -q -p /media/mmc/picon
python {0} -1 -d
python {0} -2 -q -o /mnt/nas/oscamcfg -p /mnt/nas/picon
python {0} -d -q -a -c 0624,0D96,FFFE
python {0} -l "M7 Group, Towercom" -c 0624,0D96,FFFE

=============================================================================
""".format(script_path) )

def user_input(question = ''):          # this user std-in function is compatible both Python 2 and Python 3 (better than function `raw_input` and / or `input`)
    print(question)
    s = sys.stdin.readline()
    return s.rstrip('\n')

def prepare_arguments():    
    global CAIDS_FILTER, DIR_TPL, DIR_PNG, DIR_OSCAMCFG
    
    if not import_PIL():
        print('WARNING ! The Python Image Library (PIL) is not installed.\nThe library is needed to convert PNG picons to TPL !\nPlease wait, trying to install it now ...')
        if os.system('opkg update > /dev/null 2>&1 && opkg install python-imaging'):
            print('... ERROR ! The Python Image Library (PIL) was not found on your system !')
            return False
        else:
            print('... the Image function from the PIL library was successful installed.')
    
    if len(sys.argv) <= 1 or ('-a' in sys.argv and '-c' not in sys.argv):
        show_man_page()
        print('ERROR ! Missing or wrong arguments !')
        return False
    
    print('Preparing arguments...')
    
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
        DIR_OSCAMCFG = [d for d in folder_list if os.path.isfile(d + '/oscam.conf')]
        if DIR_OSCAMCFG:
            DIR_OSCAMCFG = DIR_OSCAMCFG[0]
            print('Oscam cfg-directory found: %s' % DIR_OSCAMCFG)
        else:
            show_man_page()
            print('ERROR ! Oscam cfg-directory not found ! Please use the "-o" argument.')
            return False
    
    DIR_TPL = ''
    with open(DIR_OSCAMCFG + '/oscam.conf', 'r') as f:
        oscam_conf = f.read().split('\n')
    for line in oscam_conf:
        if line.lower().startswith('httptpl'):
            DIR_TPL = line.split('=')[1].strip()
    if DIR_TPL == '':
        print('ERROR ! The TPL-directory not found - in the "%s" file !' % (DIR_OSCAMCFG + '/oscam.conf'))
        return False
    else:
        print('TPL-directory path was found in the "oscam.conf" configuration file: %s' % DIR_TPL)
        if not os.path.isdir(DIR_TPL):
            print('TPL-directory does not exist ! It will now be created !')
            try:
                os.mkdir(DIR_TPL)
            except OSError:
                print ('ERROR ! Creation of the directory failed: ' % DIR_TPL)
                return False
            else:
                print ('Successfully created the directory: %s' % DIR_TPL)
    
    if ('-a' not in sys.argv) and ('-l' not in sys.argv):
        if '-1' in sys.argv and not os.path.isfile(DIR_OSCAMCFG + '/oscam.srvid'):
            print('ERROR ! The oscam.srvid file does not exist !')
            return False
        if '-2' in sys.argv and not os.path.isfile(DIR_OSCAMCFG + '/oscam.srvid2'):
            print('ERROR ! The oscam.srvid2 file does not exist !')
            return False
    
    if '-l' in sys.argv:
        print('User-selected PROVIDER NAME for "lamedb" file that will be considered: %s' % sys.argv[sys.argv.index('-l') + 1] )
    
    if '-c' in sys.argv:
        clist = sys.argv[ sys.argv.index('-c') + 1 ].upper().split(',')
        CAIDS_FILTER = [s.rjust(4, '0') for s in clist]
        print('User-selected CAIDs that will be considered: %s' % ', '.join(CAIDS_FILTER) )
    else:
        CAIDS_FILTER = []
        print('User-selected CAIDs: <empty/blank>   (all found CAIDs will be included !)')
    
    if '-p' in sys.argv:
        DIR_PNG = sys.argv[ sys.argv.index('-p') + 1 ]
    else:
        DIR_PNG = '/usr/share/enigma2/picon'
    if glob.glob(DIR_PNG + '/*.png'):
        print('PNG-directory (SKIN-picon directory) found: %s ' % DIR_PNG)
    else:
        print('ERROR ! PNG-files was not found in the SKIN-picon folder: %s ' % DIR_PNG)
        return False
    
    #if not (os.path.isdir(DIR_TPL) and os.path.isdir(DIR_PNG)):
    #    print('ERROR ! TPL directory "%s" or PNG directory "%s" does not exist !' % (DIR_TPL, DIR_PNG))
    #    return False
    
    print('...done.\n')
    
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
        table = table_from_png_files(CAIDS_FILTER)
        if table_size_checking(table):
            convert_png2tpl(table)
    
    if '-l' in sys.argv:
        table = table_from_lamedb(CAIDS_FILTER)
        if table_size_checking(table):
            convert_png2tpl(table)
    
    print('Good bye.')

