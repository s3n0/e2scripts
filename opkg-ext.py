#!/usr/bin/env python


##############################################################################################
#### - python script is intended for easier search of installation packages, on feed servers from specific Enigma2 distributions
#### - therefore, it is also necessary to occasionally update the source URLs in this script, i.e. according to the currently released firmware version - for a specific Enigma2
#### - this python script is compatible with both PY2 and PY3
#### - written by s3n0, 2019-2025
##############################################################################################


from __future__ import print_function

import os
import sys
if sys.version_info.major == 3:                                     # data of this object type, as example:   sys.version_info(major=3, minor=10, micro=1, releaselevel='final', serial=0)
    import urllib.request as urllib2
else:
    import urllib2
import ssl                                                          # I use the SSL module for unverified connections with the urllib2 module, due to problems with SSL certificates 
ssl._create_default_https_context = ssl._create_unverified_context  # this will ensure downloading from the Internet without SSL-key verification as default, for all open HTTPS websites


################################# FEEDS variable format: #####################################
####
#### ----atv                    # Enigma2 distribution shortcut for your database (4 x minus/dash character + the Enigma2 distribution shortcut)
####
####
#### http.......Packages.gz     # if the line starts with "http" and ends with "Packages.gz" - it means to download + browse the only one package-list (directly)
####
####
####                            # blank lines are also allowed ! they will ignored :-)
####
####
#### http.........../           # if the line starts with "http" and ends with the "/" (slash character), then the following additional sub-directories (sub-feeds) are assumed...
####                            # ...and the following assumed sub-feeds (sub-folders) will be added after the previous URL (source feed URL)
####                            # ...and also then the string "/Packages.gz" will be added at the end of the whole URL (whole line)
#### armv7ahf-neon              # example 1 - of assumed sub-directory (sub-feed)
#### mips32el                   # example 2 - of assumed sub-directory (sub-feed)
#### vusolo                     # example 3 - of assumed sub-directory (sub-feed)
####
####
####
#### ----END                    # end of your database (4 x minus/dash character + the string END)
####
##############################################################################################



FEEDS = """



----pli


http://taapat.ho.ua/openpli/openpli-5/sh4/Packages.gz



http://downloads.openpli.org/feeds/openpli-8-release/

all

mips32el
3rd-party-mips32el

vusolose
3rd-party-vusolose

et8000
3rd-party-et8000

et6x00
3rd-party-et6x00

armv7ahf-neon
3rd-party-armv7ahf-neon

armv7vehf-neon-vfpv4
cortexa7hf-vfp

cortexa15hf-neon-vfpv4
3rd-party-cortexa15hf-neon-vfpv4

aarch64
3rd-party-aarch64




http://downloads.openpli.org/feeds/openpli-9-release/

all

mips32el
3rd-party-mips32el

vusolose
3rd-party-vusolose

et8000
3rd-party-et8000

et6x00
3rd-party-et6x00

armv7ahf-neon
3rd-party-armv7ahf-neon

armv7vehf-neon-vfpv4
cortexa7hf-vfp

cortexa15hf-neon-vfpv4
3rd-party-cortexa15hf-neon-vfpv4

aarch64
3rd-party-aarch64





----atv

http://feeds2.mynonpublic.com/7.5.1/
formuler4turbo/mips32el
formuler4turbo/all
formuler4turbo/3rdparty
formuler4turbo/formuler4turbo_3rdparty
formuler4turbo/formuler4turbo

vuzero4k/cortexa15hf-neon-vfpv4
vuzero4k/all
vuzero4k/3rdparty
vuzero4k/vuzero4k_3rdparty
vuzero4k/vuzero4k

http://feeds2.mynonpublic.com/7.4/
formuler4turbo/mips32el
formuler4turbo/all
formuler4turbo/3rdparty
formuler4turbo/formuler4turbo_3rdparty
formuler4turbo/formuler4turbo

vuzero4k/cortexa15hf-neon-vfpv4
vuzero4k/all
vuzero4k/3rdparty
vuzero4k/vuzero4k_3rdparty
vuzero4k/vuzero4k

http://feeds2.mynonpublic.com/6.4/
spark/sh4
spark/spark
spark/spark_3rdparty

http://updates.mynonpublic.com/oea/4.4/
mips32el
cortexa15hf-neon-vfpv4
sh4

http://updates.mynonpublic.com/oea/4.3/aarch64/Packages.gz





----pure2

http://pur-e2.club/OU/
6.2/3rdparty
6.3/extra-aarch64
6.5/3rdparty

6.5/vusolo/vusolo
6.5/vusolo/all
6.5/vusolo/mips32el

6.5/vuzero4k/vuzero4k
6.5/vuzero4k/all
6.5/vuzero4k/cortexa15hf-neon-vfpv4

6.5/amikoalien/amikoalien
6.5/amikoalien/all
6.5/amikoalien/sh4

http://pur-e2.club/cam/6.2/aarch64/Packages.gz




----nn2

https://feed.newnigma2.to/weekly/oe2.0/ipk/
mips32el
mips32el-nf




----openeight-arm

http://feed.openeight.de/6.8/
sf8008/all
sf8008/cortexa15hf-neon-vfpv4
sf8008/sf8008
sf8008/3rdparty
sf8008/sf8008_3rdparty
http://openeight.dyndns.tv/armv7/Packages.gz




----entware

http://bin.entware.net/
armv7sf-k2.6
armv7sf-k3.2
mipselsf-k3.4




----satdreamgr

http://188.165.252.42/feeds/satdreamgr-10/
mips32el
armv7ahf-neon
all
vusolo2
sf4008
sf8008
vuzero4k

http://188.165.252.42/feeds/
satdreamgr-extra
satdreamgr-extra-aarch64
satdreamgr-extra-vuzero4k
satdreamgr-extra-osmio4k

http://188.165.252.42/feeds/3rd-party/Packages.gz



----END
"""


