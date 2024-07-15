#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

## Install packages
apt-get update
apt-get install -y net-tools

sed -i "s/#PermitRootLogin prohibit-password/PermitRootLogin yes/g" /etc/ssh/sshd_config

echo 'root:usap' | sudo chpasswd

systemctl restast ssh.service