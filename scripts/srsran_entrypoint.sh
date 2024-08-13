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
    export AMF_BIND_ADDR="$(ip addr show $AMF_BIND_INTERFACE | grep -Po 'inet \K[\d.]+')"
fi

ip_check="^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$"

if [[ ! -z "$RIC_HOSTNAME" ]] ; then
    if [[ ${RIC_HOSTNAME} =~ ${ip_check} ]] ; then
        export RIC_ADDR=${RIC_HOSTNAME} ## is a IP format
    else
        export RIC_ADDR="$(host -4 $RIC_HOSTNAME |awk '/has.*address/{print $NF; exit}')" ## is a hostname format
    fi
fi

if [[ -z "${RIC_BIND_ADDR}" ]] ; then
    export RIC_BIND_ADDR="$(ip addr show $RIC_BIND_INTERFACE | grep -Po 'inet \K[\d.]+')"
fi

envsubst < /gnb-template.yml > gnb.yml

exec /opt/srsRAN_Project/target/bin/gnb -c gnb.yml