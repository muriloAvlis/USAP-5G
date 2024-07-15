#!/bin/bash

export DEBIAN_FRONTEND=noninteractive
export K8S_CLUSTER_CONFIG="inventory/mycluster/group_vars/k8s_cluster/k8s-cluster.yml"
export K8S_CLUSTER_ADDONS="inventory/mycluster/group_vars/k8s_cluster/addons.yml"

## Install packages
apt-get update
apt-get install -y net-tools git python3-pip sshpass python3-venv

## Add ssh keys to connect with others nodes
ssh-keygen -t rsa -b 4096 -f ${HOME}/.ssh/id_rsa -q -N ""
sshpass -p vagrant ssh-copy-id -o StrictHostKeyChecking=no -i ${HOME}/.ssh/id_rsa.pub oaicn
while [[ ! ssh root@5gran ]] || [[ ! ssh root@nrtric ]]
do
    sleep 3
done
sshpass -p usap ssh-copy-id -o StrictHostKeyChecking=no -i ${HOME}/.ssh/id_rsa.pub root@5gran
sshpass -p usap ssh-copy-id -o StrictHostKeyChecking=no -i ${HOME}/.ssh/id_rsa.pub root@nrtric

## Configure Kubespray
python3 -m venv ~/kubespray-venv
. ~/kubespray-venv/bin/activate
git clone -b v2.25.0 https://github.com/kubernetes-sigs/kubespray.git
cd kubespray
### Install requirements
python3 -m pip install --break-system-packages -r requirements.txt
### Set inventory file
cp -rfp inventory/sample inventory/mycluster
declare -a IPS=(10.126.1.120 10.126.1.121 10.126.1.122)
CONFIG_FILE=inventory/mycluster/hosts.yaml python3 contrib/inventory_builder/inventory.py ${IPS[@]}
### set cluster configs
sed -i "s/kube_network_plugin_multus: false/kube_network_plugin_multus: true/g" ${K8S_CLUSTER_CONFIG}
sed -i "s/helm_enabled: false/helm_enabled: true/g" ${K8S_CLUSTER_ADDONS}
sed -i "s/ingress_nginx_enabled: false/ingress_nginx_enabled: true/g" ${K8S_CLUSTER_ADDONS}
sed -i "s/metrics_server_enabled: false/metrics_server_enabled: true/g" ${K8S_CLUSTER_ADDONS}
sed -i "s/local_path_provisioner_enabled: false/local_path_provisioner_enabled: true/g" ${K8S_CLUSTER_ADDONS}
### Create cluster
ansible-playbook -i inventory/mycluster/hosts.yaml  --become --become-user=root cluster.yml