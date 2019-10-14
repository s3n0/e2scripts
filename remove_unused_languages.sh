#!/bin/sh

#### HOW TO CHECK INSTALLED LANG. PACKAGES:
#opkg update && opkg list-installed | grep enigma2-locale

#### HOW TO REMOVE LANGUAGE PACKAGES:
#opkg remove --force-depends enigma2-locale-{ar,bg,ca,cs,da,el,en-gb,es,et,fa,fi,fr,fy,he,hr,hu,id,is,it,ku,lt,lv,nb,nl,no,pl,pt,pt-br,ro,ru,sk,sl,sr,sv,th,tr,uk,vi,zh-cn,zh-hk}    # remove all except EN,DE
#opkg remove --force-depends enigma2-locale-{ar,bg,ca,cs,da,el,en-gb,es,et,fa,fi,fr,fy,he,hr,hu,id,is,it,ku,lt,lv,nb,nl,no,pl,pt,pt-br,ro,ru,sl,sr,sv,th,tr,uk,vi,zh-cn,zh-hk}       # remove all except EN,DE,SK

#### HOW TO REMOVE LANGUAGE PACKAGES (WITH THE HELPING OF THE LOOP-FOR, BY S3N0):
opkg remove --force-depends $(ls /usr/share/enigma2/po/ | grep -v -E 'en|de|sk' | awk '{print "enigma2-locale-" $0}' | tr '\n' ' ')     # remove all except EN,DE,SK

#### HOW TO REMOVE LANGUAGE PACKAGES (WITH THE HELPING OF LOOP, BY OpenATV FORUM -> https://www.opena.tv/howtos/41966-howto-sprachen-deinstallieren-nachdem-die-box-online-geflasht-wurde-post360880.html#post360880 ):
#for R in `ls /usr/share/enigma2/po/ | grep -v -E 'de|en|sk'` ; do opkg remove --force-depends enigma2-locale-$R ; done ;                # remove all except EN,DE,SK

#### HOW TO INSTALL LANGUAGE PACKAGES:
#opkg install enigma2-locale-{ar,bg,ca,cs,da,el,en-gb,es,et,fa,fi,fr,fy,he,hr,hu,id,is,it,ku,lt,lv,nb,nl,no,pl,pt,pt-br,ro,ru,sk,sl,sr,sv,th,tr,uk,vi,zh-cn,zh-hk}
#opkg install enigma2-locale-{en,de,sk}

#### A NOTE:
###Please do not remove the English language (en) and the German language (de). These are the default languages that will be used when other languages do not exist. It also has a lot of plugins for OpenATV (as the default localization language in case of emergency).

#### FOLDERS USED IN ENIGMA2 FOR LANG. PACKAGES:
#rm /usr/share/enigma2/countries/*.png
#rm -r /usr/share/enigma2/po/*
