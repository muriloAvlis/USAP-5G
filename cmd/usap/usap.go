package main

import (
	"os"

	"github.com/muriloAvlis/USAP/pkg/coredb"
)

type appConfig struct {
	coreDBConfig coredb.Config
}

func main() {
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
	coreDBMgr.Run()
}
