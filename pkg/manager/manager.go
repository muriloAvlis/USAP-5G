package manager

import (
	"encoding/json"
	"errors"
	"os"
	"os/signal"
	"syscall"
	"time"

	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/clientmodel"
	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
	"github.com/muriloAvlis/usap-5g/pkg/config"
	"github.com/muriloAvlis/usap-5g/pkg/e2ap"
	"github.com/muriloAvlis/usap-5g/pkg/e2sm"
	"github.com/muriloAvlis/usap-5g/pkg/rnib"
)

// Listen RIC messages and send them to the RMR channel
func (m *Manager) Consume(msg *xapp.RMRParams) (err error) {
	id := xapp.Rmr.GetRicMessageName(msg.Mtype)

	defer func() {
		xapp.Rmr.Free(msg.Mbuf)
		msg.Mbuf = nil
	}()

	xapp.Logger.Info("Received RIC message: name=%s | e2NodeID=%s | subID=%d | txID=%s | len=%d",
		id,
		msg.Meid.RanName,
		msg.SubId,
		msg.Xid,
		msg.PayloadLen,
	)
	// send message to RMR channel to be processed
	m.RMR <- msg
	return nil
}

// Setup response callback to handle subscription response from SubMgr
func (m *Manager) subscriptionCB(response *clientmodel.SubscriptionResponse) {
	for _, sub := range m.subscriptions {
		if sub.SubscriptionID == response.SubscriptionID {
			sub.SubscriptionInstances = append(sub.SubscriptionInstances, response.SubscriptionInstances...)
		}
	}
}

// TODO
func (m *Manager) ConfigChangeHandler(f string) {
	xapp.Logger.Info("Config file %s changed, do something meaningful!", f)
}

// Send subscription to E2 Node
func (m *Manager) sendSubscription(e2NodeID string) {
	// Create Subscription message and send it to RIC platform
	xapp.Logger.Info("Sending subscription request for E2 Node: %s", e2NodeID)

	// Encode eventTriggerDefinitionFormat1
	evTriggerDefFmt1 := m.E2sm.EncodeEventTriggerDef(config.GetReportingPeriod())

	//***** Action Definition Format 4 *****//
	var actDefEncoded []int64
	if m.E2sm.ReportStyleType == 4 {
		// Dummy condition that is always satisfied, useful to get IDs of all connected UEs
		// example matching UE condition: ul-rSRP < 1000
		machingUEConds := e2sm.MatchingUEConds{
			TestCondInfo: e2sm.TestCondInfo{
				TestType:  "ul-rSRP",
				TestExpr:  "lessthan",
				TestValue: 1000,
			},
		}

		granularityPeriod := config.GetGranularityPeriod()

		// Only Action Definition Format 4 is available in gRPC API
		actDefEncoded = m.E2sm.EncodeActionDefFormat4(machingUEConds, m.E2sm.RanUeKpis[e2NodeID], granularityPeriod)
	} else {
		xapp.Logger.Error("Unsupported Report Style Type %d", m.E2sm.ReportStyleType)
		return
	}

	// ActionsToBeSetup
	actionToBeSetup := &clientmodel.ActionToBeSetup{
		ActionDefinition: actDefEncoded,
		ActionID:         &ActionId,
		ActionType:       &ActionType,
		SubsequentAction: &clientmodel.SubsequentAction{
			SubsequentActionType: &SubsequentActionType,
			TimeToWait:           &TimeToWait,
		},
	}

	// Set subscription details
	subsDetails := &clientmodel.SubscriptionDetail{
		EventTriggers:       evTriggerDefFmt1,
		XappEventInstanceID: &XappEventInstanceID,
		ActionToBeSetupList: clientmodel.ActionsToBeSetup{
			actionToBeSetup,
		},
	}

	// Set subscription parameters
	subscriptionParams := clientmodel.SubscriptionParams{
		ClientEndpoint: &m.ClientEndpoint,
		Meid:           &e2NodeID,
		RANFunctionID:  &KPM_RAN_FUNC_ID,
		SubscriptionDetails: clientmodel.SubscriptionDetailsList{
			subsDetails,
		},
	}

	// indent subs parameters (just to print beautifully)
	b, err := json.MarshalIndent(subscriptionParams, "", " ")
	if err != nil {
		xapp.Logger.Error("Json marshaling failed: %v", err)
	}

	xapp.Logger.Debug("Subscription parameters to E2 Node %s: %s", e2NodeID, string(b))

	// send subscription
	response, err := xapp.Subscription.Subscribe(&subscriptionParams)

	if err != nil {
		xapp.Logger.Error("Subscription to E2 Node (%s) failed with error: %s", e2NodeID, err)
		return
	}

	m.subscriptions = append(m.subscriptions, &clientmodel.SubscriptionResponse{
		SubscriptionID:        response.SubscriptionID,
		SubscriptionInstances: response.SubscriptionInstances,
	})

	xapp.Logger.Info("Subscription completed successfully for E2 Node %s, subscription ID: %s", e2NodeID, *response.SubscriptionID)
}

