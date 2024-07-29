package manager

import (
	"sync"

	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
	"github.com/muriloAvlis/USAP/pkg/coredb"
)

type UsapXapp struct {
	CoreDBConfig coredb.Config

	WaitForSdl bool
}

func (u *UsapXapp) Consume(msg *xapp.RMRParams) (err error) {
	// xapp.Logger.Debug("Message received - type=%d len=%d", msg.Mtype, msg.PayloadLen)

	// xapp.SdlStorage.Store("myKey", "payload", msg.Payload)
	// xapp.Rmr.Send(msg, true)
	return nil
}

func (u *UsapXapp) Run(wg *sync.WaitGroup) {
	defer wg.Done()
	xapp.RunWithParams(u, u.WaitForSdl)
}
