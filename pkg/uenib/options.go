package uemgr

import "github.com/onosproject/onos-api/go/onos/uenib"

type Manager struct {
	ueClient uenib.UEServiceClient
}

type Config struct {
	UeNibEndpoint string
	UeNibPort     int
}
