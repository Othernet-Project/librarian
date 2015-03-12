# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "256"
    vb.cpus = 1
    vb.customize ["modifyvm", :id, "--cpuexecutioncap", "30"]
    vb.name = "Librarian VM"
  end
  config.vm.provision "shell", inline: <<-SHELL
    #!/usr/bin/env bash
  
    set -e
    # Install/remove packages
    sudo DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes install \
        sqlite3 build-essential python-dev python-pip libev-dev gettext
    sudo DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes remove \
        chef puppet

    # Make sure setuptools is latest version
    easy_install -U setuptools

    # Set up directories
    mkdir -p /vagrant/tmp/zipballs
    mkdir -p /vagrant/tmp/downloads
    ln -s /vagrant/tmp/zipballs /srv/zipballs
    ln -s /vagrant/tmp/downloads /var/spool/downloads
    cd /vagrant

    # Install Librarian and dependencies
    python setup.py develop
    sudo pip install repoze
    sudo pip install -r /vagrant/conf/dev_requirements.txt
  SHELL
end
