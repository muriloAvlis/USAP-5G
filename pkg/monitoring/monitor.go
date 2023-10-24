package monitoring

import (
	"context"

	appConfig "github.com/muriloAvlis/qmai/pkg/config"
	"github.com/muriloAvlis/qmai/pkg/rnib"
	e2api "github.com/onosproject/onos-api/go/onos/e2t/e2/v1beta1"
	topoapi "github.com/onosproject/onos-api/go/onos/topo"
	e2smkpmv2 "github.com/onosproject/onos-e2-sm/servicemodels/e2sm_kpm_v2_go/v2/e2sm-kpm-v2-go"
	"github.com/onosproject/onos-kpimon/pkg/broker"
	"github.com/onosproject/onos-kpimon/pkg/store/actions"
	measurmentStore "github.com/onosproject/onos-kpimon/pkg/store/measurements"
	"github.com/onosproject/onos-lib-go/pkg/logging"
	"google.golang.org/protobuf/proto"
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

	// TODO: gets indication/measurements and does a decision in select
	select {
	case err := <-errCh:
		return err
	case <-ctx.Done():
		return ctx.Err()
	}
}

// Process indication msg
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
	// Gets indication msg header
	indHeader := e2smkpmv2.E2SmKpmIndicationHeader{}
	err := proto.Unmarshal(indication.Header, &indHeader)
	if err != nil {
		log.Warn(err)
		return err
	}

	// Gets indication msg payload
	indMessage := e2smkpmv2.E2SmKpmIndicationMessage{}
	err = proto.Unmarshal(indication.Payload, &indMessage)
	if err != nil {
		log.Warn(err)
		return err
	}

	// Gets indication header on format 1
	indHdrFormat1 := indHeader.GetIndicationHeaderFormats().GetIndicationHeaderFormat1()
	indMsgFormat1 := indMessage.GetIndicationMessageFormats().GetIndicationMessageFormat1()
	// log.Debugf("Received indication header format 1 %v:", indHdrFormat1)
	// log.Debugf("Received indication message format 1: %v", indMsgFormat1)

	startTime := getTimeStampFromHeader(indHdrFormat1)
	startTimeUnixNano := toUnixNano(int64(startTime))

	// Gets granularity
	granularity, err := m.appConfig.GetGranularityPeriod()
	if err != nil {
		log.Warn(err)
		return err
	}

	log.Debug(startTimeUnixNano, granularity)

	// gets cell obj ID
	var cid string

	if indMsgFormat1.GetCellObjId() == nil {
		// Use the actions store to find cell object Id based on sub ID in action definition
		key := actions.NewKey(actions.SubscriptionID{
			SubID: indMsgFormat1.GetSubscriptId().GetValue(),
		})

		response, err := m.actionStore.Get(ctx, key)
		if err != nil {
			return err
		}

		actionDefinition := response.Value.(*e2smkpmv2.E2SmKpmActionDefinitionFormat1)
		cid = actionDefinition.GetCellObjId().GetValue()
	} else {
		cid = indMsgFormat1.GetCellObjId().Value
	}

	log.Debugf("Cell object ID: %v", cid)

	// TODO: Review this code to get UEs metrics

	return nil
}
