package subutils

import (
	"github.com/onosproject/onos-e2-sm/servicemodels/e2sm_kpm_v2_go/pdubuilder"
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
