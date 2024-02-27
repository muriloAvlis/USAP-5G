package e2

// import ONF ONOS RIC SDK
import (
	"context"
	"strings"

	"github.com/atomix/atomix/api/errors"
	prototypes "github.com/gogo/protobuf/types"
	appConfig "github.com/muriloAvlis/qmai/pkg/config"
	"github.com/muriloAvlis/qmai/pkg/monitoring"
	"github.com/muriloAvlis/qmai/pkg/rnib"
	e2api "github.com/onosproject/onos-api/go/onos/e2t/e2/v1beta1"
	topoapi "github.com/onosproject/onos-api/go/onos/topo"
	"github.com/onosproject/onos-kpimon/pkg/broker"
	"github.com/onosproject/onos-kpimon/pkg/store/actions"
	"github.com/onosproject/onos-kpimon/pkg/store/measurements"
	"github.com/onosproject/onos-lib-go/pkg/logging"
	e2client "github.com/onosproject/onos-ric-sdk-go/pkg/e2/v1beta1"
)

type Config struct {
	AppID       string
	AppConfig   *appConfig.AppConfig
	E2tAddress  string
	E2tPort     int
	TopoAddress string
	TopoPort    int
	SMName      string
	SMVersion   string
}

// TODO: creates appConfig path
type Manager struct {
	appConfig        *appConfig.AppConfig
	e2client         e2client.Client
	rnibClient       rnib.Client
	serviceModel     ServiceModelOptions
	streams          broker.Broker
	actionStore      actions.Store
	measurementStore measurements.Store
}

const (
	kpmServiceModelOID = "1.3.6.1.4.1.53148.1.2.2.2"
)

var log = logging.GetLogger("qmai", "e2", "manager")

// creates a new E2 Manager
func NewManager(config Config) (Manager, error) {
	// declares SM Name, SM Version and appID
	smName := e2client.ServiceModelName(config.SMName)
	smVer := e2client.ServiceModelVersion(config.SMVersion)
	appID := e2client.AppID(config.AppID)

	// creates an E2 Client
	e2Client := e2client.NewClient(
		e2client.WithAppID(appID),
		e2client.WithServiceModel(smName, smVer),
		e2client.WithE2TAddress(config.E2tAddress, config.E2tPort),
		e2client.WithEncoding(e2client.ProtoEncoding),
	)

	// creates a R-NIB client
	rnibConfig := rnib.Config{
		TopoAddress: config.TopoAddress,
		TopoPort:    config.TopoPort,
	}
	rnibClient, err := rnib.NewClient(rnibConfig)
	if err != nil {
		return Manager{}, err
	}

	return Manager{
		appConfig:  config.AppConfig,
		e2client:   e2Client,
		rnibClient: rnibClient,
		serviceModel: ServiceModelOptions{
			Name:    config.SMName,
			Version: config.SMVersion,
		},
		streams:          broker.NewBroker(),
		actionStore:      actions.NewStore(),
		measurementStore: measurements.NewStore(),
	}, nil
}

func (m *Manager) Start() error {
	// go routine for Watch KPMs from E2 Nodes
	go func() {
		ctx, cancel := context.WithCancel(context.Background())
		defer cancel()
		err := m.watchE2Connections(ctx)
		if err != nil {
			log.Warn(err)
			return
		}
	}()

	return nil
}

func (m *Manager) watchE2Connections(ctx context.Context) error {
	ch := make(chan topoapi.Event)
	err := m.rnibClient.WatchE2Connections(ctx, ch)
	if err != nil {
		log.Warn(err)
		return err
	}

	// verify E2 Nodes events and configure KPMs subscriptions
	for topoEvent := range ch {
		if topoEvent.Type == topoapi.EventType_ADDED || topoEvent.Type == topoapi.EventType_NONE {
			relation := topoEvent.Object.Obj.(*topoapi.Object_Relation)
			e2NodeID := relation.Relation.TgtEntityID

			if !m.rnibClient.HasKPMRanFunction(ctx, e2NodeID, kpmServiceModelOID) {
				log.Debugf("Received topo event does not have KPM RAN Function - %v", topoEvent)
				continue
			}

			go func(t topoapi.Event) {
				log.Debugf("Start subscription process - %v", t)
				err := m.createSubscription(ctx, e2NodeID)
				if err != nil {
					log.Warn(err)
				}
			}(topoEvent)
		} else if topoEvent.Type == topoapi.EventType_REMOVED {
			continue
			// TODO: delete subcription
		}
	}
	return nil
}

