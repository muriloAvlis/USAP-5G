#!/bin/bash

ip_check="^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$"

## Search Near-RT RIC IP
if [[ -n "$NEAR_RIC_HOST" ]] ; then 
    if [[ ${NEAR_RIC_HOST} =~ ${ip_check} ]] ; then
        export NEAR_RIC_IP=${NEAR_RIC_HOST} ## is a IP format
    else
        export NEAR_RIC_IP="$(host -4 $NEAR_RIC_HOST | awk '/has.*address/{print $NF; exit}')" ## is a hostname format -> convert to ipv4
    fi
fi

## Set Near-RT RIC IP
if [ -n ${NEAR_RIC_IP} ]; then
sed -i "s/NEAR_RIC_IP = 127.0.0.1/NEAR_RIC_IP = ${NEAR_RIC_IP}/g" /etc/usap-xapp/xapp.conf
fi

## Find server IP
if [[ -n ${SERVER_BIND_INTERFACE} ]]; then
    export SERVER_IP=$(ip -4 addr show dev ${SERVER_BIND_INTERFACE} 2>/dev/null | grep inet | awk '{print $2}' | cut -d / -f1);

    # If interface doesn't exist, exit
    if [[ -z "${SERVER_IP}" ]]; then
        echo "[Error]: Device \"${SERVER_BIND_INTERFACE}\" does not exist";
        exit 1;
    fi

    if [[ ${SERVER_IP} =~ ${ip_check} ]]; then
        echo "[INFO]: Set gRPC server IP to ${SERVER_IP} ";
    else 
        echo "[Error]: Invalid IP address obtained from ${SERVER_BIND_INTERFACE}";
        unset ${SERVER_IP};
        exit 1;
    fi
fi

stdbuf -o0 xapp_usap -c /etc/usap-xapp/xapp.conf