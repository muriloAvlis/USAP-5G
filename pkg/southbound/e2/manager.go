package e2

// import ONF ONOS RIC SDK
import (
	"context"
	"strings"

	"github.com/atomix/atomix/api/errors"
	prototypes "github.com/gogo/protobuf/types"
	"github.com/muriloAvlis/qmai/pkg/rnib"
	topoapi "github.com/onosproject/onos-api/go/onos/topo"
	"github.com/onosproject/onos-lib-go/pkg/logging"
	e2client "github.com/onosproject/onos-ric-sdk-go/pkg/e2/v1beta1"
)

type Config struct {
	AppID       string
	E2tAddress  string
	E2tPort     int
	TopoAddress string
	TopoPort    int
	SMName      string
	SMVersion   string
}

type Manager struct {
	config     Config
	e2client   e2client.Client
	rnibClient rnib.Client
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
		e2client:   e2Client,
		rnibClient: rnibClient,
	}, nil
}

func (m *Manager) Start() error {
	// go routine for Watch KPMs
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

// Creates a subscription spec for KPM v2
func (m *Manager) createSubscription(ctx context.Context, e2NodeID topoapi.ID) error {
	log.Info("Creating subscription for E2 node with ID:", e2NodeID)
	aspects, err := m.rnibClient.GetE2NodeAspects(ctx, e2NodeID)
	if err != nil {
		log.Warn(err)
		return err
	}

	// get report styles for KPM
	reportStyles, err := m.getReportStyles(aspects.ServiceModels)
	if err != nil {
		log.Warn(err)
		return err
	}

	// get cells for each E2 Node
	cells, err := m.rnibClient.GetCells(ctx, e2NodeID)
	if err != nil {
		log.Warn(err)
		return err
	}

	// TODO
	// reportPeriod, err := m.config.AppID

	return nil
}

// get E2 Node report style
func (m *Manager) getReportStyles(serviceModelsInfo map[string]*topoapi.ServiceModelInfo) ([]*topoapi.KPMReportStyle, error) {
	for _, sm := range serviceModelsInfo {
		smName := strings.ToLower(sm.Name)
		if smName == string(m.config.SMName) && sm.OID == kpmServiceModelOID {
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
