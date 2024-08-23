package main

import (
	"log"
	"sync"

	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/clientmodel"
	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
	asn1coder "github.com/muriloAvlis/USAP/pkg/ans1coder"
	"github.com/muriloAvlis/USAP/pkg/coredb"
	"github.com/muriloAvlis/USAP/pkg/logging"
	"github.com/muriloAvlis/USAP/pkg/manager"
	"github.com/muriloAvlis/USAP/pkg/utils"
)

var wg sync.WaitGroup

func main() {
	// Number of App routines
	wg.Add(2)

	// Set xApp logger configuration
	logging.SetLogger()

	// Set configurations used by xApp
	appConfig := manager.Config{
		WaitForSdl: xapp.Config.GetBool("db.waitForSdl"),
		ClientEndpoint: clientmodel.SubscriptionParamsClientEndpoint{
			Host:     "service-ricxapp-usap-http.ricxapp",
			HTTPPort: &manager.HttpPort,
			RMRPort:  &manager.RMRPort,
		},
		OranAsn1CoderEndpoint: asn1coder.OranAsn1CoderEndpoint{
			Port: xapp.Config.GetInt("oranASN1Coder.grpcPort"),
		},
	}

	// Set configuration to connect to 5GC
	coreDBConfig := coredb.Config{
		CoreDBUser:     xapp.Config.GetString("coredb.username"),
		CoreDBPassword: xapp.Config.GetString("coredb.password"),
		CoreDBPort:     xapp.Config.GetString("coredb.port"),
		CoreDBName:     xapp.Config.GetString("coredb.dbname"),
	}

	// Get DB IP address
	coreDBAddr, err := utils.GetIpbyHostname(xapp.Config.GetString("coredb.hostname"))
	if err != nil {
		log.Fatal(err.Error()) // critical application process
	}
	coreDBConfig.CoreDBAddress = coreDBAddr

	// Get usap-oranASN1Coder IP address
	asn1CoderAddr, err := utils.GetIpbyHostname(xapp.Config.GetString("oranASN1Coder.grpcServerService"))
	if err != nil {
		log.Fatal(err.Error()) // critical application process
	}
	appConfig.OranAsn1CoderEndpoint.Ip = asn1CoderAddr

	// Create a New xApp Manager
	appMgr := manager.NewManager(appConfig)

	// Run xApp
	go appMgr.Run(&wg)

	// Create a New 5GC Manager
	coreDBMgr := coredb.NewManager(coreDBConfig)

	// Run 5GC DB management
	go coreDBMgr.Run(&wg)

	wg.Wait()
}
