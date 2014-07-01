VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "archlinux-i686"
  config.vm.provision :shell, :path => "scripts/setup.sh"
  config.vm.network "forwarded_port", guest: 80, host: 8080
end
