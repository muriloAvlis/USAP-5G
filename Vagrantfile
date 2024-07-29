Vagrant.configure("2") do |config|

    config.vm.synced_folder ".", "/vagrant", disabled: true

    config.hostmanager.enabled = false
    config.hostmanager.manage_host = false
    config.hostmanager.manage_guest = true

    ## VM Core
    config.vm.define :core do |core|
        core.vm.box = "cloud-image/ubuntu-24.04"
        core.vm.hostname = "5gcore"
        core.vm.network "public_network",
            :ip => "10.126.1.120",
            :mode => "bridge",
            :type => "bridge",
            :dev => "br1"

        core.vm.provider :libvirt do |lbv|
            lbv.title = "5gcore"
            lbv.description = "OAI 5G Core Network for USAP project"
            lbv.cpu_mode = "host-model"
            lbv.cpus = 8
            lbv.memory = 24576
            lbv.machine_virtual_size = 60
        end

        core.vm.provision "shell", path: "./scripts/vagrant/5gcore.sh"

        # default router
        core.vm.provision "shell", run: "always", inline: "route add default gw 10.126.1.254"
    end

    ## VM RAN
    config.vm.define :ran do |ran|
        ran.vm.box = "cloud-image/ubuntu-24.04"
        ran.vm.hostname = "5gran"
        ran.vm.network "public_network",
            :ip => "10.126.1.121",
            :mode => "bridge",
            :type => "bridge",
            :dev => "br1"
        ran.vm.provider :libvirt do |lbv|
            lbv.title = "5gran"
            lbv.description = "5G RAN for USAP project"
            lbv.cpu_mode = "host-model"
            lbv.cpus = 8
            lbv.memory = 16384
            lbv.machine_virtual_size = 40
        end

        ran.vm.provision "shell", path: "./scripts/vagrant/5gran.sh"
    end

    ## VM RIC
    config.vm.define :ric do |ric|
        ric.vm.box = "cloud-image/ubuntu-24.04"
        ric.vm.hostname = "nrtric"
        ric.vm.network "public_network",
            :ip => "10.126.1.122",
            :type => "bridge",
            :mode => "bridge",
            :dev => "br1"
        ric.vm.provider :libvirt do |lbv|
            lbv.title = "nrtric"
            lbv.description = "O-RAN RIC for USAP project"
            lbv.cpu_mode = "host-model"
            lbv.cpus = 8
            lbv.memory = 16384
            lbv.machine_virtual_size = 40
        end

        ric.vm.provision "shell", path: "./scripts/vagrant/ric.sh"
    end

    config.vm.provision :hostmanager
end