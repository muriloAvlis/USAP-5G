package main

import (
	"log"
	"sync"

	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
	"github.com/muriloAvlis/USAP/pkg/coredb"
	"github.com/muriloAvlis/USAP/pkg/utils"
)

var wg sync.WaitGroup

func main() {
	// Number of App routines
	wg.Add(2)

	// Set configurations used by xApp
	// appConfig := manager.Config{}

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

	// Create a New 5GC Manager (TODO: adapt to Open5GS)
	coreDBMgr := coredb.NewManager(coreDBConfig)

	// Run 5GC DB management
	go coreDBMgr.Run(&wg)

	// Create a New xApp Manager
	// appMgr := manager.NewManager(appConfig)

	// Run xApp
	// go appMgr.Run(&wg)

	wg.Wait()
}
