BUZZFEED_ROOT = '/opt/buzzfeed'

def chef_path(path)
    File.join(BUZZFEED_ROOT, 'chef', path)
end

def deploy_path(path)
    File.join(BUZZFEED_ROOT, 'deploy', path)
end

def require_repos(repo_names)
    missing_repos = repo_names.select do |repo_name|
        not Dir.exists?(File.join(BUZZFEED_ROOT, repo_name, '.git'))
    end
    if missing_repos.size > 0
        puts "These git repositories should be checked out to #{BUZZFEED_ROOT}:\n\n"
        missing_repos.each do |repo_name|
            expected_path = File.join(BUZZFEED_ROOT, repo_name)
            puts "    git clone git@github.com:buzzfeed/#{repo_name}.git #{expected_path}"
        end
        puts "\nMake sure those repositories exist and try again."
        exit 1
    end
end

require_repos(%w(chef deploy wsgi_talk))

system('ssh-add')  # Add ssh key to the agent for forwarding

Vagrant.configure('2') do |config|
    config.vm.box = 'hashicorp/precise64'
    config.vm.hostname = 'dev.wsgi_talk.buzzfeed.com'
    config.vm.network :private_network, ip: '10.16.39.5'
    config.vm.network :forwarded_port, guest: 8090, host: 8090
    
    config.ssh.forward_agent = true
    config.ssh.insert_key = false 
    
    config.vm.provider 'virtualbox' do |v|
       v.memory = 4096 
       v.cpus = 2
       v.auto_nat_dns_proxy = false
       v.customize ['modifyvm', :id, '--natdnsproxy1', 'off']
       v.customize ['modifyvm', :id, '--natdnshostresolver1', 'off']
    end

    config.vm.synced_folder BUZZFEED_ROOT, BUZZFEED_ROOT

    config.vm.provision 'shell', inline: <<SCRIPT
        echo "creating bfdeploy user"
        ssh-add
        useradd -d /home/bfdeploy -m -s /bin/bash bfdeploy
        mkdir ~bfdeploy/.ssh/
        touch ~bfdeploy/.ssh/authorized_keys
        chown -R bfdeploy:bfdeploy ~bfdeploy
        cp -r ~vagrant/.ssh ~bfdeploy/.ssh
SCRIPT

    config.vm.provision 'chef_zero' do |chef|
        chef.verbose_logging = true
        chef.log_level = 'debug'
        chef.cookbooks_path = chef_path('cookbooks')
        chef.roles_path = chef_path('roles')
        chef.environments_path = chef_path('environments')
        chef.data_bags_path = chef_path('data_bags')
        chef.environment = 'development'

        chef.add_recipe('wsgi_talk::default')
        chef.add_recipe('bf-nsq::nsqd')
        chef.add_recipe('bf-nsq::nsqlookupd')
    end

    config.vm.provision 'shell', inline: <<SCRIPT
        echo "copy vagrant pubkey into bfdeploy user's authorized_keys..."
        sudo cat /home/vagrant/.ssh/authorized_keys >> /home/bfdeploy/.ssh/authorized_keys
SCRIPT

    config.vm.provision 'ansible' do |ansible|
        ansible.inventory_path = 'ansible_vm_inventory'
        ansible.playbook = deploy_path('wsgi_talk_deploy.yml')
    end
end
