#!/usr/bin/env bash

# cmpmsgs.sh: Compile all translations into MO files
#
# author: 	Outernet Inc <branko@outernet.is>
# version: 	0.1
#
# Copyright 2014, Outernet Inc.
# Some rights reserved.
# 
# This software is free software licensed under the terms of GPLv3. See COPYING
# file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
#

SCRIPTDIR="$( cd "$( dirname "$0" )" && pwd )"
. "$SCRIPTDIR/i18n_vars"


get_lang_dir() {
    lang=$1
    echo "$LOCALEDIR/$lang/LC_MESSAGES"
}

get_po_path() {
    lang=$1
    echo $(get_lang_dir "$lang")/${DOMAIN}.po
}

get_mo_path() {
    lang=$1
    echo $(get_lang_dir "$lang")/${DOMAIN}.mo
}


for lang in ${LANGUAGES[*]}; do
    mopath=$(get_mo_path "$lang")
    popath=$(get_po_path "$lang")
    msgfmt -o "$mopath" "$popath"
    echo "Compiled ${mopath}."
done
