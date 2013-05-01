# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure('2') do |config|
  config.vm.box = 'precise64'
  config.vm.hostname = 'dev'
  config.vm.box_url = 'http://files.vagrantup.com/precise64.box'

  config.vm.provider :virtualbox do |vb|
    vb.customize [
      'modifyvm', :id,
      '--memory', '512',
      '--name', 'WURFL Python',
    ]
  end

  config.vm.provision :puppet do |puppet|
    puppet.manifests_path = 'extras/vagrant/manifests'
  end

  config.vm.synced_folder '.', '/vagrant', :nfs => false
end
