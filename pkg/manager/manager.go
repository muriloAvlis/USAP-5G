package manager

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"

	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/clientmodel"
	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
	asn1coder "github.com/muriloAvlis/USAP/pkg/ans1coder"
)

func NewManager(c Config) *usapXapp {
	// create a new oranASN1Coder]
	asn1CoderConfig := asn1coder.Config{
		OranAsn1CoderEndpoint: c.OranAsn1CoderEndpoint,
	}

	oranAsn1Coder := asn1coder.NewAsn1Coder(asn1CoderConfig)

	// create a RMR Go channel
	RMRCh := make(chan *xapp.RMRParams)

	return &usapXapp{
		asn1Coder: oranAsn1Coder,
		Config:    c,
		RMR:       RMRCh,
	}
}

// Listen RIC messages and send them to the RMR channel
func (u *usapXapp) Consume(msg *xapp.RMRParams) (err error) {
	msgTypeName := xapp.Rmr.GetRicMessageName(msg.Mtype)

	defer func() {
		xapp.Rmr.Free(msg.Mbuf)
		msg.Mbuf = nil
	}()

	xapp.Logger.Info(fmt.Sprintf("Received RIC message:\n\tType=%s\n\tE2NodeID=%s\n\tSubID=%d\n\tTxID=%s\n\tLength=%d bytes",
		msgTypeName,
		msg.Meid.RanName,
		msg.SubId,
		msg.Xid,
		msg.PayloadLen,
	)) // it's ugly, but it's working...

	// send message to RMR channel to be processed
	u.RMR <- msg
	return nil
}

