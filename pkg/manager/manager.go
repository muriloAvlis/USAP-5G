package manager

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"

	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/clientmodel"
	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
	"github.com/muriloAvlis/USAP/pkg/kpmpacker"
)

// Listen RIC messages and send them to the RMR channel
func (app *UsapXapp) Consume(msg *xapp.RMRParams) (err error) {
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
	app.RMR <- msg
	return nil
}

// Get eNBs list
func (app *UsapXapp) geteNBList() ([]*xapp.RNIBNbIdentity, error) {
	eNBs, err := xapp.Rnib.GetListEnbIds()
	if err != nil {
		xapp.Logger.Error("Unable to get eNodeB list: %s", err.Error())
		return nil, err
	}

	var eNB_names []string
	for _, eNB := range eNBs {
		eNB_names = append(eNB_names, eNB.GetInventoryName())
	}

	xapp.Logger.Info("List of connected eNodeBs: [%s]", strings.Join(eNB_names, ", "))

	return eNBs, nil
}

// Get gNBs list
func (app *UsapXapp) getgNBList() ([]*xapp.RNIBNbIdentity, error) {
	gNBs, err := xapp.Rnib.GetListGnbIds()
	if err != nil {
		xapp.Logger.Error("Unable to get gNodeB list: %s", err.Error())
		return nil, err
	}

	var gNB_names []string
	for _, gNB := range gNBs {
		gNB_names = append(gNB_names, gNB.GetInventoryName())
	}

	xapp.Logger.Info("List of connected gNodeBs: [%s]", strings.Join(gNB_names, ", "))

	return gNBs, nil
}

// Get gNB and eNB list connected to RIC
func (app *UsapXapp) getNbList() []*xapp.RNIBNbIdentity {
	var nodeBs []*xapp.RNIBNbIdentity

	if eNBs, err := app.geteNBList(); err == nil {
		nodeBs = append(nodeBs, eNBs...)
	}

	if gNBs, err := app.getgNBList(); err == nil {
		nodeBs = append(nodeBs, gNBs...)
	}

	return nodeBs
}

// Setup response callback to handle subscription response from SubMgr
func (app *UsapXapp) subscriptionCB(resp *clientmodel.SubscriptionResponse) {
	if app.subscriptionId == resp.SubscriptionID {
		app.subscriptionInstances = append(app.subscriptionInstances, resp.SubscriptionInstances...)
	}
}

// Send subscription to E2 Node
func (app *UsapXapp) sendSubscription(e2NodeID string) {
	// Create Subscription message and send it to RIC platform
	xapp.Logger.Info("Sending subscription request for E2 Node: %s", e2NodeID)

	// Encode eventTriggerDefinitionFormat1 using C encoder
	evTriggerDefFmt1, err := kpmpacker.EncodeEventTriggerDefinitionFormat1(reportingPeriod)
	if err != nil {
		log.Fatal(err) // critical process
	}

	xapp.Logger.Debug("Encoded eventTriggerDefinitionFormat1: %v", evTriggerDefFmt1)

	// Encode actionDefinitionFormat4 using C encoder
	actionDefinitionFormat4, err := kpmpacker.EncodeActionDefinitionFormat4(ranUeKpis[e2NodeID], granularityPeriod)
	if err != nil {
		log.Fatal(err) // critical process
	}

	xapp.Logger.Debug("Encoded actionDefinitionFormat4: %v", actionDefinitionFormat4)

	// Set actionToBeSetup
	actionToBeSetup := &clientmodel.ActionToBeSetup{
		ActionID:         &actionId,
		ActionDefinition: actionDefinitionFormat4,
		ActionType:       &actionType,
		SubsequentAction: &clientmodel.SubsequentAction{
			SubsequentActionType: &subsequentActionType,
			TimeToWait:           &timeToWait,
		},
	}

	// Set subscription details
	subsDetail := clientmodel.SubscriptionDetail{
		ActionToBeSetupList: clientmodel.ActionsToBeSetup{
			actionToBeSetup,
		},
		EventTriggers:       evTriggerDefFmt1,
		XappEventInstanceID: &seqId,
	}

	xapp.Logger.Debug("Subscription detail to E2 Node %s: %v", e2NodeID, subsDetail)

	// Set subscription parameters
	subscriptionParams := clientmodel.SubscriptionParams{
		ClientEndpoint: &app.ClientEndpoint,
		Meid:           &e2NodeID,
		RANFunctionID:  &KpmRanFuncId,
		SubscriptionDetails: clientmodel.SubscriptionDetailsList{
			&subsDetail,
		},
	}

	// indent subs parameters (just to print beautifully)
	b, err := json.MarshalIndent(subscriptionParams, "", " ")
	if err != nil {
		xapp.Logger.Error("Json marshaling failed: %v", err)
	}

	xapp.Logger.Debug("Subscription parameters to E2 Node %s: %s", e2NodeID, string(b))

	// send subscription
	resp, err := xapp.Subscription.Subscribe(&subscriptionParams)
	if err != nil {
		xapp.Logger.Error("Subscription to E2 Node (%s) failed with error: %s", e2NodeID, err)
		return
	}

	xapp.Logger.Info("Subscription completed successfully for E2 Node %s, subscription ID: %s", e2NodeID, *resp.SubscriptionID)
}

