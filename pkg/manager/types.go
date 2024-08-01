package manager

import "github.com/muriloAvlis/USAP/pkg/coredb"

type UsapXapp struct {
	CoreDBConfig coredb.Config

	WaitForSdl bool
}

// -------- E2mgr HTTP SVC response -------- //
type E2mgrResponse struct {
	RanName                      string
	ConnectionStatus             string
	GlobalNbId                   GlobalNbId
	NodeType                     string
	Gnb                          Gnb
	AssociatedE2tInstanceAddress string `json:"associatedE2tInstanceAddress,omitempty"`
	SetupFromNetwork             bool
	StatusUpdateTimeStamp        string
}

type GlobalNbId struct {
	PlmnId string
	NbId   string
}

type Gnb struct {
	RanFunctions []RanFunctions
	GnbType      string
	NodeConfigs  []NodeConfigs
}

/*
=> RAN Functions IDs:

	2 ==> SM_KPM
	3 ==> SM_RC

	Others (CCC, NI) ????
*/
type RanFunctions struct {
	RanFunctionId         uint32
	RanFunctionDefinition string
	RanFunctionRevision   uint32
	RanFunctionOid        string
}

type E2nodeComponentInterfaceTypeE1 struct{}
type E2nodeComponentInterfaceTypeXn struct{}
type E2nodeComponentInterfaceTypeF1 struct{}
type E2nodeComponentInterfaceTypeNG struct{}

type NodeConfigs struct {
	E2nodeComponentInterfaceTypeE1 E2nodeComponentInterfaceTypeE1 `json:"e2nodeComponentInterfaceTypeE1,omitempty"`
	E2nodeComponentInterfaceTypeXn E2nodeComponentInterfaceTypeXn `json:"e2nodeComponentInterfaceTypeXn,omitempty"`
	E2nodeComponentInterfaceTypeF1 E2nodeComponentInterfaceTypeF1 `json:"e2nodeComponentInterfaceTypeF1,omitempty"`
	E2nodeComponentInterfaceTypeNG E2nodeComponentInterfaceTypeNG `json:"e2nodeComponentInterfaceTypeNG,omitempty"`
	E2nodeComponentInterfaceType   string
	E2nodeComponentRequestPart     string
	E2nodeComponentResponsePart    string `json:"e2nodeComponentResponsePart,omitempty"`
}
