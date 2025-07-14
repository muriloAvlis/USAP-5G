#!/bin/bash

set -e

ip_check="^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$"

if [[ -n "$AMF_HOSTNAME" ]] ; then
    if [[ ${AMF_HOSTNAME} =~ ${ip_check} ]] ; then
        export AMF_ADDR=${AMF_HOSTNAME} ## is a IP format
    else
        export AMF_ADDR="$(getent hosts $AMF_HOSTNAME | awk '{print $1; exit}')" ## is a hostname format
    fi
fi

if [[ -z "${AMF_BIND_ADDR}" ]] ; then
    export AMF_BIND_ADDR="$(ip addr show $AMF_BIND_INTERFACE | grep -Po 'inet \K[\d.]+')"
fi

if [[ ! -z "$RIC_HOSTNAME" ]] ; then
    if [[ ${RIC_HOSTNAME} =~ ${ip_check} ]] ; then
        export RIC_ADDR=${RIC_HOSTNAME} ## is a IP format
    else
        export RIC_ADDR="$(getent hosts $RIC_HOSTNAME | awk '{print $1; exit}')" ## is a hostname format
    fi
fi

if [[ -z "${RIC_BIND_ADDR}" ]] ; then
    export RIC_BIND_ADDR="$(ip addr show $RIC_BIND_INTERFACE | grep -Po 'inet \K[\d.]+')"
fi


envsubst < /gnb-template.yml > /etc/srsran/gnb-config.yml

stdbuf -o0 $RUN_AS -c /etc/srsran/gnb-config.yml

# while true; do sleep 10000; done