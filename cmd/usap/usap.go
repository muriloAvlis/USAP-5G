package main

import (
	"os"
	"sync"

	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
	"github.com/muriloAvlis/USAP/pkg/coredb"
)

var wg sync.WaitGroup

type appConfig struct {
	coreDBConfig coredb.Config
}

type usapXapp struct {
	waitForSdl bool
}

func (u *usapXapp) Consume(msg *xapp.RMRParams) (err error) {
	// xapp.Logger.Debug("Message received - type=%d len=%d", msg.Mtype, msg.PayloadLen)

	// xapp.SdlStorage.Store("myKey", "payload", msg.Payload)
	// xapp.Rmr.Send(msg, true)
	return nil
}

func (u *usapXapp) Run() {
	defer wg.Done()
	xapp.RunWithParams(u, u.waitForSdl)
}

func main() {
	wg.Add(2)
	app := &usapXapp{
		waitForSdl: xapp.Config.GetBool("db.waitForSdl"),
	}

	go app.Run()

	// Set configurations used by App
	appCfg := appConfig{
		coreDBConfig: coredb.Config{
			CoreDBUser:     os.Getenv("CORE_DB_USER"),
			CoreDBPassword: os.Getenv("CORE_DB_PASSWORD"),
			CoreDBAddress:  os.Getenv("CORE_DB_ADDRESS"),
			CoreDBPort:     os.Getenv("CORE_DB_PORT"),
			CoreDBName:     os.Getenv("CORE_DB_NAME"),
		},
	}

	// Start 5GC DB connection
	coreDBMgr := coredb.NewManager(appCfg.coreDBConfig)

	// Run 5GC DB management
	go coreDBMgr.Run(&wg)

	wg.Wait()
}
