#!/bin/bash

set -ex

if [ $# -lt 1 ]
then
        echo "Usage : $0 [gnb]"
        exit
fi

if [[ ! -z "$AMF_HOSTNAME" ]] ; then 
    export AMF_ADDR="$(host -4 $AMF_HOSTNAME |awk '/has.*address/{print $NF; exit}')"
fi

if [[ -z "${AMF_BIND_ADDR}" ]] ; then
    export AMF_BIND_ADDR=$(ip addr show $AMF_BIND_INTERFACE | grep -Po 'inet \K[\d.]+')
fi

if [[ ! -z "$RIC_HOSTNAME" ]] ; then 
    export RIC_ADDR="$(host -4 $RIC_HOSTNAME |awk '/has.*address/{print $NF; exit}')"
fi

if [[ -z "${RIC_BIND_ADDR}" ]] ; then
    export RIC_BIND_ADDR=$(ip addr show $RIC_BIND_INTERFACE | grep -Po 'inet \K[\d.]+')
fi

envsubst < /gnb-template.yml > gnb.yml

/opt/srsRAN_Project/target/bin/gnb -c gnb.yml