package monitoring

import (
	"context"

	e2api "github.com/onosproject/onos-api/go/onos/e2t/e2/v1beta1"
	topoapi "github.com/onosproject/onos-api/go/onos/topo"
	e2smkpmv2 "github.com/onosproject/onos-e2-sm/servicemodels/e2sm_kpm_v2_go/v2/e2sm-kpm-v2-go"
	"github.com/onosproject/onos-kpimon/pkg/broker"
	"github.com/onosproject/onos-lib-go/pkg/logging"
	"google.golang.org/protobuf/proto"
)

type Monitor struct {
	streamReader broker.StreamReader
	nodeID       topoapi.ID
	indChan      chan *E2NodeIndication
}

var log = logging.GetLogger("qmai", "monitoring")

func NewMonitor(streamReader broker.StreamReader, nodeID topoapi.ID, indChan chan *E2NodeIndication) *Monitor {
	return &Monitor{
		streamReader: streamReader,
		nodeID:       nodeID,
		indChan:      indChan,
	}
}

func (m *Monitor) Start(ctx context.Context) error {
	errCh := make(chan error)
	go func() {
		for {
			indMsg, err := m.streamReader.Recv(ctx)
			if err != nil {
				log.Errorf("Error reading indication stream, chanID:%v, streamID:%v, err:%v", m.streamReader.ChannelID(), m.streamReader.StreamID(), err)
				errCh <- err
			}
			err = m.processIndication(ctx, indMsg, m.nodeID)
			if err != nil {
				log.Errorf("Error processing indication, err:%v", err)
				errCh <- err
			}
		}
	}()

	select {
	case ind := <-m.indChan:
		indMessage := e2smkpmv2.E2SmKpmIndicationMessage{}
		err := proto.Unmarshal(ind.IndMsg.Payload, &indMessage)
		if err != nil {
			return err
		}
		indMsg := indMessage.String()
		log.Debugf("E2 Node: %s, Pkg Payload: %v", ind.NodeID, indMsg)
		return nil
	case err := <-errCh:
		return err
	case <-ctx.Done():
		return ctx.Err()
	}
}

func (m *Monitor) processIndication(ctx context.Context, indication e2api.Indication, nodeID topoapi.ID) error {
	m.indChan <- &E2NodeIndication{
		NodeID: string(nodeID),
		IndMsg: e2api.Indication{
			Header:  indication.Header,
			Payload: indication.Payload,
		},
	}
	return nil
}
