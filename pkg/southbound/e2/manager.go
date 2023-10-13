package e2

// import ONF ONOS RIC SDK
import (
	"context"

	"github.com/muriloAvlis/qmai/pkg/rnib"
	e2api "github.com/onosproject/onos-api/go/onos/e2t/e2/v1beta1"
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
				log.Debugf("Creating subscription - %v", t)
				// TODO: Create a new subscription logic
			}(topoEvent)
		} else if topoEvent.Type == topoapi.EventType_REMOVED {
			continue
			// TODO: delete subcription
		}
	}
	return nil
}

// Creates a subscription spec for KPM v2
func NewReportSubscription() e2api.SubscriptionSpec {
	var actionDefinitionData, eventTriggerData []byte // action definitions payload
	var actions []e2api.Action

	// define a action
	action := e2api.Action{
		ID:   100,
		Type: e2api.ActionType_ACTION_TYPE_REPORT,
		SubsequentAction: &e2api.SubsequentAction{
			Type:       e2api.SubsequentActionType_SUBSEQUENT_ACTION_TYPE_CONTINUE,
			TimeToWait: e2api.TimeToWait_TIME_TO_WAIT_ZERO,
		},
		Payload: actionDefinitionData,
	}

	// slice of actions
	actions = append(actions, action)

	// subscription spec
	subSpec := e2api.SubscriptionSpec{
		Actions: actions,
		EventTrigger: e2api.EventTrigger{
			Payload: eventTriggerData,
		},
	}

	return subSpec
}
