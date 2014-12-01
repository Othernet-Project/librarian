#!/usr/bin/env bash

# This script is used by Vagrant. It's not meant to be run by the user.

set -e

apt-get update -y --force-yes
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes install python-pip \
    libev-dev python-dev sqlite3

pip install -r /vagrant/conf/requirements.txt
