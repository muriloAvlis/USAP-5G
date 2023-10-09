package rnib

import (
	"context"

	topoapi "github.com/onosproject/onos-api/go/onos/topo"
	"github.com/onosproject/onos-lib-go/pkg/logging"
	toposdk "github.com/onosproject/onos-ric-sdk-go/pkg/topo"
)

// Topo configs
type Config struct {
	TopoAddress string
	GRPCPort    int
}

// TopoClient R-NIB client interface
type TopoClient interface {
	WatchE2Connections(ctx context.Context, ch chan topoapi.Event) error
	GetCells(ctx context.Context, nodeID topoapi.ID) ([]*topoapi.E2Cell, error)
	GetE2NodeAspects(ctx context.Context, nodeID topoapi.ID) (*topoapi.E2Node, error)
	E2NodeIDs(ctx context.Context, oid string) ([]topoapi.ID, error)
}

// Client topo SDK client
type Client struct {
	rnibClient toposdk.Client
}

var log = logging.GetLogger("qmai", "rnib")

// creates a new Topo client
func NewClient(config Config) (Client, error) {
	sdkClient, err := toposdk.NewClient()
	if err != nil {
		return Client{}, err
	}
	return Client{
		rnibClient: sdkClient,
	}, nil
}
