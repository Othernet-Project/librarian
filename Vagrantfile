# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "terrywang/archlinux"
  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "256"
    vb.name = "Librarian VM"
  end
  config.vm.provision "shell", inline: <<-SHELL
    #!/usr/bin/env bash
  
    set -e
    sudo su
    # System upgrade
    pacman -Syu --noconfirm
    # Install/remove packages
    pacman -S --noconfirm python2-pip

    # Make sure setuptools is latest version
    easy_install -U setuptools

    # Set up directories
    mkdir -p /vagrant/tmp/zipballs
    mkdir -p /vagrant/tmp/downloads
    ln -s /vagrant/tmp/zipballs /srv/zipballs
    ln -s /vagrant/tmp/downloads /var/spool/downloads
    cd /vagrant

    # Install Librarian and dependencies
    pip2 install -e .
    pip2 install -r /vagrant/conf/dev_requirements.txt
  SHELL
end
