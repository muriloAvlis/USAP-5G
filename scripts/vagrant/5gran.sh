#!/bin/bash

export DEBIAN_FRONTEND=noninteractive
export SERVER_ADDR="10.126.1.120"

## Install packages
apt-get update
apt-get install -y net-tools

## Set RKE2 config
curl -sfL https://get.rke2.io | sudo INSTALL_RKE2_TYPE="agent" sh -

sudo mkdir -p /etc/rancher/rke2 && \
sudo cat <<EOF | sudo tee /etc/rancher/rke2/config.yaml
server: https://<server-addr>:9345
token: <token-from-server-node>
EOF

## Wait for token from server
while [ ! -f /home/vagrant/node-token  ]; do
  echo "Waiting for K8s token file..."
  sleep 20
done

export NODE_TOKEN=$(</home/vagrant/node-token)

## Apply configs
sed -i "s/<server-addr>/${SERVER_ADDR}/g" /etc/rancher/rke2/config.yaml
sed -i "s/<token-from-server-node>/${NODE_TOKEN}/g" /etc/rancher/rke2/config.yaml

echo "#--------RKE2 Config--------#"
cat /etc/rancher/rke2/config.yaml

## Start RKE2 agent
sudo systemctl enable rke2-agent.service
sudo systemctl start rke2-agent.service

## Change vagrant default password
echo 'vagrant:@admin123#' | sudo chpasswd