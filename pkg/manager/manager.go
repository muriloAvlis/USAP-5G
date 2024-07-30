package manager

import (
	"fmt"
	"sync"

	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
	"github.com/muriloAvlis/USAP/pkg/coredb"
)

type UsapXapp struct {
	CoreDBConfig coredb.Config

	WaitForSdl bool
}

func (u *UsapXapp) Consume(msg *xapp.RMRParams) (err error) {
	fmt.Println("TODO: Consume UE KPMs")
	return nil
}

func (u *UsapXapp) Run(wg *sync.WaitGroup) {
	defer wg.Done()
	// Set MDC (read: name visible in the logs)
	xapp.Logger.SetMdc("VERSION", "v1.0.0-alpha")

	// xapp.SetReadyCB(func(i interface{}) { u.rmrReady = true })

	xapp.RunWithParams(u, u.WaitForSdl)
}
