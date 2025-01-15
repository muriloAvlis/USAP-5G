package manager

import (
	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/clientmodel"
	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
	"github.com/muriloAvlis/usap-5g/pkg/e2sm"
	"github.com/muriloAvlis/usap-5g/pkg/server"
)

var (
	// Default vars
	Host                 = "service-ricxapp-usap-xapp-http.ricxapp"
	HttpPort             = int64(8080)
	RMRPort              = int64(4560)
	XappEventInstanceID  = int64(1234)  // XappEventInstanceID
	ReportingPeriod      = uint64(1000) // in ms
	GranularityPeriod    = uint64(1000) // in ms
	ActionId             = int64(1)     // What is this??
	ActionType           = "report"
	SubsequentActionType = "continue"
	TimeToWait           = "w10ms"
	KPM_RAN_FUNC_ID      = int64(2)
)

type Manager struct {
	Config
	RMR           chan *xapp.RMRParams
	subscriptions []*clientmodel.SubscriptionResponse
	E2sm          *e2sm.E2sm
	Server        *server.UeMetricsServer
}

type Config struct {
	WaitForSdl     bool
	ClientEndpoint clientmodel.SubscriptionParamsClientEndpoint
}
