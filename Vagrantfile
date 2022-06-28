# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
    # Do this steps on Windows before first run ``vagrant up``
    # 1. download box ``ubuntu/focal64`` from this:
    #    https://app.vagrantup.com/ubuntu/boxes/focal64/versions/20220520.0.0/providers/virtualbox.box
    # 2. comment string #1
    # 3. uncomment string #2 and set you path to downloaded box
    #    For example: /Users/User/Desktop/focal-server-cloudimg-amd64-vagrant.box
    # 4. run ``vagrant up``
    # 5. comment string #2 and uncomment string #1
    # 6. now you can remove downloaded box
    # 7. machine files will be at C:\Users\User\.vagrant.d\boxes
    # 8. if you will remove this machine files, do all steps again

    # string #1
    config.vm.box = "ubuntu/focal64"
    # string #2
    # config.vm.box = "/Users/BoBaH/Skillbox/django_diplom/focal-server-cloudimg-amd64-vagrant.box"

    config.vm.define "develop" do |develop|
        develop.vm.hostname = "develophost"
        develop.vm.network "forwarded_port", guest: 8000, host: 8000

        develop.vm.provider "virtualbox" do |vb|
            vb.name = "develop"
            vb.memory = 2048
        end

        develop.vm.provision "ansible_local" do |ansible|
            ansible.playbook = "scripts/ansible/develop/provision.yml"
            ansible.become = true
            ansible.verbose = "vv"
        end
    end
end
