package manager

import (
	"encoding/json"
	"os"
	"os/signal"
	"syscall"
	"time"

	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/clientmodel"
	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
	"github.com/muriloAvlis/usap-5g/pkg/config"
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
	evTriggerDefFmt1 := []int64{8, 3, 231} // 1000 ms

	// Action Definition
	var actDefFmt4 []int64

	if e2NodeID == "gnb_001_001_00019b" { // CU Node
		actDefFmt4 = []int64{0, 1, 4, 128, 43, 0, 0, 0, 56, 0, 1, 0, 32, 2, 3, 232, 0, 0, 0, 1, 48, 68, 82, 66, 46, 80, 100, 99, 112, 82, 101, 111, 114, 100, 68, 101, 108, 97, 121, 85, 108, 1, 32, 0, 0, 64, 3, 231}
	} else { // DU Node
		actDefFmt4 = []int64{0, 1, 4, 128, 129, 107, 0, 0, 0, 56, 0, 1, 0, 32, 2, 3, 232, 0, 0, 14, 0, 240, 68, 82, 66, 46, 65, 105, 114, 73, 102, 68, 101, 108, 97, 121, 85, 108, 1, 32, 0, 0, 1, 176, 68, 82, 66, 46, 80, 97, 99, 107, 101, 116, 83, 117, 99, 99, 101, 115, 115, 82, 97, 116, 101, 85, 108, 103, 78, 66, 85, 117, 1, 32, 0, 0, 0, 208, 68, 82, 66, 46, 82, 108, 99, 68, 101, 108, 97, 121, 85, 108, 1, 32, 0, 0, 1, 96, 68, 82, 66, 46, 82, 108, 99, 80, 97, 99, 107, 101, 116, 68, 114, 111, 112, 82, 97, 116, 101, 68, 108, 1, 32, 0, 0, 1, 0, 68, 82, 66, 46, 82, 108, 99, 83, 100, 117, 68, 101, 108, 97, 121, 68, 108, 1, 32, 0, 0, 1, 192, 68, 82, 66, 46, 82, 108, 99, 83, 100, 117, 84, 114, 97, 110, 115, 109, 105, 116, 116, 101, 100, 86, 111, 108, 117, 109, 101, 68, 76, 1, 32, 0, 0, 1, 192, 68, 82, 66, 46, 82, 108, 99, 83, 100, 117, 84, 114, 97, 110, 115, 109, 105, 116, 116, 101, 100, 86, 111, 108, 117, 109, 101, 85, 76, 1, 32, 0, 0, 0, 160, 68, 82, 66, 46, 85, 69, 84, 104, 112, 68, 108, 1, 32, 0, 0, 0, 160, 68, 82, 66, 46, 85, 69, 84, 104, 112, 85, 108, 1, 32, 0, 0, 0, 208, 82, 82, 85, 46, 80, 114, 98, 65, 118, 97, 105, 108, 68, 108, 1, 32, 0, 0, 0, 208, 82, 82, 85, 46, 80, 114, 98, 65, 118, 97, 105, 108, 85, 108, 1, 32, 0, 0, 0, 176, 82, 82, 85, 46, 80, 114, 98, 84, 111, 116, 68, 108, 1, 32, 0, 0, 0, 176, 82, 82, 85, 46, 80, 114, 98, 84, 111, 116, 85, 108, 1, 32, 0, 0, 0, 192, 82, 82, 85, 46, 80, 114, 98, 85, 115, 101, 100, 68, 108, 1, 32, 0, 0, 0, 192, 82, 82, 85, 46, 80, 114, 98, 85, 115, 101, 100, 85, 108, 1, 32, 0, 0, 64, 3, 231}
	}

	// ActionsToBeSetup
	actionToBeSetup := &clientmodel.ActionToBeSetup{
		ActionDefinition: actDefFmt4,
		ActionID:         &config.ActionId,
		ActionType:       &config.ActionType,
		SubsequentAction: &clientmodel.SubsequentAction{
			SubsequentActionType: &config.SubsequentActionType,
			TimeToWait:           &config.TimeToWait,
		},
	}

	// Set subscription details
	subsDetails := &clientmodel.SubscriptionDetail{
		EventTriggers:       evTriggerDefFmt1,
		XappEventInstanceID: &config.XappEventInstanceID,
		ActionToBeSetupList: clientmodel.ActionsToBeSetup{
			actionToBeSetup,
		},
	}

	// Set subscription parameters
	subscriptionParams := clientmodel.SubscriptionParams{
		ClientEndpoint: &m.ClientEndpoint,
		Meid:           &e2NodeID,
		RANFunctionID:  &config.KpmRanFuncId,
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

func (m *Manager) controlLoop() {
	// Handle receiving message based on message type
	for {
		// consume message from RMR chan
		msg := <-m.RMR // wait here until receive a message
		xapp.Logger.Debug("Received message type: %d", msg.Mtype)
		switch msg.Mtype {
		case xapp.RIC_INDICATION:
			xapp.Logger.Debug("Received RIC Indication!")
			// go m.handleRicIndication(msg) // TODO: Is it necessary to control this routine?
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

	// prepare nodeBs data
	for _, nb := range nbs {
		if nb.ConnectionStatus == 1 { // CONNECTED NodeB
			xapp.Logger.Info("E2 node %s is connected! Starting information extraction...", nb.GetInventoryName())

			// Get RAN Function Definition coded from E2 node
			_, err := rnib.GetRanFuncDefiniton(nb.GetInventoryName(), config.KpmRanFuncId)
			if err != nil {
				xapp.Logger.Error("%s", err.Error())
				continue
			}

			// CU Node
			if nb.GetInventoryName() == "gnb_001_001_00019b" {
				config.RanUeKpis[nb.InventoryName] = append(config.RanUeKpis[nb.InventoryName], metricsCU...)
			} else {
				config.RanUeKpis[nb.InventoryName] = append(config.RanUeKpis[nb.InventoryName], metricsDU...)
			}

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
			xapp.Logger.Warn("E2 node %s is disconnected!", nb.GetInventoryName())
		}
	}
}

// TODO
func (m *Manager) Stop(sig os.Signal) {
	xapp.Logger.Debug("Received signal %s, stopping application...", sig)
	for _, sub := range m.subscriptions {
		xapp.Logger.Debug("Removing subscription ID: %s", *sub.SubscriptionID)
		xapp.Subscription.Unsubscribe(*sub.SubscriptionID)
	}
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

	// start xapp
	xapp.RunWithParams(m, m.Config.WaitForSdl)
}
