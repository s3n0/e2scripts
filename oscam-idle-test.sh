#!/bin/sh

USR="oscam"
PAS="xxxxxxxxxxxx"

oscam_is_busy() {
    # CHAN_REQ_LIST=$(wget -q -O - "http://${USR}:${PAS}@127.0.0.1:8888/oscamapi.html?part=status" | sed -rn '/<request/,/request>/ {s/.*srvid="([0-9]*)".*/\1/p}')    ## a functional "oscamapi.html" is required, which is unfortunately not included in every Oscam build
    # TOTAL=0; for CHAN in $CHAN_REQ_LIST; do (( TOTAL += CHAN )); done
    # [ $TOTAL -gt 0 ]     # the function returns a boolean (according to the sum of all ServiceIDs watching)

    # DELAY_CLIENT_LIST=$(wget -q -O - --no-check-certificate --no-cache --no-cookies "http://${USR}:${PAS}@127.0.0.1:8888/oscamapi.html?part=status" | awk '/type="c"/,/client>/' | sed -rn 's/.*idle="([0-9]*)".*/\1/p')    ## a functional "oscamapi.html" is required, which is unfortunately not included in every Oscam build
    
    # DELAY_CLIENT_LIST=$(wget -q -O - --no-check-certificate --no-cache --no-cookies "http://${USR}:${PAS}@127.0.0.1:8888/oscamapi.html?part=status" | sed -rn '/type="c"/,/client>/ {s/.*idle="([0-9]*)".*/\1/p}')    ## a functional "oscamapi.html" is required, which is unfortunately not included in every Oscam build
    
    DELAY_CLIENT_LIST=$(wget -q -O - --no-check-certificate --no-cache --no-cookies "http://${USR}:${PAS}@127.0.0.1:8888" | sed -rn '/CLASS="c"/,/TR>/ {s/.*IDLE:\s*([0-9:]*)".*/\1/p}' | tr -d ':')    ## read all idle time from all active clients, but without a colon signs, for example: 000007
    
    for DELAY in $DELAY_CLIENT_LIST; do [ $DELAY -lt 20 ] && break; done    ## if at least one client accesses Oscam within 20 seconds, the function returns the value "0", otherwise the function returns "1"
}

if oscam_is_busy; then 
    echo "Oscam is busy (decoding channels)."
else 
    echo "Oscam is idle (sleeping)."
fi
