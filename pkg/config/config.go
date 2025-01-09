package config

// Default vars
var (
	Host                 = "service-ricxapp-usap-http.ricxapp"
	HttpPort             = int64(8080)
	RMRPort              = int64(4560)
	KpmRanFuncId         = int64(2)
	XappEventInstanceID  = int64(1234)               // XappEventInstanceID
	RanUeKpis            = make(map[string][]string) // map to [E2NodeID]:[RF_Def_Fmt]
	ReportingPeriod      = uint64(1000)              // in ms
	GranularityPeriod    = uint64(1000)
	ActionId             = int64(1) // What is this??
	ActionType           = "report"
	SubsequentActionType = "continue"
	TimeToWait           = "w10ms"
)
