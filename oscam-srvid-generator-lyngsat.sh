#!/bin/bash

HEADER="
######################################################################################
### - the script serves as a generator of the 'oscam.srvid' file
### - based on data parsing from website: https://www.lyngsat.com/packages/XXXXXX.html
### - script written by s3n0, 2021-03-13: https://github.com/s3n0
######################################################################################
"

######################################################################################
######################################################################################

find_oscam_cfg_dir()
{
    RET_VAL=""
    DIR_LIST="/etc /var /usr /config"
    for FOLDER in $DIR_LIST; do
        FILEPATH=$(find "${FOLDER}" -iname "oscam.conf" | head -n 1)
        [ -f "$FILEPATH" ] && { RET_VAL="${FILEPATH%/*.conf}"; break; }
    done

    if [ -z "$RET_VAL" ]; then
        OSCAM_BIN=$(find /usr/bin -iname 'oscam*' | head -n 1)
        if [ -z "$OSCAM_BIN" ]; then
            echo -e "ERROR !\nOscam binary file was not found in folder '/usr/bin'.\nAlso, do not find the Oscam configuration directory.\nThe script will be terminated."
            exit 1
        else
            RET_VAL="$($OSCAM_BIN -V | grep -i 'configdir' | awk '{print substr($2,0,length($2)-1)}')"
        fi
    fi

    [ -z "$RET_VAL" ] && echo "WARNING ! Oscam configuration directory not found !"
    echo "$RET_VAL"
}

######################################################################################

create_srvid_file()
{
    # INPUT ARGUMENTS:
    #    $1 = the package name, on a specific https://www.lyngsat.com/packages/XXXXXX.html website (see below)
    #    $2 = CAIDs (separated by comma) what is necessary for the provider
    #    $3 = DVB provider name
    #
    # A NOTE:   "${1^}" provides the string with only first upper character = "Provider"    "${1^^}" provides the upper-case string = "PROVIDER"    "${1}" provides the string = "provider"    "${1,,}" provides the lower-case string = "provider"
    
    URL="https://www.lyngsat.com/packages/${1}.html"
    
    if wget -q -O /tmp/los.html --no-check-certificate "${URL}" > /dev/null 2>&1; then
        echo "URL download successful:  ${URL}"
    else
        echo "URL download FAILED:  ${URL}"
        exit 1
    fi
    
    CHN_MATCH='<font face="Arial"><font size='
    SID_MATCH='<td align="center" bgcolor="#[0-9a-f]+"><font face="Verdana" size=[0-9]+>[0-9 ]+</td>'
    
    LIST=$(cat /tmp/los.html | grep -E -e "${CHN_MATCH}" -e "${SID_MATCH}")
    
    rm -f /tmp/los.html
    
    # Example of the $LIST variable content:
    #
    # <td align="center" bgcolor="#ffcc99"><font face="Verdana" size=1> 2417</td>
    # <td bgcolor="#ffcc99"><font face="Arial"><font size=2><b><a href="https://www.lyngsat.com/tvchannels/pt/Porto-Canal.html">Porto Canal</a></b></td>
    # <td align="center" bgcolor="#ffcc99"><font face="Verdana" size=1> 2418</td>
    # <td bgcolor="#ffcc99"><font face="Arial"><font size=2><b><a href="https://www.lyngsat.com/tvchannels/us/ESPN-2-Africa.html">ESPN 2 Africa</a></b></td>
    # <td align="center" bgcolor="#ffcc99"><font face="Verdana" size=1> 2420</td>
    # <td bgcolor="#ffcc99"><font face="Arial"><font size=2><b><a href="https://www.lyngsat.com/tvchannels/ao/Blast.html">Blast</a></b></td>
    
    RESULT=""
    while IFS= read -r LINE; do
        # if the SID was found at $LINE:
        if grep -q 'align' <<< $LINE; then
            SID=$(echo $LINE | cut -d '>' -f 3 | cut -d '<' -f 1)
            SIDHEX=$(printf "%04X" $SID)                    # converting a decimal value to hexadecimal
            RESULT="${RESULT}${2}:${SIDHEX}|${3}|"
        fi
        # if the CHANNEL name was found at the $LINE:
        if grep -qv 'align' <<< $LINE; then
            CHN=$(echo $LINE | grep -oE 'html">.*' | cut -d '>' -f 2 | cut -d '<' -f 1)
            RESULT="${RESULT}${CHN}\n"
        fi
    done <<< "$LIST"
    
    # the '.srvid' file format is, for example :  "CAID1,CAID2,CAID3:SID|PROVIDER-NAME|CHANNEL-NAME"
    echo -e "$RESULT" > "/tmp/oscam__${1}.srvid"
}

######################################################################################
######################################################################################
######################################################################################

echo "$HEADER"

### if the oscam config directory is not found, then use the "/tmp" directory, to avoid a possible error in the variable below:
OSCAM_CFGDIR=$(find_oscam_cfg_dir)
[ -z "$OSCAM_CFGDIR" ] && { echo "WARNING ! The output directory for the 'oscam.srvid' file was changed to '/tmp' !"; OSCAM_CFGDIR="/tmp"; }

#OSCAM_SRVID="/tmp/oscam_-_merged-kingofsat.srvid"
OSCAM_SRVID="${OSCAM_CFGDIR}/oscam.srvid"

### create temporary ".srvid" files:
create_srvid_file "Skylink" "0D96,0624" "Skylink"
create_srvid_file "Antik-Sat" "0B00" "AntikSAT"
create_srvid_file "Orange-Slovensko" "0B00,0609" "Orange SK"                 # some channels are shared to the AntikSat provider (package), so this one "orangesk" package is also needed for "antiksat" (as the CAID=0B00)
create_srvid_file "Sky-Deutschland" "1833,1834,1702,1722,09C4,09AF" "SKY DE"

### backup the original file "oscam.srvid" to the "/tmp" dir
[ -n "$OSCAM_CFGDIR" -a -f "${OSCAM_CFGDIR}/oscam.srvid" ] && mv "${OSCAM_CFGDIR}/oscam.srvid" "/tmp/oscam_-_backup_$(date '+%Y-%m-%d_%H-%M-%S').srvid"

### merge all generated ".srvid" files into one file + write this new file to the Oscam config-dir:
echo "$HEADER" > $OSCAM_SRVID
echo -e "### File creation date: $(date '+%Y-%m-%d %H:%M:%S')\n" >> $OSCAM_SRVID
cat /tmp/oscam__* >> $OSCAM_SRVID
rm -f /tmp/oscam__*
[ -f "$OSCAM_SRVID" ] && echo "Path to the generated 'oscam.srvid' file:  ${OSCAM_SRVID}"


exit 0


