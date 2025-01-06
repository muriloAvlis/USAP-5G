#!/bin/bash

set -ex

# IP address resolution from interfaces or hostnames
if [[ ! -z "$GNB_HOSTNAME" ]] ; then 
    export GNB_ADDRESS="$(host -4 $GNB_HOSTNAME |awk '/has.*address/{print $NF; exit}')"
fi
if [[ ! -z "$UE_HOSTNAME" ]] ; then 
    export UE_ADDRESS="$(host -4 $UE_HOSTNAME |awk '/has.*address/{print $NF; exit}')"
fi

echo "Launching srsue"

envsubst < /etc/srsran/ue.conf > ue.conf
if [ "$SRSUE_5G" = true ] ; then
    sed -i 's/#device_name = zmq/device_name = zmq\ndevice_args = tx_port=tcp:\/\/${UE_ADDRESS}:2001,rx_port=tcp:\/\/${GNB_ADDRESS}:2000,id=ue,base_srate=23.04e6/' ue.conf
    sed -i 's/^dl_earfcn =.*/dl_earfcn = ${DL_EARFCN}/' ue.conf
    sed -i 's/^# bands = .*/bands = ${BANDS}/' ue.conf
    sed -i 's/^#apn =.*/apn = ${APN}/' ue.conf
    sed -i 's/^#apn_protocol =.*/apn_protocol = ${APN_PROTOCOL}/' ue.conf
    sed -i 's/^#srate =.*/srate = ${SRATE}e6/' ue.conf
    sed -i 's/^#rx_gain =.*/rx_gain = ${RX_GAIN}/' ue.conf
    sed -i 's/^tx_gain =.*/tx_gain = ${TX_GAIN}/' ue.conf
    sed -E -i '/^\[rat\.eutra\]/{n;n;s/^#nof_carriers = .*/nof_carriers = ${EUTRA_NOF_CARRIERS}/}' ue.conf
    sed -E -i '/^\[rat\.nr\]/{n;n;s/^# nof_carriers = .*/nof_carriers = ${NR_NOF_CARRIERS}/}' ue.conf
    sed -i '/\[rat.nr\]/a\max_nof_prb = ${NR_MAX_NOF_PRB}' ue.conf
    sed -i '/\[rat.nr\]/a\nof_prb = ${NR_NOF_PRB}' ue.conf
    
elif [ "$ZMQ" = true ] ; then
    sed -i 's/#device_name = zmq/device_name = zmq\ndevice_args = tx_port=tcp:\/\/${UE_ADDRESS}:2001,rx_port=tcp:\/\/${GNB_ADDRESS}:2000,id=ue,base_srate=23.04e6/' ue.conf
    
fi

envsubst < ue.conf > ue_temp.conf
mv ue_temp.conf ue.conf
/bin/srsue ue.conf