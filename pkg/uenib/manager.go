package uemgr

import (
	"context"
	"strconv"

	"github.com/onosproject/onos-api/go/onos/uenib"
	"github.com/onosproject/onos-lib-go/pkg/grpc/retry"
	"github.com/onosproject/onos-lib-go/pkg/logging"
	"github.com/onosproject/onos-ric-sdk-go/pkg/e2/creds"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials"
)

var log = logging.GetLogger("qmai", "uenib")

// creates a new uemgr
func NewManager(config Config) (Manager, error) {
	// onos-uenib address
	ueNibServiceAddress := config.UeNibEndpoint + ":" + strconv.Itoa(config.UeNibPort)
	// connects to UE NIB service
	conn, err := connectUeNibServiceHost(ueNibServiceAddress)
	if err != nil {
		return Manager{}, err
	}
	// creates a ue-nib client
	ueClient := uenib.CreateUEServiceClient(conn)
	log.Info(ueClient)

	return Manager{
		ueClient: ueClient,
	}, nil
}

// ConnectUeNibServiceHost connects to UE NIB service
func connectUeNibServiceHost(UeNibServiceAddress string) (*grpc.ClientConn, error) {
	tlsConfig, err := creds.GetClientCredentials()
	if err != nil {
		return nil, err
	}
	opts := []grpc.DialOption{
		grpc.WithTransportCredentials(credentials.NewTLS(tlsConfig)),
	}
	opts = append(opts, grpc.WithUnaryInterceptor(retry.RetryingUnaryClientInterceptor()))
	return grpc.DialContext(context.Background(), UeNibServiceAddress, opts...)
}
