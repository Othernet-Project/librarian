#!/usr/bin/env bash

# setup.sh: Prepare vagrant box for testing artexin code
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


set -e  # Halt on all errors

YES=1
NO=0

EI="easy_install3 -q"
PY="python3"
PIP="pip"
PACMAN="pacman --noconfirm --noprogressbar"

SRCDIR=/vagrant
PRODUCTION=$NO

SPOOLDIR=/var/spool/downloads/content
CONTENTDIR=/srv/zipballs
APPDIR=/opt/librarian
DBDIR=/var/lib/outernet
KEYDIR=/var/lib/outernet/gnupg


###############################################################################
# FILESYSTEM
###############################################################################

echo "Creating directory structure"
mkdir -p $SPOOLDIR      # Directory to hold downloaded zipballs
mkdir -p $CONTENTDIR    # Directory to hold prepared content
mkdir -p $KEYDIR        # Directory to hold gnupg keys (includes $DBDIR)
chmod 700 $SPOOLDIR     # This dir should be kept safe
chmod 700 $KEYDIR       # Application runs as root, so it's OK if it's 700
rm -rf "$APPDIR" || true  # Kill this just in case it already exists
ln -s "$SRCDIR" "$APPDIR"


###############################################################################
# PACKAGES
###############################################################################

# Update local package DB, upgrade packages, and install python
$PACMAN -Sqyu --needed
$PACMAN -Sq --needed python python-pip sqlite


###############################################################################
# LIBRARIES AND DATA FILES
###############################################################################

echo "Installing dependencies"
$PIP install -r "$SRCDIR/conf/requirements.txt"
if [[ $PRODUCTION == $NO ]]; then
    $PIP install -r "$SRCDIR/conf/dev_requirements.txt"
fi

