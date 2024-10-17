#!/bin/bash

ip_check="^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$"

## Search Near-RT RIC IP
if [[ -n "$NEAR_RIC_HOST" ]] ; then 
    if [[ ${NEAR_RIC_HOST} =~ ${ip_check} ]] ; then
        export NEAR_RIC_IP=${NEAR_RIC_HOST} ## is a IP format
    else
        export NEAR_RIC_IP="$(host -4 $NEAR_RIC_IP | awk '/has.*address/{print $NF; exit}')" ## is a hostname format -> convert to ipv4
    fi
fi

## Set Near-RT RIC IP
if [ -n ${NEAR_RIC_IP} ]; then
sed -i "s/NEAR_RIC_IP = 127.0.0.1/NEAR_RIC_IP = ${NEAR_RIC_IP}/g" /etc/usap-xapp/xapp.conf
fi

stdbuf -o0 xapp_usap -c /etc/usap-xapp/xapp.conf