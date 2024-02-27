package monitoring

import (
	"context"

	appConfig "github.com/muriloAvlis/qmai/pkg/config"
	"github.com/muriloAvlis/qmai/pkg/rnib"
	e2api "github.com/onosproject/onos-api/go/onos/e2t/e2/v1beta1"
	topoapi "github.com/onosproject/onos-api/go/onos/topo"
	"github.com/onosproject/onos-kpimon/pkg/broker"
	"github.com/onosproject/onos-kpimon/pkg/store/actions"
	measurmentStore "github.com/onosproject/onos-kpimon/pkg/store/measurements"
	"github.com/onosproject/onos-lib-go/pkg/logging"
)

// Indication monitor
type Monitor struct {
	streamReader     broker.StreamReader
	measurementStore measurmentStore.Store
	actionStore      actions.Store
	appConfig        *appConfig.AppConfig
	measurements     []*topoapi.KPMMeasurement
	nodeID           topoapi.ID
	rnibClient       rnib.Client
}

var log = logging.GetLogger("qmai", "monitoring")

func NewMonitor(opts ...Option) *Monitor {
	options := Options{}

	for _, opt := range opts {
		opt.apply(&options)
	}

	return &Monitor{
		streamReader:     options.Monitor.StreamReader,
		measurementStore: options.App.MeasurementStore,
		actionStore:      options.App.ActionStore,
		appConfig:        options.App.AppConfig,
		measurements:     options.Monitor.Measurements,
		nodeID:           options.Monitor.NodeID,
		rnibClient:       options.App.RNIBClient,
	}
}

// Start monitoring process
func (m *Monitor) Start(ctx context.Context) error {
	errCh := make(chan error)
	go func() {
		for {
			indMsg, err := m.streamReader.Recv(ctx)
			if err != nil {
				log.Errorf("Error reading indication stream, chanID:%v, streamID:%v, err:%v", m.streamReader.ChannelID(), m.streamReader.StreamID(), err)
				errCh <- err
			}
			err = m.processIndication(ctx, indMsg, m.measurements, m.nodeID)
			if err != nil {
				log.Errorf("Error processing indication, err:%v", err)
				errCh <- err
			}
		}
	}()

	select {
	case err := <-errCh:
		return err
	case <-ctx.Done():
		return ctx.Err()
	}
}

// Process indication msg (E2 Nodes metrics)
func (m *Monitor) processIndication(ctx context.Context, indication e2api.Indication, measurements []*topoapi.KPMMeasurement, nodeID topoapi.ID) error {
	err := m.processIndicationFormat1(ctx, indication, measurements, nodeID)
	if err != nil {
		log.Warn(err)
		return err
	}
	return nil
}

// Process indication on format 1
func (m *Monitor) processIndicationFormat1(ctx context.Context, indication e2api.Indication, measurements []*topoapi.KPMMeasurement, nodeID topoapi.ID) error {
	return nil
}
