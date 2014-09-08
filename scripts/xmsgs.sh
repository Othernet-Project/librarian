#!/usr/bin/env bash

# xmsgs.sh: Extract all messages from sources and templates and build a 
# GNU gettext template file.
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

set -e

SCRIPTDIR="$( cd "$( dirname "$0" )" && pwd )"
. "$SCRIPTDIR/i18n_vars"

PYEXT=py
TPLEXT=tpl

# Paths that will be processed
PYTHON_PATHS=(librarian)
TEMPLATE_PATHS=(librarian/views)

# process_dir $path, $ext
# 
# Process files with extension $ext in directory at $path, and extract all 
# messages into a new PO template, or existing one.
#
process_dir() {
    path=$1
    ext=$2
    joinopt=""

    for file in $(ls $SRCDIR/$path/*.$ext); do
        echo "Processing $file"
        if [[ -f $TEMPLATE ]]; then
            joinopt="--join-existing"
        else
            echo "Creating new PO template $TEMPLATE"
        fi
        xgettext -L python --force-po --copyright-holder="Outernet Inc" \
            --msgid-bugs-address=translations@outernet.is --from-code=UTF-8 \
            --add-comments="Translators," -o $TEMPLATE $joinopt $file
    done
}

# get_po_path $lang
#
# Return the path of the message file for given $lang.
#
get_po_path() {
    lang=$1
    echo "$LOCALEDIR/${lang}/LC_MESSAGES/${DOMAIN}.po"
}

# update_po $lang
#
# Update message catalog for language $lang.
#
update_po() {
    lang=$1
    target_file=$(get_po_path "$lang")
    VERSION_CONTROL=none msgmerge -o "$target_file" \
        "$target_file" "$TEMPLATE" 2> /dev/null
    echo "Updated $target_file."
}

# create_po $lang
#
# Create new message catalog for language $lang.
#
create_po() {
    lang=$1
    target_file=$(get_po_path "$lang")
    msginit --locale="${lang}" --no-translator -o $target_file \
        -i "$TEMPLATE"
    # Fix file encoding
    iconv -f ascii -t utf8 "$target_file" | sed 's|ASCII|UTF-8|' \
        > "${target_file}.new"
    mv "${target_file}.new" "$target_file"
}


for path in ${PYTHON_PATHS[*]}; do
    process_dir $path $PYEXT
done

for path in ${TEMPLATE_PATHS[*]}; do
    process_dir $path $TPLEXT
done

for language in ${LANGUAGES[*]}; do
    path=$(get_po_path "$language")
    mkdir -p $(dirname "$path")
    if [[ ! -f "$path" ]]; then
        create_po "$language"
    else
        update_po "$language"
    fi
done

echo "Bye!"
