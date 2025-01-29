#!/bin/bash

set -e

ip_check="^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$"

if [[ ! -z "$AMF_HOSTNAME" ]] ; then
    if [[ ${AMF_HOSTNAME} =~ ${ip_check} ]] ; then
        export AMF_ADDR=${AMF_HOSTNAME} ## is a IP format
    else
        export AMF_ADDR="$(host -4 $AMF_HOSTNAME |awk '/has.*address/{print $NF; exit}')" ## is a hostname format
    fi
fi

envsubst < /etc/config/gnb-config.yml > /etc/config/gnb-config-final.yml

#### To DPDK #####

if [[ -n "${ISOLATED_CPUS:-}" ]]; then
    stdbuf -o0 taskset -c $ISOLATED_CPUS chrt -r 1 $RUN_AS -c /etc/config/gnb-config-final.yml
else
    $RUN_AS -c /etc/config/gnb-config-final.yml
fi