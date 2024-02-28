package uemgr

import (
	"context"
	"io"
	"strconv"

	"github.com/onosproject/onos-api/go/onos/uenib"
	"github.com/onosproject/onos-lib-go/pkg/grpc/retry"
	"github.com/onosproject/onos-lib-go/pkg/logging"
	"github.com/onosproject/onos-ric-sdk-go/pkg/e2/creds"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials"
)

var log = logging.GetLogger("qmai", "uenib")

// creates a new UE Manager
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

	return Manager{
		ueClient: ueClient,
	}, nil
}

// starts UE Manager
func (m *Manager) Start() error {
	// go routine
	go func() {
		ctx, cancel := context.WithCancel(context.Background())
		defer cancel()
		m.listUEs(ctx)
		// err := m.watchUEConnections(ctx) // TODO
		// if err != nil {
		// 	log.Warn(err)
		// 	return
		// }
	}()

	return nil
}

// list all UEs
func (m *Manager) listUEs(ctx context.Context) {
	// sets UE aspect to list
	aspectTypes := []string{"onos.uenib.CellInfo", "operator.SubscriberData"}
	// get UEs stream
	stream, err := m.ueClient.ListUEs(ctx, &uenib.ListUERequest{AspectTypes: aspectTypes})
	if err != nil {
		log.Warn(err)
		return
	}

	// Number of UEs
	num_ues := 0

	for {
		response, err := stream.Recv()
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Warn(err)
		}

		// increment num of UEs
		num_ues++

		// print UE num and UE id
		log.Debugf("UE-%d with ID %v connected", num_ues, response.UE.ID)

		// get UE aspects
		m.getUE(ctx, response.UE.ID, num_ues)

		// create an UE aspect
		m.createUEAspect(ctx, response.UE)
	}

	log.Infof("Total connected UEs: %d", num_ues)
}

// getUE gets UE aspects
func (m *Manager) getUE(ctx context.Context, ueID uenib.ID, num_ue int) {
	response, err := m.ueClient.GetUE(ctx, &uenib.GetUERequest{ID: ueID})
	if err != nil {
		log.Warn(err)
	}

	var aspects []string

	for k := range response.UE.GetAspects() {
		aspects = append(aspects, k)
	}

	log.Debugf("Available aspects of UE-%d: %s", num_ue, aspects)
}

func (m *Manager) createUEAspect(ctx context.Context, ue uenib.UE) {
	// cellTest := topoapi.E2Cell{
	// 	CellObjectID: "e2:4/e00/2/64/e0000",
	// }
	// cellID := cellTest.CellObjectID
	log.Debug("Creating UE aspects")

	ue.SetAspect(&uenib.CellInfo{ServingCell: &uenib.CellConnection{
		ID:             "e2:4/e00/2/64/e0000",
		SignalStrength: 11.0,
	}})

	_, err := m.ueClient.UpdateUE(ctx, &uenib.UpdateUERequest{
		UE: ue,
	})

	if err != nil {
		log.Warn(err)
	}
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
