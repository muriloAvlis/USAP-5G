package main

import (
	"os"

	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/clientmodel"
	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
	"github.com/muriloAvlis/usap-5g/pkg/e2sm"
	"github.com/muriloAvlis/usap-5g/pkg/logger"
	"github.com/muriloAvlis/usap-5g/pkg/manager"
	"github.com/muriloAvlis/usap-5g/pkg/server"
)

func main() {
	// Set logger
	logger.SetLogger()

	// gRPC server
	server := server.NewServer("0.0.0.0:5052")

	// USAP Manager
	mgr := &manager.Manager{
		Config: manager.Config{
			WaitForSdl: true, // dynamic ??
			ClientEndpoint: clientmodel.SubscriptionParamsClientEndpoint{
				Host:     manager.Host,
				HTTPPort: &manager.HttpPort,
				RMRPort:  &manager.RMRPort,
			},
		},
		RMR:    make(chan *xapp.RMRParams),
		E2sm:   e2sm.NewClient(os.Getenv("E2SM_SERVICE_HOST"), os.Getenv("E2SM_SERVICE_PORT")),
		Server: server,
	}

	// Run App Manager
	mgr.Run()
}
