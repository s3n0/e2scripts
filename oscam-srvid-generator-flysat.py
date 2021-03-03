#!/usr/bin/env python

header = """
#######################################################################
###    Simple python-script for create the 'oscam.srvid' files      ###
###   by parsing the https://www.FLYSAT.com/XXXXXX.php web page.    ###
#######################################################################
###   Script written by s3n0, 2021-03-03, https://github.com/s3n0   ###
#######################################################################
"""

output_file = '/tmp/oscam.srvid'

packages = {
  'antiksat'   :   '0B00' ,
  'skylink'    :   '0D96,0624' ,
  'skyde'      :   '1833,1834,1702,1722,09C4,09AF' ,
}

#{ 'FlySat_package_name <string>'  :  'list_of_CAIDs_separated_by_comma <string>' ,  ...... }

#############################################################################

from sys import version_info as py_version
if py_version.major == 3:           # data of this object type:   sys.version_info(major=3, minor=8, micro=5, releaselevel='final', serial=0)
    import urllib.request as urllib2
else:
    import urllib2

import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass                                                                    # Legacy Python versions (for example v2.7.2) that doesn't verify HTTPS certificates by default
else:
    ssl._create_default_https_context = _create_unverified_https_context    # Handle target environment that doesn't support HTTPS verification --- https://www.python.org/dev/peps/pep-0476/

from datetime import datetime

#############################################################################

def htmlContent(url):
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0'}
    try:
        req = urllib2.Request(url, data=None, headers=headers)
        handler = urllib2.urlopen(req, timeout=15)
        data = handler.read()
    except:
        print('ERROR ! Failed to request and download the web-site: %s' % url)
        data = ''
    return data

#############################################################################

if __name__ == '__main__':
    
    result = []
    
    for pckg in packages:
        html = htmlContent('https://www.flysat.com/%s.php' % pckg)
        if html:
            print('Web page download successful - package name: %s' % pckg)
            
            i = 2000
            while i < len(html)-1000:
                
                # retrieve the channel name
                i = html.find('height="30">', i)
                if i == -1:
                    break # break the while-loop
                i = html.find('<b>', i) + 3
                CHN = html[ i  :  html.find('</b>', i) ]
                if '<!--' in CHN:
                    CHN = CHN[ CHN.find('<!--') + 4  :  CHN.find('-->') ].strip()   # if the channel name is censored, then retrieve the inner string part between <!-- and -->  +  delete blank characters at the begin/end of string
                
                # retrieve all SIDs - next from the channel name
                i = html.find('color="#0000ff" size=1>', i) + 23
                SIDS = html[ i  :  html.find('\n', i) ]                             # read the string to end of line
                # all possible SIDs are separated in the html table TAG... so... there is '<br>' or '</.....' between these SIDs
                if len(SIDS.split('<br>')) == 1:                                    # if there is only one SID number, then SIDS str variable was not splitted, and we need to split it again - but now via the '<' delimiter
                    SIDS = [ SIDS.split('<')[0] ,]                                  # convert to list type (for SIDS it is neccessary to use just the list data type)
                else:
                    SIDS = SIDS.split('<br>')
                SIDS = [ "%04X" % int(s) for s in SIDS if s.isdigit() ]             # remove all non-numeric (also for a string type) entries from the list + converting decimal to hexadecimal (4-digits) string-numeric values
                
                # a small step to forward
                i += 10
                
                #print('MYDEBUGLOGLINE--CHN=%s;;SIDS=%s;;i=%s;;pckg=%s;;' % (CHN, SIDS, i, pckg) )
                
                # add the otput to the 'result' variable
                for SID in SIDS:  # if some more SIDs were found...
                    # # # # # # # # #  "  CAIDS     :    SID    |    PROVIDER        |  CHANNEL   "
                    result.append(packages[pckg] + ':' + SID + '|' + pckg.upper() + '|' + CHN)
        else:
            print('Web page download FAILED !!! - package name: %s' % pckg)
    
    if result:
        data = header + '\n### File creation date: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n\n' + '\n'.join(result)
        # delete (rewrite) a file / save the 'result' variable into a file
        with open(output_file, 'w') as f:
            f.write( data )
            print('File "%s" was saved.' % output_file)
    
    print('Good bye.')

#############################################################################
### EoF
