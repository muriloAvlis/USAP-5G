import time
from datetime import datetime, timezone
import ntplib


def ntp_ts_to_ms(ntp_timestamp):
    # Offset entre as épocas NTP e Unix (1900-1970 em segundos)
    ntp_epoch_offset = 2208988800

    # Subtract the NTP epoch offset to get Unix timestamp
    unix_timestamp = (ntp_timestamp >> 32) - ntp_epoch_offset

    # Converta para milissegundos
    unix_timestamp_ms = unix_timestamp * 1000

    return unix_timestamp_ms


dt = datetime.now(timezone.utc).timestamp()

ntptime = ntplib.system_to_ntp_time(dt)
print("NTP time: ", ntptime)

ts = ntplib.ntp_to_system_time(ntptime)
print("timestamp NTP:", ts)
