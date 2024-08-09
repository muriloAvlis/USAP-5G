package manager

/*
#cgo LDFLAGS: -L/usr/local/lib -le2smwrapper -lm
#cgo CFLAGS: -I/usr/local/include/e2sm
#include <e2sm/wrapper.h>
*/
import "C"
import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"
	"unsafe"

	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
	"github.com/muriloAvlis/USAP/pkg/kpmpacker"
)

func (app *UsapXapp) Consume(msg *xapp.RMRParams) (err error) {
	id := xapp.Rmr.GetRicMessageName(msg.Mtype)
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

// Encode subscription actions
// func encode_actionsToBeSetup(e2NodeId string) clientmodel.ActionsToBeSetup {
// 	return nil
// }

// Send subscription to E2 Node
func (app *UsapXapp) sendSubscription(e2NodeID string) {
	// Create Subscription message and send it to RIC platform
	xapp.Logger.Info("Sending subscription request for E2 Node: %s", e2NodeID)

	eventTrigger, err := kpmpacker.EncodeEventTriggerDefinitionFormat1(reportingPeriod)
	if err != nil {
		log.Fatal(err)
	}

	xapp.Logger.Debug("Event Trigger Def: %v", eventTrigger)

	// // Set subscription details
	// subsDetail := clientmodel.SubscriptionDetail{
	// 	XappEventInstanceID: &seqId,
	// }

	// Set subscription parameters
	// subscriptionParams := clientmodel.SubscriptionParams{
	// 	ClientEndpoint: &app.ClientEndpoint,
	// 	Meid:           &e2NodeID,
	// 	RANFunctionID:  &KpmRanFuncId,
	// 	SubscriptionDetails: clientmodel.SubscriptionDetailsList{
	// 		&clientmodel.SubscriptionDetail{
	// 			EventTriggers:       clientmodel.EventTriggerDefinition{},
	// 			XappEventInstanceID: &seqId,
	// 			ActionToBeSetupList: encode_actionsToBeSetup(e2NodeID),
	// 		},
	// 	},
	// }
}

// Application callback
func (app *UsapXapp) xAppCB(d interface{}) {
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

			// get KPM RF definition
			RfDefCString := C.CString(e2Resp.Gnb.RanFunctions[kpm_idx].RanFunctionDefinition)
			defer C.free(unsafe.Pointer(RfDefCString))     // free buffer
			rfActDefs := C.buildRanCellUeKpi(RfDefCString) // get RAN Function definitions from C wrapper

			// For E2SM-KPM Action Definition Format 4
			rfActDef4 := make([]string, rfActDefs.act_def_format4_size)

			for _, v := range unsafe.Slice(rfActDefs.act_def_format4, rfActDefs.act_def_format4_size) {
				rfActDef4 = append(rfActDef4, C.GoString(v))
			}

			ranUeKpis[nb.GetInventoryName()] = rfActDef4

			xapp.Logger.Info("Available UE KPIs: %v", ranUeKpis)

			// TODO: prepare variable to receive cell KPIs

			// loop to check if xApp is registered
			for {
				time.Sleep(5 * time.Second)
				if xapp.IsRegistered() {
					xapp.Logger.Info("xApp registration is done, ready to send subscription request")
					break
				}
				xapp.Logger.Debug("xApp registration is not done yet, sleep 5s and check again")
			}

			// send subscription request
			app.sendSubscription(nb.GetInventoryName())

		} else { // disconnected nodeB
			xapp.Logger.Warn("NodeB %s is disconnected!", nb.GetInventoryName())
		}
	}

}

// Application Starting
func (app *UsapXapp) Run(wg *sync.WaitGroup) {
	defer wg.Done()

	xapp.SetReadyCB(app.xAppCB, true)

	xapp.Run(app)
}
