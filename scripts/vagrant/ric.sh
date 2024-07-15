#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

## Install packages
apt-get update
apt-get install -y net-tools

sed -i "s/#PermitRootLogin prohibit-password/PermitRootLogin yes/g" /etc/ssh/sshd_config

echo 'root:usap' | sudo chpasswd

systemctl restart ssh.service

## Clean root password
sleep 30
passwd -d root

## Add default route to bridge
# ip route add default via 10.126.1.254 dev ens6