#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

## Install packages
apt-get update
apt-get install -y net-tools git sshpass

## Add ssh keys to connect with others nodes
ssh-keygen -t rsa -b 4096 -f ${HOME}/.ssh/id_rsa -q -N ""

### Wait for ssh connection
while [[ ! $(sshpass -p vagrant ssh-copy-id -f -o StrictHostKeyChecking=no -i ${HOME}/.ssh/id_rsa.pub vagrant@5gran) ]] \
 || [[ ! $(sshpass -p vagrant ssh-copy-id -f -o StrictHostKeyChecking=no -i ${HOME}/.ssh/id_rsa.pub vagrant@nrtric) ]] ;
do 
    sleep 3;
done

## Get RKE2
curl -sfL https://get.rke2.io | sudo sh -

## Set RKE2 config
mkdir -p /etc/rancher/rke2 && \
cat <<EOF | tee /etc/rancher/rke2/config.yaml
cni:
    - multus
    - calico
EOF

## Start RKE2
systemctl enable rke2-server.service
systemctl start rke2-server.service
sleep 30

## Get K8s config
mkdir -p /home/vagrant/.kube/
cp /etc/rancher/rke2/rke2.yaml /home/vagrant/.kube/config
chown -R vagrant:vagrant /home/vagrant/.kube/*

## Get kubectl
cp /var/lib/rancher/rke2/bin/kubectl /usr/local/bin/kubectl
kubectl completion bash | tee /etc/bash_completion.d/kubectl > /dev/null

## Send token to workers
scp /var/lib/rancher/rke2/server/node-token vagrant@5gran:/home/vagrant/
scp /var/lib/rancher/rke2/server/node-token vagrant@nrtric:/home/vagrant/

## Install helm
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh

## Change vagrant default password
echo 'vagrant:@admin123#' | chpasswd