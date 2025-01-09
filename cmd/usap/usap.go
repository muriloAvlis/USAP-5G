package main

import (
	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/clientmodel"
	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
	"github.com/muriloAvlis/usap-5g/pkg/config"
	"github.com/muriloAvlis/usap-5g/pkg/logger"
	"github.com/muriloAvlis/usap-5g/pkg/manager"
)

func main() {
	// Set logger
	logger.SetLogger()

	// USAP Manager
	mgr := &manager.Manager{
		Config: manager.Config{
			WaitForSdl: true, // dynamic ??
			ClientEndpoint: clientmodel.SubscriptionParamsClientEndpoint{
				Host:     config.Host,
				HTTPPort: &config.HttpPort,
				RMRPort:  &config.RMRPort,
			},
		},
		RMR: make(chan *xapp.RMRParams),
	}

	// Run App Manager
	mgr.Run()
}
