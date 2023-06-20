package qmaiXapp

// import ONF ONOS RIC SDK
import (
	"fmt"

	e2client "github.com/onosproject/onos-ric-sdk-go/pkg/e2/v1beta1"
)

// Defines service model name and version to be used for creating an  E2 client.
const (
	svcModelName    = "oran-e2sm-kpm"
	svcModelVersion = "v2"
)

func NewE2Client() {
	client := e2client.NewClient(e2client.WithE2TAddress("onos-e2t", 5150),
		e2client.WithServiceModel(e2client.ServiceModelName(svcModelName), e2client.ServiceModelVersion(svcModelVersion)),
		e2client.WithEncoding(e2client.ProtoEncoding))
	fmt.Println(client)
}
