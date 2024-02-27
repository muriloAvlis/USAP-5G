package main

import (
	"os"
	"os/signal"
	"syscall"

	"github.com/muriloAvlis/qmai/pkg/manager"
	"github.com/onosproject/onos-lib-go/pkg/logging"
)

// initializes package log
var log = logging.GetLogger("qmai")

func main() {
	// defines log level
	log.SetLevel(logging.DebugLevel)

	// initial app message
	log.Info("Starting QoS Manager by Artificial Intelligence (QMAI) xAPP")

	// set manager configuration
	cfg := manager.Config{
		AppID:         "qmai",
		CAPath:        "/etc/qmai/certs/tls.cacrt",
		KeyPath:       "/etc/qmai/certs/tls.key",
		CertPath:      "/etc/qmai/certs/tls.crt",
		E2tEndpoint:   "onos-e2t",
		E2tPort:       5150,
		TopoEndpoint:  "onos-topo",
		TopoPort:      5150,
		UeNibEndpoint: "onos-uenib",
		UeNibPort:     5150,
		ConfigPath:    "/etc/qmai/config/config.json",
		SMName:        "oran-e2sm-kpm",
		SMVersion:     "v2",
	}

	// creates an application manager
	mgr := manager.NewManager(cfg)

	// starts APP manager
	mgr.Run()

	// configures a shutdown signal for xApp
	killSignal := make(chan os.Signal, 1)
	signal.Notify(killSignal, os.Interrupt, syscall.SIGTERM, syscall.SIGINT)
	log.Debug("xApp received a shutdown signal ", <-killSignal)

	// finalizes xApp processes
	mgr.Close()
}
