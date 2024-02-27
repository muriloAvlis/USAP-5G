package uemgr

import (
	"github.com/onosproject/onos-api/go/onos/uenib"
	"github.com/onosproject/onos-lib-go/pkg/logging"
	"google.golang.org/grpc"
)

var log = logging.GetLogger("qmai", "uenib")

func NewClient() (Manager, error) {
	// ctx, cancel := context.WithCancel(context.Background())
	// defer cancel()
	ueClient := uenib.CreateUEServiceClient(&grpc.ClientConn{})
	log.Info(ueClient)

	return Manager{}, nil
}
