package main

import (
	"fmt"

	"github.com/muriloAvlis/qmai/pkg/e2Connectivity"
)

// Defines service model name and version to be used for creating an  E2 client.
const (
	serviceModelName    = "oran-e2sm-kpm"
	serviceModelVersion = "v2"
)

func main() {
	e2Client := e2Connectivity.NewE2Client(serviceModelName, serviceModelVersion)
	fmt.Println(e2Client.Node())
}
