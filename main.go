package main

import (
	"context"
	"fmt"
	"log"
	"qmaiXapp"
	"time"

	e2api "github.com/onosproject/onos-api/go/onos/e2t/e2/v1beta1"
	e2client "github.com/onosproject/onos-ric-sdk-go/pkg/e2/v1beta1"
)

// Defines service model name and version to be used for creating an  E2 client.
const (
	svcModelName    = "oran-e2sm-kpm"
	svcModelVersion = "v2"
	e2nodeID        = "e2:1/5153"
	subName         = "onos-kpimon-subscription"
)

func main() {
	client := qmaiXapp.NewE2Client(svcModelName, svcModelVersion)
	e2node := client.Node(e2client.NodeID(e2nodeID))

	var eventTriggerData []byte     // codifica um gatilho específico para o evento
	var actionDefinitionData []byte // codifica as definições de ação específica para o SM
	var actions []e2api.Action

	action := e2api.Action{
		ID:   100,
		Type: e2api.ActionType_ACTION_TYPE_REPORT,
		SubsequentAction: &e2api.SubsequentAction{
			Type:       e2api.SubsequentActionType_SUBSEQUENT_ACTION_TYPE_CONTINUE,
			TimeToWait: e2api.TimeToWait_TIME_TO_WAIT_ZERO,
		},
		Payload: actionDefinitionData,
	}

	actions = append(actions, action)

	subSpec := e2api.SubscriptionSpec{
		Actions: actions,
		EventTrigger: e2api.EventTrigger{
			Payload: eventTriggerData,
		},
	}

	ch := make(chan e2api.Indication)
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()
	_, err := e2node.Subscribe(ctx, subName, subSpec, ch)

	if err != nil {
		log.Panic(err)
	}

	for ind := range ch {
		fmt.Println(ind)
	}
}