FEEDS = FEEDS.splitlines()

FEEDS = [s.strip() for s in FEEDS if s.strip() != '']

###############################################################################################

def downloadFile(url, targetfile):
    header = { 'User-Agent' : 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0' }   # pre stiahnutie obrazkovych suborov z internetu musim zmenit UserAgent-a v requestovacej hlavicke, nakolko niektore webstranky nedovoluju stahovat obrazky urllib2 klientovi, ktory sa pouziva v module Python jazyka
    try:
        req = urllib2.Request(url, None, header)
        content = urllib2.urlopen(req).read()
        with open(targetfile, 'wb') as f:
            f.write(content)
        print('%s - DOWNLOADED' % (url,))
    except urllib2.HTTPError as e:
        print("HTTP Error: ", e, url)
        return False
    except urllib2.URLError as e:
        print("URL Error: ", e, url)
        return False
    except IOError as e:
        print("I/O Error: ", e, targetfile)
        return False
    except Exception as e:
        print("Another error: ", e, targetfile, url)
        return False
    
    return True

def findPackages(distr, ipkname):
    global FEEDS
    print('-' * 20 + ' FEED LISTs DOWNLOADing: ' + '-' * 20)
    
    URL_LIST = []
    i = FEEDS.index('----%s' % distr) + 1
    
    while not FEEDS[i].startswith('----'):
        
        if FEEDS[i].startswith('http'):
            
            if FEEDS[i].endswith('Packages.gz'):
                URL_LIST.append(FEEDS[i])
                i += 1
            
            elif FEEDS[i].endswith('/'):
                url_template = FEEDS[i] + '%s/Packages.gz'
                i += 1
                
                while not FEEDS[i].startswith('----') and not FEEDS[i].startswith('http'):
                    URL_LIST.append(url_template % FEEDS[i])
                    i += 1
    
    db = []
    for feed_url in URL_LIST:
        if downloadFile(feed_url, '/tmp/Packages.gz'):              # from downloaded package will be extracted a text file named as "Package"
            os.system('cd /tmp && gunzip -f /tmp/Packages.gz')      # the one exactly file will be gunzipped, with the same name as the package name (without extension)
            with open('/tmp/Packages', 'r') as f:
                tmp = f.readlines()
            db.append('@@@' + feed_url + '\n')
            db += tmp
            os.remove('/tmp/Packages')
    
    #with open('/tmp/' + sys.argv[0].split(".")[0] + '.tmp', 'w') as f:
    #    f.writelines(db)
    
    index_list = [i for i, val in enumerate(db) if val.startswith('Filename:') and (ipkname in val)]
    if index_list:
        print('-' * 23 + ' PACKAGES FOUND: ' + '-' * 23)
        for idx in index_list:
            url_dir = next(db[i] for i in reversed(range(idx)) if db[i].startswith('@@@'))    # '@@@http://feeds2.mynonpublic.com/6.2/vusolose/mips32el/Packages.gz'
            url_dir = '/'.join(url_dir.split('/')[:-1])                                       # '@@@http://feeds2.mynonpublic.com/6.2/vusolose/mips32el'
            url_dir = url_dir[3:] + '/' + db[idx].split(':')[1].strip()                       # 'http://feeds2.mynonpublic.com/6.2/vusolose/mips32el/7zip-full_16.02-r0_mips32el.ipk'
            print('index = %s, url = %s' % (idx, url_dir))
    else:
        print('The package "%s" was not found.' % ipkname)

def availableDistros():
    global FEEDS
    lst = []
    for line in FEEDS:
        if line.startswith('----') and not line.endswith('END'):
            lst.append(line[4:].strip())
    return lst

###############################################################################################

if __name__ == '__main__':
    
    if len(sys.argv) == 3:      #  1 + 2 arguments are neccessary ! the sum of:  [0] script file name (default built-in argument)   [1] Enigma feed atv/pli   [2] package name to find
        
        scriptname, distro, ipkmatchname = sys.argv
        
        if distro in availableDistros():
            findPackages(distro, ipkmatchname)
    
    else:
        print('USAGE:     python %s <%s> <package-name> \n' % ( sys.argv[0] , '|'.join(availableDistros()) )   +
              'Examples:  python %s pli youtube \n' % sys.argv[0]  +
              '           python %s pure2 oscam \n' % sys.argv[0]  +
              '           python %s atv 7zip' % sys.argv[0]
             )



# Note:
# - list of all feed URLs, currently for the installed local Enigma2 distribution or in the current set-top box: /etc/opkg/*.conf
# - list of all available .ipk packages, already in the form of a database downloaded to the local disk, for the currently installed Enigma2 distribution: /var/lib/opkg/lists