func (m *Manager) handleRicIndication(msg *xapp.RMRParams) error {
	var e2ap *e2ap.E2ap

	// Decode Indication Message
	indMsg, err := e2ap.DecodeRicIndMsg(msg.Payload)
	if err != nil {
		xapp.Logger.Error("Failed to decode RIC Indication message: %s", err.Error())
		return nil
	}

	// Check if Indication Message is empty
	if indMsg == nil || indMsg.IndHeader == nil || len(indMsg.IndHeader) == 0 ||
		indMsg.IndMessage == nil || len(indMsg.IndMessage) == 0 {
		return errors.New("unable to get IndicationHeader or IndicationMessage due to invalid size")
	}

	// decode Header and Message
	uesData := m.E2sm.DecodeIndicationMessage(indMsg.IndHeader, indMsg.IndMessage)

	xapp.Logger.Info("Indication latency (ms): %f\n", uesData.Latency)

	// TODO: Update latency
	// uesData.Latency = uesData.Latency

	m.Server.Mtx.Lock()
	defer m.Server.Mtx.Unlock()

	select {
	case m.Server.UEMetrics <- uesData:
		xapp.Logger.Debug("Sending UE metrics to gRPC channel...")
	default:
		xapp.Logger.Warn("Channel buffer full. Dropping UE metrics.")
	}

	return nil
}

func (m *Manager) controlLoop() {
	// Handle receiving message based on message type
	for {
		// consume message from RMR chan
		msg := <-m.RMR // wait here until receive a message
		xapp.Logger.Debug("Received message type: %d", msg.Mtype)
		switch msg.Mtype {
		case xapp.RIC_INDICATION:
			go m.handleRicIndication(msg)
		case xapp.RIC_HEALTH_CHECK_REQ:
			xapp.Logger.Info("Received health check request")
		case xapp.A1_POLICY_REQ:
			xapp.Logger.Info("Received policy request")
		default:
			xapp.Logger.Error("Unknow message type %d, discarding...", msg.Mtype)
		}
	}
}

// xApp Entrypoint
func (m *Manager) xAppStartCB(d interface{}) {
	xapp.Logger.Info("Starting xApp callback...")

	nbs := rnib.GetNbList()

	// Stores KPIs by E2 node ID
	m.E2sm.RanUeKpis = make(map[string][]string)

	// prepare nodeBs data
	for _, nb := range nbs {
		if nb.ConnectionStatus == 1 { // CONNECTED NodeB
			xapp.Logger.Info("E2 node %s is connected! Starting information extraction...", nb.GetInventoryName())

			// Get RAN Function Definition coded from E2 node
			encodedRanFuncDef, err := rnib.GetRanFuncDefiniton(nb.GetInventoryName(), KPM_RAN_FUNC_ID)
			if err != nil {
				xapp.Logger.Error("%s", err.Error())
				continue
			}

			// Decode ranFunctionDefinition
			decodedRanFuncDef := m.E2sm.DecodeRanFuncDefinition(encodedRanFuncDef)

			// Get defined report style in config file
			m.E2sm.ReportStyleType = config.GetReportStyleType()

			// Get meas name list by report style
			measNameList := rnib.GetMeasNameList(decodedRanFuncDef, m.E2sm.ReportStyleType)

			m.E2sm.RanUeKpis[nb.GetInventoryName()] = measNameList

			// loop to check if xApp is registered
			for {
				if xapp.IsRegistered() {
					xapp.Logger.Info("xApp registration is done, ready to send subscription request")
					break
				}
				xapp.Logger.Debug("xApp registration is not done yet, sleep 5s and check again")
				time.Sleep(5 * time.Second)
			}

			// send subscription request
			m.sendSubscription(nb.GetInventoryName())

			// run controlLoop to receive RIC indication messages
			go m.controlLoop() // TODO: Is it necessary to control this routine?

		} else { // DISCONNECTED NodeB
			xapp.Logger.Warn("E2 node %s is disconnected! Ignoring...", nb.GetInventoryName())
		}
	}
}

func (m *Manager) Stop(sig os.Signal) {
	// Delete subscriptions
	xapp.Logger.Debug("Received signal %s, stopping application...", sig)
	for _, sub := range m.subscriptions {
		xapp.Logger.Debug("Removing subscription ID: %s", *sub.SubscriptionID)
		xapp.Subscription.Unsubscribe(*sub.SubscriptionID)
	}

	// Stop gRPC Server
	xapp.Logger.Debug("Stopping gRPC server...")
	m.Server.StopServer()

	// Stop E2sm client
	xapp.Logger.Debug("Stopping gRPC E2SM client...")
	m.E2sm.Stop()
}

// Manager Entrypoint
func (m *Manager) Run() {
	// Signal handler
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, syscall.SIGTERM, syscall.SIGINT)
	go func() {
		sig := <-sigCh
		m.Stop(sig)
	}()

	// set Start callback
	xapp.SetReadyCB(m.xAppStartCB, true)

	// set config change listener
	xapp.AddConfigChangeListener(m.ConfigChangeHandler)

	// set subscription callback
	xapp.Subscription.SetResponseCB(m.subscriptionCB)

	// start gRPC server in Go routine
	go m.Server.StartServer()

	// start xapp
	xapp.RunWithParams(m, m.Config.WaitForSdl)
}
