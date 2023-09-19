package e2Connectivity

// import ONF ONOS RIC SDK
import (
	e2api "github.com/onosproject/onos-api/go/onos/e2t/e2/v1beta1"
	e2client "github.com/onosproject/onos-ric-sdk-go/pkg/e2/v1beta1"
)

// Defines service model name and version to be used for creating an E2 client.
const (
	svcModelName    = "oran-e2sm-kpm"
	svcModelVersion = "v2"
)

var (
	eventTriggerData     []byte // event trigger payload
	actionDefinitionData []byte // action definitions payload
	actions              []e2api.Action
)

// Creates a New E2 Client
func NewE2Client(e2tAddr string) e2client.Client {
	client := e2client.NewClient(e2client.WithAppID(e2client.AppID("qmai")),
		e2client.WithE2TAddress(e2tAddr, 5150),
		e2client.WithServiceModel(e2client.ServiceModelName(svcModelName),
			e2client.ServiceModelVersion(svcModelVersion)),
		e2client.WithEncoding(e2client.ProtoEncoding))
	return client
}

// Get a E2 Node by ID
func GetE2Node(client e2client.Client, id string) e2client.Node {
	return e2client.Node(client.Node(e2client.NodeID(id)))
}

// Creates a subscription spec for KPM v2
func NewReportSubscription() e2api.SubscriptionSpec {
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

func NewIndicationChannel() chan e2api.Indication {
	ch := make(chan e2api.Indication)
	return ch
}