// TODO
func (app *UsapXapp) handleRicIndication(msg *xapp.RMRParams) {
	xapp.Logger.Debug("Everything Already until here :) %v", msg.Meid)
}

func (app *UsapXapp) controlLoop() {
	// Handle receiving message based on message type
	for {
		// consume message from RMR chan
		msg := <-app.RMR // wait here until receive a message
		xapp.Logger.Debug("Received message type: %d", msg.Mtype)
		switch msg.Mtype {
		case xapp.RIC_INDICATION:
			go app.handleRicIndication(msg) // TODO: Is it necessary to control this routine?
		case xapp.RIC_HEALTH_CHECK_REQ:
			xapp.Logger.Info("Received health check request")
		case xapp.A1_POLICY_REQ:
			xapp.Logger.Info("Received policy request")
		default:
			xapp.Logger.Error("Unknow message type %d, discarding...", msg.Mtype)
		}
	}
}

// TODO
func (u *UsapXapp) ConfigChangeHandler(f string) {
	xapp.Logger.Info("Config file changed, do something meaningful!")
}

// xApp callback (start here)
func (app *UsapXapp) xAppStartCB(d interface{}) {
	xapp.Logger.Info("Starting application callback...")

	nodeBs := app.getNbList()

	// prepare nodeBs data
	for _, nb := range nodeBs {
		if nb.ConnectionStatus == 1 { // connected nodeB
			xapp.Logger.Info("NodeB %s is connected! Starting KPI extraction...", nb.GetInventoryName())

			// get E2 Node infos from E2 Manager
			e2NodeLink := "http://" + os.Getenv("E2MGR_HTTP_SERVICE_HOST") + ":" + os.Getenv("E2MGR_HTTP_SERVICE_PORT") + "/v1/nodeb/" + nb.GetInventoryName()
			e2NodeInfo, err := http.Get(e2NodeLink)
			if err != nil {
				xapp.Logger.Error("Failed to get E2 Node informations from E2MGR: %s", err.Error())
				continue
			}
			defer e2NodeInfo.Body.Close()
			var e2Resp E2mgrResponse
			err = json.NewDecoder(e2NodeInfo.Body).Decode(&e2Resp)
			if err != nil {
				xapp.Logger.Error("Failed to decode E2 Node informations from E2MGR: %s", err.Error())
				continue
			}

			// check if E2 Node has KPM RAN function == 2
			kpm_idx := -1
			for idx, rf := range e2Resp.Gnb.RanFunctions {
				if rf.RanFunctionId == 2 {
					kpm_idx = idx
					xapp.Logger.Debug("NodeB %s has KPM RF index: %d", nb.GetInventoryName(), kpm_idx)
					break
				}
			}

			if kpm_idx == -1 {
				xapp.Logger.Debug("NodeB %s does not have KPM RF, finalizing KPI extraction process...", nb.GetInventoryName())
				continue
			}

			// decode KPM RF definition Action Format Type 4
			rfDefActFmtType4 := kpmpacker.DecodeActFmtTypebyReportStyle(e2Resp.Gnb.RanFunctions[kpm_idx].RanFunctionDefinition, 4)
			ranUeKpis[nb.GetInventoryName()] = append(ranUeKpis[nb.GetInventoryName()], rfDefActFmtType4...)

			// loop to check if xApp is registered
			for {
				time.Sleep(5 * time.Second)
				if xapp.IsRegistered() {
					xapp.Logger.Info("xApp registration is done, ready to send subscription request")
					break
				}
				xapp.Logger.Debug("xApp registration is not done yet, sleep 10s and check again")
			}

			// print RAN UEs Kpis available by E2 Node
			xapp.Logger.Debug("Available %d UE KPIs on E2 Node %s: %v",
				len(ranUeKpis[nb.GetInventoryName()]),
				nb.GetInventoryName(),
				ranUeKpis[nb.GetInventoryName()])

			// send subscription request
			app.sendSubscription(nb.GetInventoryName())

			// run controlLoop to receive RIC indication messages
			go app.controlLoop() // TODO: Is it necessary to control this routine?

		} else { // disconnected nodeB
			xapp.Logger.Warn("NodeB %s is disconnected!", nb.GetInventoryName())
		}
	}
}

// Application Starting
func (app *UsapXapp) Run(wg *sync.WaitGroup) {
	defer wg.Done()

	// set Start callback
	xapp.SetReadyCB(app.xAppStartCB, true)

	// set config change listener
	xapp.AddConfigChangeListener(app.ConfigChangeHandler)

	// set subscription callback
	xapp.Subscription.SetResponseCB(app.subscriptionCB)

	// start xapp
	xapp.RunWithParams(app, app.Config.WaitForSdl)
}
