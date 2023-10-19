package monitoring

import e2api "github.com/onosproject/onos-api/go/onos/e2t/e2/v1beta1"

type E2NodeIndication struct {
	NodeID string
	IndMsg e2api.Indication
}
