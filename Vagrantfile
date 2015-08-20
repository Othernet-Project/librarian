# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.provider "virtualbox" do |vbox|
    vbox.memory = "256"
    vbox.name = "Librarian VM"
  end

  config.vm.define "librarian" do |librarian|
    librarian.vm.box = "ubuntu/trusty64"

    librarian.vm.network "forwarded_port", guest: 80, host: 8080

    config.vm.provision "shell", inline: <<-SHELL
      #!/usr/bin/env bash
      set -e
      apt-get update
      apt-get install -y build-essential g++ python-dev libevent-dev \
                         python-setuptools
      # Make sure setuptools is latest version
      easy_install -U setuptools
      easy_install -U pip
      # Set up directories
      mkdir -p /vagrant/tmp/zipballs
      mkdir -p /vagrant/tmp/downloads
      mkdir -p /var/lib/outernet
      ln -f -s /vagrant/tmp/zipballs /srv/zipballs
      ln -f -s /vagrant/tmp/downloads /var/spool/downloads
      chmod 755 /var/lib/outernet
      chmod 755 /srv/zipballs
      chmod 755 /var/spool/downloads
      # Install Librarian and dependencies
      pip install -e /vagrant
      pip install -r /vagrant/conf/dev_requirements.txt
      pip install -r /vagrant/conf/requirements.txt
    SHELL
  end
end
