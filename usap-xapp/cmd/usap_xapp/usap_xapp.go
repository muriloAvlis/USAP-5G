package main

import (
	"os"
	"time"

	"github.com/muriloAvlis/usap-5g/usap-xapp/pkg/logger"
	xapp "github.com/muriloAvlis/usap-5g/usap-xapp/pkg/xapp_sdk"
)

var log = logger.GetLogger()

func main() {
	xapp.Init(xapp.SlToStrVec(os.Args))

	for !xapp.Try_stop() {
		time.Sleep(1 * time.Second)
	}

	log.Info("usap-xapp finish with successfully!")
}
