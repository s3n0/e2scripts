#!/bin/sh

USR="oscam"
PAS="xxxxxxxxxxxx"

oscam_is_busy() {
    # CHAN_REQ_LIST=$(wget -q -O - "http://${USR}:${PAS}@127.0.0.1:8888/oscamapi.html?part=status" | sed -rn '/<request/,/request>/ {s/.*srvid="([0-9]*)".*/\1/p}')
    # TOTAL=0; for CHAN in $CHAN_REQ_LIST; do (( TOTAL += CHAN )); done
    # [ $TOTAL -gt 0 ]     # the function returns a boolean (according to the sum of all ServiceIDs watching)

    # --- alternative 1 ---
    #DELAY_CLIENT_LIST=$(wget -q -O - --no-check-certificate --no-cache --no-cookies "http://${USR}:${PAS}@127.0.0.1:8888/oscamapi.html?part=status" | sed -rn '/type="c"/,/client>/ {s/.*idle="([0-9]*)".*/\1/p}')
    # --- alternative 2 ---
    #DELAY_CLIENT_LIST=$(wget -q -O - --no-check-certificate --no-cache --no-cookies "http://${USR}:${PAS}@127.0.0.1:8888/oscamapi.html?part=status" | awk '/type="c"/,/client>/' | sed -rn 's/.*idle="([0-9]*)".*/\1/p')
    # --- alternative 3 ---
    DELAY_CLIENT_LIST=$(wget -q -O - --no-check-certificate --no-cache --no-cookies "http://${USR}:${PAS}@127.0.0.1:8888/oscamapi.html?part=status" | sed -rn '/type="c"/,/client>/ {s/.*idle="([0-9]*)".*/\1/p}')
    
    for DELAY in $DELAY_CLIENT_LIST; do [ $DELAY -lt 20 ] && break; done     # if at least one client accesses Oscam within 20 seconds, the function returns the value "0", otherwise the function returns "1"
}

if oscam_is_busy; then 
    echo "Oscam is busy (decoding channels)."
else 
    echo "Oscam is idle (sleeping)."
fi