// Get eNBs list
func (u *usapXapp) geteNBList() ([]*xapp.RNIBNbIdentity, error) {
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
func (u *usapXapp) getgNBList() ([]*xapp.RNIBNbIdentity, error) {
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
func (u *usapXapp) getNbList() []*xapp.RNIBNbIdentity {
	var nodeBs []*xapp.RNIBNbIdentity

	if eNBs, err := u.geteNBList(); err == nil {
		nodeBs = append(nodeBs, eNBs...)
	}

	if gNBs, err := u.getgNBList(); err == nil {
		nodeBs = append(nodeBs, gNBs...)
	}

	return nodeBs
}

// Setup response callback to handle subscription response from SubMgr
func (u *usapXapp) subscriptionCB(resp *clientmodel.SubscriptionResponse) {
	if u.subscriptionId == resp.SubscriptionID {
		u.subscriptionInstances = append(u.subscriptionInstances, resp.SubscriptionInstances...)
	}
}

// Send subscription to E2 Node
func (u *usapXapp) sendSubscription(e2NodeID string) {
	// Create Subscription message and send it to RIC platform
	xapp.Logger.Info("Sending subscription request for E2 Node: %s", e2NodeID)

	// Encode eventTriggerDefinitionFormat1 using C encoder
	evTriggerDefFmt1 := u.asn1Coder.EncodeEventTriggerDefinitionFormat1(reportingPeriod)

	xapp.Logger.Debug("Encoded eventTriggerDefinitionFormat1: %v", evTriggerDefFmt1)

	// Encode actionDefinitionFormat4 using C encoder
	actionDefinitionFormat4 := u.asn1Coder.EncodeActionDefinitionFmt4(ranUeKpis[e2NodeID], granularityPeriod)

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
		ClientEndpoint: &u.ClientEndpoint,
		Meid:           &e2NodeID,
		RANFunctionID:  &KpmRanFuncId,
		SubscriptionDetails: clientmodel.SubscriptionDetailsList{
			&subsDetail,
		},
	}

	// Indent subs parameters (just to print beautifully)
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

// RIC_INDICATION (12050) msg type handler
func (u *usapXapp) handleRicIndication(msg *xapp.RMRParams) {
	xapp.Logger.Debug("RIC Indication Payload: %s", string(msg.Payload)) // just a test
	indMsg, err := u.asn1Coder.DecodeRICIndicationMsg(msg.Payload)

	if err != nil {
		xapp.Logger.Error("Failed to decode RIC indication message: %s", err.Error())
		return
	}

	xapp.Logger.Info("Decoded RIC Indication message from {%s} with successfully!", msg.Meid.RanName)

	// check if Ind Msg Header and Ind Msg has content
	if indMsg.IndHeader == nil || indMsg.IndHeaderLength == 0 || indMsg.IndMessage == nil || indMsg.IndMessageLength == 0 {
		xapp.Logger.Error("Indication message header and indication message are empty!")
		return
	}

	// Decode indication header and message
	xapp.Logger.Debug("Encoded RIC Indication Header: %v", indMsg.IndHeader)
	xapp.Logger.Debug("Encoded RIC Indication Message: %v", indMsg.IndMessage)
}

func (u *usapXapp) controlLoop() {
	// Handle receiving message based on message type
	for {
		// consume message from RMR chan
		msg := <-u.RMR // wait here until receive a message

		msgTypeName := xapp.Rmr.GetRicMessageName(msg.Mtype)
		xapp.Logger.Debug("Handling message type: %s", msgTypeName)

		switch msg.Mtype {
		case xapp.RIC_INDICATION:
			go u.handleRicIndication(msg) // TODO: Is it necessary to control this routine?
		case xapp.RIC_HEALTH_CHECK_REQ:
			xapp.Logger.Info("Received health check request, ignoring...")
		case xapp.A1_POLICY_REQ:
			xapp.Logger.Info("Received policy request, ignoring...")
		default:
			xapp.Logger.Error("Unknow message type %d, discarding...", msg.Mtype)
		}
	}
}

// TODO
func (u *usapXapp) ConfigChangeHandler(f string) {
	xapp.Logger.Info("Config file changed, do something meaningful!")
}

// xApp callback (start here)
func (u *usapXapp) xAppStartCB(d interface{}) {
	xapp.Logger.Info("Starting application callback...")

	nodeBs := u.getNbList()

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
			rfDefActFmtType4 := u.asn1Coder.DecodeMeasNameListbyReportStyle(e2Resp.Gnb.RanFunctions[kpm_idx].RanFunctionDefinition, 4)
			ranUeKpis[nb.GetInventoryName()] = append(ranUeKpis[nb.GetInventoryName()], rfDefActFmtType4...)

			// loop to check if xApp is registered
			for {
				time.Sleep(5 * time.Second)
				if xapp.IsRegistered() {
					xapp.Logger.Info("xApp registration is done, ready to send subscription request")
					break
				}
				xapp.Logger.Debug("xApp registration is not done yet, sleep 5s and check again")
			}

			// print RAN UEs Kpis available by E2 Node
			xapp.Logger.Debug("Available %d UE KPIs on E2 Node %s: %v",
				len(ranUeKpis[nb.GetInventoryName()]),
				nb.GetInventoryName(),
				ranUeKpis[nb.GetInventoryName()])

			// send subscription request
			u.sendSubscription(nb.GetInventoryName())

			// run controlLoop to receive RIC indication messages
			go u.controlLoop() // TODO: Is it necessary to control this routine?

		} else { // disconnected nodeB
			xapp.Logger.Warn("NodeB %s is disconnected!", nb.GetInventoryName())
		}
	}
}

// Application Starting
func (u *usapXapp) Run(wg *sync.WaitGroup) {
	defer wg.Done()

	// set Start callback
	xapp.SetReadyCB(u.xAppStartCB, true)

	// set config change listener
	xapp.AddConfigChangeListener(u.ConfigChangeHandler)

	// set subscription callback
	xapp.Subscription.SetResponseCB(u.subscriptionCB)

	// start xapp
	xapp.RunWithParams(u, u.Config.WaitForSdl)
}
