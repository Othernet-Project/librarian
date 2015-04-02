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

    PACMAN="pacman --noconfirm --noprogress"

    # Install reflector to sort mirrors
    $PACMAN -Sy
    $PACMAN -S reflector
    reflector --verbose -l 5 --sort rate --save /etc/pacman.d/mirrorlist

    # Update system and install system pkgs
    $PACMAN -Syu
    $PACMAN -S --needed python2-pip libev

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
    pip2 install -e /vagrant
    pip2 install -r /vagrant/conf/dev_requirements.txt
  SHELL
end
