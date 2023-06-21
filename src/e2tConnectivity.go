package qmaiXapp

// import ONF ONOS RIC SDK
import (
	e2client "github.com/onosproject/onos-ric-sdk-go/pkg/e2/v1beta1"
)

func NewE2Client(svcModelName, svcModelVersion string) e2client.Client {
	client := e2client.NewClient(e2client.WithE2TAddress("192.168.122.100", 5150),
		e2client.WithServiceModel(e2client.ServiceModelName(svcModelName),
			e2client.ServiceModelVersion(svcModelVersion)),
		e2client.WithEncoding(e2client.ProtoEncoding))
	return client
}

// func E2Subscription(nodeID string) {

// }
