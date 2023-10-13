package rnib

import (
	"context"

	"github.com/atomix/atomix/api/errors"
	topoapi "github.com/onosproject/onos-api/go/onos/topo"
	"github.com/onosproject/onos-lib-go/pkg/logging"
	toposdk "github.com/onosproject/onos-ric-sdk-go/pkg/topo"
)

// Topo configs
type Config struct {
	TopoAddress string
	TopoPort    int
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
	sdkClient, err := toposdk.NewClient(
		toposdk.WithTopoAddress(
			config.TopoAddress,
			config.TopoPort,
		),
	)
	if err != nil {
		return Client{}, err
	}
	return Client{
		rnibClient: sdkClient,
	}, nil
}

// create a control relation filter
func getControlRelationFilter() *topoapi.Filters {
	filter := &topoapi.Filters{
		KindFilter: &topoapi.Filter{
			Filter: &topoapi.Filter_Equal_{
				Equal_: &topoapi.EqualFilter{
					Value: topoapi.CONTROLS,
				},
			},
		},
	}
	return filter
}

// gets E2 node aspects
func (c *Client) GetE2NodeAspects(ctx context.Context, nodeID topoapi.ID) (*topoapi.E2Node, error) {
	object, err := c.rnibClient.Get(ctx, nodeID)
	if err != nil {
		return nil, err
	}
	e2Node := &topoapi.E2Node{}
	err = object.GetAspect(e2Node)
	return e2Node, err

}

// Checks if an E2 Node has KPM Service Model
func (c *Client) HasKPMRanFunction(ctx context.Context, nodeID topoapi.ID, oid string) bool {
	e2Node, err := c.GetE2NodeAspects(ctx, nodeID)
	if err != nil {
		// log.Warn(err)
		return false
	}

	for _, sm := range e2Node.GetServiceModels() {
		if sm.OID == oid {
			return true
		}
	}

	return false
}

// WatchE2Connections watch e2 node connection changes
func (c *Client) WatchE2Connections(ctx context.Context, ch chan topoapi.Event) error {
	err := c.rnibClient.Watch(ctx, ch, toposdk.WithWatchFilters(getControlRelationFilter()))
	if err != nil {
		return err
	}
	return nil
}

// E2NodeIDs lists all of connected E2 nodes
func (c *Client) E2NodeIDs(ctx context.Context, oid string) ([]topoapi.ID, error) {
	objects, err := c.rnibClient.List(ctx, toposdk.WithListFilters(getControlRelationFilter()))
	if err != nil {
		return nil, err
	}

	e2NodeIDs := make([]topoapi.ID, len(objects))
	for _, object := range objects {
		relation := object.Obj.(*topoapi.Object_Relation)
		e2NodeID := relation.Relation.TgtEntityID
		if c.HasKPMRanFunction(ctx, e2NodeID, oid) {
			e2NodeIDs = append(e2NodeIDs, e2NodeID)
		}
	}
	return e2NodeIDs, nil
}

// get list of cells for each E2 node
func (c *Client) GetCells(ctx context.Context, nodeID topoapi.ID) ([]*topoapi.E2Cell, error) {
	filter := &topoapi.Filters{
		RelationFilter: &topoapi.RelationFilter{
			SrcId:        string(nodeID),
			RelationKind: topoapi.CONTAINS,
			TargetKind:   "",
		},
	}

	objects, err := c.rnibClient.List(ctx, toposdk.WithListFilters(filter))
	if err != nil {
		return nil, err
	}

	var cells []*topoapi.E2Cell
	for _, obj := range objects {
		cellObject := &topoapi.E2Cell{}
		err := obj.GetAspect(cellObject)
		if err != nil {
			log.Warn("Cell entity %s has no E2Cell aspect", obj.ID)
			return nil, err
		}
		cells = append(cells, cellObject)
	}

	if len(cells) == 0 {
		return nil, errors.New(errors.NotFound, "There is no cell to subscribe for E2 node %s", nodeID)
	}

	return cells, nil
}
