package utils

import (
	"fmt"
	"net"
)

func GetIpbyHostname(hostname string) (string, error) {
	ipAddr := net.ParseIP(hostname)
	if ipAddr != nil { // it is already IP format
		return ipAddr.String(), nil
	} else { // convert to IPv4 format
		IpAddrList, err := net.LookupIP(hostname)
		if err != nil {
			return "", err
		}

		for _, ipAddr := range IpAddrList {
			if ipAddr.To4() != nil { // first IPv4 occurrence // TODO: review this comportament
				return ipAddr.To4().String(), nil
			}
		}
	}

	return "", fmt.Errorf("unable to get IP Address from host %s", hostname)
}
