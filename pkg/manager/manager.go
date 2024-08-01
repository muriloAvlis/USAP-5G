package manager

import (
	"encoding/json"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"

	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
)

func (app *UsapXapp) Consume(msg *xapp.RMRParams) (err error) {
	xapp.Logger.Info("TODO: Consume UE KPMs")
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

// Application callback
func (app *UsapXapp) xAppCB(d interface{}) {
	xapp.Logger.Info("Starting application callback...")

	nodeBs := app.getNbList()

	for _, nb := range nodeBs {
		if nb.ConnectionStatus == 1 { // connected nodeB
			xapp.Logger.Info("NodeB %s is connected! Starting KPI extraction...", nb.GetInventoryName())

			// get E2 Node infos from E2 Manager
			e2NodeLink := os.Getenv("E2MGR_HTTP_SERVICE_HOST") + ":" + os.Getenv("E2MGR_HTTP_SERVICE_PORT") + "/v1/nodeb/" + nb.GetInventoryName()
			e2NodeInfo, err := http.Get(e2NodeLink)
			if err != nil {
				xapp.Logger.Error("Failed to get E2 Node informations from E2MGR: %s", err.Error())
				os.Exit(1)
			}
			defer e2NodeInfo.Body.Close()
			var e2Resp E2mgrResponse
			err = json.NewDecoder(e2NodeInfo.Body).Decode(&e2Resp)
			if err != nil {
				xapp.Logger.Error("Failed to decode E2 Node informations from E2MGR: %s", err.Error())
				os.Exit(1)
			}

			// check if E2 Node has RAN function KPM == 2
			rf_idx := 0
			for idx, rf := range e2Resp.Gnb.RanFunctions {
				if rf.RanFunctionId == 2 {
					rf_idx = idx
					break
				}
			}

			for {
				xapp.Logger.Debug("KPM Index: %d", rf_idx)
				time.Sleep(3 * time.Second)
			}

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
