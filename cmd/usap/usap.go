package main

import (
	"os"
	"sync"

	"github.com/muriloAvlis/usap-5g/pkg/coredb"
	"github.com/muriloAvlis/usap-5g/pkg/logger"
	"github.com/muriloAvlis/usap-5g/pkg/utils"
)

var wg sync.WaitGroup

func main() {
	// Initialize log
	log := logger.GetLogger()
	defer logger.Sync()
	log.Info("Starting USAP Application...")

	// Set number of App routines
	wg.Add(2)

	// Set configurations used by xApp
	// appConfig := manager.Config{}

	// Set configuration to connect to 5GC
	coreDBConfig := coredb.Config{
		CoreDBUser:     os.Getenv("CORE_DB_USER"),
		CoreDBPassword: os.Getenv("CORE_DB_PASSWORD"),
		CoreDBPort:     os.Getenv("CORE_DB_PORT"),
		CoreDBName:     os.Getenv("CORE_DB_NAME"),
	}

	// Get DB IP address
	coreDBAddr, err := utils.GetIpbyHostname(os.Getenv("CORE_DB_HOSTNAME"))
	if err != nil {
		log.Fatal(err.Error()) // critical application process
	}
	coreDBConfig.CoreDBAddress = coreDBAddr

	// Create a New 5GC Manager (TODO: adapt to Open5GS)
	coreDBMgr := coredb.NewManager(coreDBConfig)

	// Run 5GC DB management
	log.Info("Starting 5GC connection...")
	go coreDBMgr.Run(&wg)

	// Create a New xApp Manager
	// appMgr := manager.NewManager(appConfig)

	// Run xApp
	// go appMgr.Run(&wg)

	wg.Wait()
}
