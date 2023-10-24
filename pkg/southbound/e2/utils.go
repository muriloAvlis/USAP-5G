package e2

import (
	"context"
	"sort"

	e2api "github.com/onosproject/onos-api/go/onos/e2t/e2/v1beta1"
	topoapi "github.com/onosproject/onos-api/go/onos/topo"
	"github.com/onosproject/onos-e2-sm/servicemodels/e2sm_kpm_v2_go/pdubuilder"
	e2smkpmv2 "github.com/onosproject/onos-e2-sm/servicemodels/e2sm_kpm_v2_go/v2/e2sm-kpm-v2-go"
	actionsstore "github.com/onosproject/onos-kpimon/pkg/store/actions"
	"google.golang.org/protobuf/proto"
)

// creates event trigger data
func CreateEventTriggerData(rtPeriog int64) ([]byte, error) {
	e2SmKpmEventTriggerDefinition, err := pdubuilder.CreateE2SmKpmEventTriggerDefinition(rtPeriog)
	if err != nil {
		return []byte{}, err
	}

	err = e2SmKpmEventTriggerDefinition.Validate()
	if err != nil {
		return []byte{}, err
	}

	protoBytes, err := proto.Marshal(e2SmKpmEventTriggerDefinition)
	if err != nil {
		return []byte{}, err
	}

	return protoBytes, nil
}

// creates a subscription actions for each cell
func (m *Manager) createSubscriptionActions(ctx context.Context, reportStyle *topoapi.KPMReportStyle, cells []*topoapi.E2Cell, granularity int64) ([]e2api.Action, error) {
	// actions list
	actions := make([]e2api.Action, 0)

	// organizes cells by ID
	sort.Slice(cells, func(i, j int) bool {
		return cells[i].CellObjectID < cells[j].CellObjectID
	})

	// for each E2 cell creates an action
	for index, cell := range cells {
		// creates a meas informations list
		measInfoList := &e2smkpmv2.MeasurementInfoList{
			Value: make([]*e2smkpmv2.MeasurementInfoItem, 0),
		}

		// for each measurement in reportStyle.Measurements gets infos
		for _, measurement := range reportStyle.Measurements {
			// gets measurement name
			measTypeMeasName, err := pdubuilder.CreateMeasurementTypeMeasName(measurement.GetName())
			if err != nil {
				return nil, err
			}

			// gets info by name
			measInfoItem, err := pdubuilder.CreateMeasurementInfoItem(measTypeMeasName)
			if err != nil {
				return nil, err
			}

			// adds item info in list
			measInfoList.Value = append(measInfoList.Value, measInfoItem)
		}
		// cell subscription ID
		subID := int64(index + 1)
		actionDefinition, err := pdubuilder.CreateActionDefinitionFormat1(cell.CellObjectID, measInfoList, granularity, subID)
		if err != nil {
			return nil, err
		}

		// creates a new key to subID
		key := actionsstore.NewKey(actionsstore.SubscriptionID{
			SubID: subID,
		})

		// TODO: clean up this store if we delete subscriptions
		_, err = m.actionStore.Put(ctx, key, actionDefinition)
		if err != nil {
			return nil, err
		}

		// // gets a Action Definition format
		// e2smKpmActionDefinition, err := pdubuilder.CreateE2SmKpmActionDefinitionFormat1(reportStyle.Type, actionDefinition)
		// if err != nil {
		// 	return nil, err
		// }

		// // convert Action Definition to []bytes
		// e2smKpmActionDefinitionProto, err := proto.Marshal(e2smKpmActionDefinition)
		// if err != nil {
		// 	return nil, err
		// }

		// // creates an action
		// action := &e2api.Action{
		// 	ID:   int32(index),
		// 	Type: e2api.ActionType_ACTION_TYPE_REPORT,
		// 	SubsequentAction: &e2api.SubsequentAction{
		// 		Type:       e2api.SubsequentActionType_SUBSEQUENT_ACTION_TYPE_CONTINUE,
		// 		TimeToWait: e2api.TimeToWait_TIME_TO_WAIT_ZERO,
		// 	},
		// 	Payload: e2smKpmActionDefinitionProto,
		// }

		// adds action to list
		// actions = append(actions, *action)
	}

	return actions, nil
}
