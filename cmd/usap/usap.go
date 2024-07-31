package main

import (
	"sync"

	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
	"github.com/muriloAvlis/USAP/pkg/coredb"
	"github.com/muriloAvlis/USAP/pkg/logging"
	"github.com/muriloAvlis/USAP/pkg/manager"
)

var wg sync.WaitGroup

func main() {
	wg.Add(2)

	// Set xApp logger configuration
	logging.SetLogger()

	// Set configurations used by xApp
	app := &manager.UsapXapp{
		WaitForSdl: xapp.Config.GetBool("db.waitForSdl"),
		CoreDBConfig: coredb.Config{
			CoreDBUser:     xapp.Config.GetString("coredb.username"),
			CoreDBPassword: xapp.Config.GetString("coredb.password"),
			CoreDBPort:     xapp.Config.GetString("coredb.port"),
			CoreDBName:     xapp.Config.GetString("coredb.dbname"),
		},
	}

	// Get DB IP address
	coreDBAddr, err := coredb.GetDBIpbyHostname(xapp.Config.GetString("coredb.hostname"))
	if err != nil {
		xapp.Logger.Error(err.Error())
	}
	app.CoreDBConfig.CoreDBAddress = coreDBAddr

	// Run xApp
	go app.Run(&wg)

	// Start 5GC DB connection
	coreDBMgr := coredb.NewManager(app.CoreDBConfig)

	// Run 5GC DB management
	go coreDBMgr.Run(&wg)

	wg.Wait()
}
