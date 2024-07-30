package manager

import (
	"sync"

	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
	"github.com/muriloAvlis/USAP/pkg/coredb"
	"github.com/muriloAvlis/USAP/pkg/logging"
)

type UsapXapp struct {
	CoreDBConfig coredb.Config

	WaitForSdl bool
}

var logger xapp.Log = *logging.GetLogger()

func (u *UsapXapp) Consume(msg *xapp.RMRParams) (err error) {
	logger.Info("TODO: Consume UE KPMs")
	return nil
}

func (u *UsapXapp) Run(wg *sync.WaitGroup) {
	defer wg.Done()

	// xapp.SetReadyCB(func(i interface{}) { u.rmrReady = true })

	xapp.RunWithParams(u, u.WaitForSdl)
}
