package main

import (
	"fmt"

	"github.com/muriloAvlis/qmai/pkg/e2Connectivity"
	e2 "github.com/onosproject/onos-ric-sdk-go/pkg/e2/v1beta1"
)

// Defines service model name and version to be used for creating an  E2 client.
const (
	serviceModelName    = "oran-e2sm-kpm"
	serviceModelVersion = "v2"
)

func main() {
	e2Client := e2Connectivity.NewE2Client(serviceModelName, serviceModelVersion)
	fmt.Println(e2Client.Node(e2.NodeID("e2:4/e00/2/64")))
}