func (m *Manager) sendIndicationOnStream(streamID broker.StreamID, ch chan e2api.Indication) {
	// get Writer by stream ID
	streamWriter, err := m.streams.GetWriter(streamID)
	if err != nil {
		log.Error(err)
		return
	}

	// for each msg in channel, send msg to Writer
	for msg := range ch {
		err := streamWriter.Send(msg)
		if err != nil {
			log.Warn(err)
			return
		}
	}
}

// Creates a subscription spec for KPM v2
func (m *Manager) createSubscription(ctx context.Context, e2NodeID topoapi.ID) error {
	log.Info("Creating subscription for E2 node with ID:", e2NodeID)

	// gets E2 Node SM aspects
	aspects, err := m.rnibClient.GetE2NodeAspects(ctx, e2NodeID)
	if err != nil {
		log.Warn(err)
		return err
	}

	// gets report styles for KPM (KPM RAN Function)
	reportStyles, err := m.getReportStyles(aspects.ServiceModels)
	if err != nil {
		log.Warn(err)
		return err
	}

	// gets cells by E2 Node ID
	cells, err := m.rnibClient.GetCells(ctx, e2NodeID)
	if err != nil {
		log.Warn(err)
		return err
	}

	// sets report period
	reportPeriod, err := m.appConfig.GetReportPeriod() // default: 1000 ms
	if err != nil {
		log.Warn(err)
		return err
	}
	log.Debugf("Report period: %d", reportPeriod)

	// creates event trigger data
	eventTriggerData, err := CreateEventTriggerData(int64(reportPeriod))
	if err != nil {
		log.Warn(err)
		return err
	}

	// sets granularity period
	granularityPeriod, err := m.appConfig.GetGranularityPeriod() // default: 1000 ms ?
	if err != nil {
		log.Warn(err)
		return err
	}
	log.Debugf("Granularity: %d", granularityPeriod)

	// prints reports styles
	log.Debugf("Report styles:%v", reportStyles)

	// for each report style creates a subscription
	for _, reportStyle := range reportStyles {
		// creates actions to each cells
		actions, err := m.createSubscriptionActions(ctx, reportStyle, cells, int64(granularityPeriod))
		if err != nil {
			log.Warn(err)
			return err
		}

		measurements := reportStyle.Measurements

		ch := make(chan e2api.Indication)
		node := m.e2client.Node(e2client.NodeID(e2NodeID))
		subName := "qmai-kpm-subscription"

		subSpec := e2api.SubscriptionSpec{
			Actions: actions,
			EventTrigger: e2api.EventTrigger{
				Payload: eventTriggerData,
			},
		}

		// subscribe to E2 Node
		channelID, err := node.Subscribe(ctx, subName, subSpec, ch)
		if err != nil {
			return err
		}
		log.Debugf("Subscription channel ID: %v", channelID)

		// Opens a new stream/buffer to subscription channel
		streamReader, err := m.streams.OpenReader(ctx, node, subName, channelID, subSpec)
		if err != nil {
			return err
		}

		// send indication from ch to stream
		go m.sendIndicationOnStream(streamReader.StreamID(), ch)

		monitor := monitoring.NewMonitor(
			monitoring.WithStreamReader(streamReader),
			monitoring.WithMeasurementStore(m.measurementStore),
			monitoring.WithActionStore(m.actionStore),
			monitoring.WithAppConfig(m.appConfig),
			monitoring.WithMeasurements(measurements),
			monitoring.WithNodeID(e2NodeID),
			monitoring.WithRNIBClient(m.rnibClient),
		)

		err = monitor.Start(ctx)
		if err != nil {
			log.Errorf("Error starting KPM monitor: %v", err)
			return err
		}
	}

	return nil
}

// get E2 Node report style
func (m *Manager) getReportStyles(serviceModelsInfo map[string]*topoapi.ServiceModelInfo) ([]*topoapi.KPMReportStyle, error) {
	for _, sm := range serviceModelsInfo {
		smName := strings.ToLower(sm.Name)
		if smName == string(m.serviceModel.Name) && sm.OID == kpmServiceModelOID {
			kpmRanFunction := &topoapi.KPMRanFunction{}
			for _, ranFunction := range sm.RanFunctions {
				if ranFunction.TypeUrl == ranFunction.GetTypeUrl() {
					err := prototypes.UnmarshalAny(ranFunction, kpmRanFunction)
					if err != nil {
						return nil, err
					}
					return kpmRanFunction.ReportStyles, nil
				}
			}
		}
	}
	return nil, errors.New(errors.NotFound, "cannot retrieve report styles")
}
