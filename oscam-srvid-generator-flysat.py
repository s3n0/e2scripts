#!/usr/bin/env python

header = """
#######################################################################
###     Simple python-script for create the 'oscam.srvid' file      ###
###         by parsing the https://www.FLYSAT.com web page.         ###
#######################################################################
###   Script written by s3n0, 2021-03-03, https://github.com/s3n0   ###
#######################################################################
"""

output_file = '/tmp/oscam.srvid'

packages = {
  'https://flysat.com/en/package/antiksat-1/eutelsat-16a'      :   '0B00' ,
  'https://flysat.com/en/package/skylink-1/astra-3b'           :   '0D96,0624' ,
  'https://flysat.com/en/package/sky-deutschland-2/astra-19'   :   '1833,1834,1702,1722,09C4,09AF' ,
}

# packages = { 
#   'FlySat_package_name<string>'   :   'list_of_CAIDs_what_you_need_-_separated_by_comma<string>,0001,0001,0003' ,
#   ... 
# }

# # # # # The right provider packages you can find here:
# # # # #    https://www.flysat.com/en/packagelist
# # # # # -- find the URL there by mouse over - under the "Package" columns
# # # # # -- after that, copy the URL and then add your required CAIDs

#############################################################################

from sys import version_info as py_version
if py_version.major == 3:           # data of this object type:   sys.version_info(major=3, minor=8, micro=5, releaselevel='final', serial=0)
    import urllib.request as urllib2
    import html
    htmlParser = html
else:
    import urllib2
    from HTMLParser import HTMLParser
    htmlParser = HTMLParser()

##########

import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass                                                                    # Legacy Python versions (for example v2.7.2) that doesn't verify HTTPS certificates by default
else:
    ssl._create_default_https_context = _create_unverified_https_context    # Handle target environment that doesn't support HTTPS verification --- https://www.python.org/dev/peps/pep-0476/

##########

from datetime import datetime

#############################################################################

def htmlContent(url):
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0'}
    try:
        req = urllib2.Request(url, data=None, headers=headers)
        handler = urllib2.urlopen(req, timeout=15)
        data = handler.read().decode('utf-8')
    except:
        print('ERROR ! Failed to request and download the web-site: %s' % url)
        data = ''
    return data

#############################################################################

if __name__ == '__main__':
    
    result = []
    for pckg in packages:
        
        webpage = htmlContent(pckg)
        
        if webpage:
            print('Web page download successful - package: %s' % pckg)
            
            pckg_name = pckg.split('/')[5]                                          # - output example:   ['https:', '', 'www.flysat.com', 'en', 'package', 'skylink-1', 'astra-3b']
            if pckg_name[-2:] in ('-1', '-2', '-3', '-4'):
                pckg_name = pckg_name[:-2]
            
            #bkp_file = '/tmp/FlySat_-_%s.html' % pckg_name
            #with open(bkp_file, 'w') as f:
            #    f.write(webpage)
            #    print('Web page was stored in a file:  %s' % bkp_file)
            
            i = 2000
            
            while i < len(webpage) - 1000:
                
                # retrieve the channel name
                i = webpage.find('flysat.com/en/channel/', i)
                if i == -1:
                    break # to break the while loop
                i = webpage.find('<b>', i) + 3
                CHN = webpage[ i : webpage.find('</b>', i) ].strip()
                CHN = htmlParser.unescape(CHN)                                      # CHN = CHN.replace('&amp;', '&')
                
                # if the channel name is censored, then retrieve the inner string part between <!-- and -->  +  delete blank characters at the begin/end of string
                #if '<!--' in CHN:
                #    CHN = CHN[ CHN.find('<!--') + 4  :  CHN.find('-->') ].strip()
                # !!! !!! !!! unfortunately, the FlySat database no longer contains the original channel name, which is included in the blacklist (18+), but only contains the censored name - as an asterisk ("*"), i.e. without TAGs "<!--" and "-->"
                if CHN == '*':
                    CHN = '**CENSORED**'
                
                # retrieve all SIDs - next from the channel name
                for x in range(4):
                    i = webpage.find('<td', i+1)
                i = webpage.find('size="1">', i) + 9
                SIDS = webpage[ i  :  webpage.find('</font>', i) ]                  # read the all data in the XML field (table column)
                SIDS = SIDS.replace('\n','').replace('\t','')
                # all possible SIDs are separated in the html table TAG... so... there is '<br>' or '</.....' between these SIDs
                if len(SIDS.split('<br>')) == 2:                                    # if there is only one SID number, then SIDS str variable was not splitted, and we need to split it again - but now via the '<' delimiter
                    SIDS = [ SIDS.split('<')[0] ,]                                  # convert to list type (for SIDS it is neccessary to use just the list data type)
                else:
                    SIDS = SIDS.split('<br>')
                SIDS = [ "%04X" % int(s) for s in SIDS if s.isdigit() ]             # remove all non-numeric (also for a string type) entries from the list + converting decimal to hexadecimal (4-digits) string-numeric values
                
                # a small step to forward
                i += 20
                
                #print('MYDEBUGLOGLINE --- CHN=%s ; SIDS=%s ; i=%s ; pckg=%s' % (CHN, SIDS, i, pckg_name) )
                
                # add the otput to the 'result' variable
                for SID in SIDS:        # if some more SIDs were found...
                    # # # # # # #      CAID(s)      :    SID    |      PROVIDER NAME      |    CHANNEL NAME 
                    result.append(packages[pckg] + ':' + SID + '|' + pckg_name.upper() + '|' + CHN)
        else:
            print('Web page download FAILED !!! - package: %s' % pckg)
    
    if result:
        data = header + '\n### File creation date: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n\n' + '\n'.join(result)
        # delete (rewrite) a file / save the 'result' variable into a file
        with open(output_file, 'w') as f:
            f.write(data)
            print('File "%s" was saved.' % output_file)
    
    print('Good bye.')

#############################################################################
### EoF
