package manager

import (
	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/clientmodel"
	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
)

var (
	metricsDU = []string{
		"DRB.AirIfDelayUl",
		"DRB.PacketSuccessRateUlgNBUu",
		"DRB.RlcDelayUl",
		"DRB.RlcPacketDropRateDl",
		"DRB.RlcSduDelayDl",
		"DRB.RlcSduTransmittedVolumeDL",
		"DRB.RlcSduTransmittedVolumeUL",
		"DRB.UEThpDl",
		"DRB.UEThpUl",
		"RRU.PrbAvailDl",
		"RRU.PrbAvailUl",
		"RRU.PrbTotDl",
		"RRU.PrbTotUl",
		"RRU.PrbUsedDl",
		"RRU.PrbUsedUl"}

	metricsCU = []string{
		"DRB.PdcpReordDelayUl",
	}
)

type Manager struct {
	Config
	RMR           chan *xapp.RMRParams
	subscriptions []*clientmodel.SubscriptionResponse
}

type Config struct {
	WaitForSdl     bool
	ClientEndpoint clientmodel.SubscriptionParamsClientEndpoint
}
