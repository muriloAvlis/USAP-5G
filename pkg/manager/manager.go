package manager

import (
	"strings"
	"sync"

	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
	"github.com/muriloAvlis/USAP/pkg/coredb"
)

type UsapXapp struct {
	CoreDBConfig coredb.Config

	WaitForSdl bool
}

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
		eNB_names = append(eNB_names, eNB.InventoryName)
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
		gNB_names = append(gNB_names, gNB.InventoryName)
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
			xapp.Logger.Info("NodeB %s is connected! Starting KPI extraction...", nb.InventoryName)
			// TODO
		} else {
			xapp.Logger.Warn("NodeB %s is disconnected!", nb.InventoryName)
		}
	}
}

// Application Starting
func (app *UsapXapp) Run(wg *sync.WaitGroup) {
	defer wg.Done()

	// set logger level
	xapp.Logger.SetLevel(xapp.Config.GetInt("controls.logger.level"))

	xapp.SetReadyCB(app.xAppCB, true)

	xapp.Run(app)
}
