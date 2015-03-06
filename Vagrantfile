# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "256"
  end
  config.vm.provision "shell", inline: <<-SHELL
    sudo DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes install \
        sqlite3 build-essential python-dev python-pip libev-dev
    sudo DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes remove \
        chef puppet
    sudo pip install -r /vagrant/conf/requirements.txt
    sudo pip install repoze
    ln -s /vagrant/tmp/zipballs /srv/zipballs
    ln -s /vagrant/tmp/downloads /var/spool/downloads
  SHELL
end
