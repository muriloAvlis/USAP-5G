package oaidb

import "database/sql"

// Object to handle coredb functionalities
type coreDB struct {
	dbHdlr *sql.DB
	Config
}

// DB Configs
type Config struct {
	CoreDBUser     string
	CoreDBPassword string
	CoreDBAddress  string
	CoreDBPort     string
	CoreDBName     string
}

// Tables

// -------- AuthenticationSubscription Table -------- //
type AuthenticationSubscriptionData struct {
	Ueid                          string
	AuthenticationMethod          string
	EncPermanentKey               sql.NullString
	ProtectionParameterId         sql.NullString
	SequenceNumber                SequenceNumberData
	AuthenticationManagementField sql.NullString
	AlgorithmId                   sql.NullString
	EncOpcKey                     sql.NullString
	EncTopcKey                    sql.NullString
	VectorGenerationInHss         sql.NullBool
	N5gcAuthMethod                sql.NullString
	RgAuthenticationInd           sql.NullBool
	Supi                          sql.NullString
}

type SequenceNumberData struct {
	Sqn         string          `json:"sqn"`
	SqnScheme   string          `json:"sqnScheme"`
	LastIndexes LastIndexesData `json:"lastIndexes"`
}

type LastIndexesData struct {
	Ausf uint8 `json:"ausf"`
}

// -------- SessionManagementSubscriptionData Table -------- //
type SessionManagementSubscriptionData struct {
	Ueid                            string
	ServingPlmnid                   string
	SingleNssai                     singleNssaiData `json:"singleNssai"`
	DnnConfigurations               dnnConfigurationsData
	InternalGroupIds                sql.NullString
	SharedVnGroupDataIds            sql.NullString
	SharedDnnConfigurationsId       sql.NullString
	OdbPacketServices               sql.NullString
	TraceData                       sql.NullString
	SharedTraceDataId               sql.NullString
	ExpectedUeBehavioursList        sql.NullString
	SuggestedPacketNumDlList        sql.NullString
	ThreegppChargingCharacteristics sql.NullString `sql:"3gppChargingCharacteristics"`
}

type singleNssaiData struct {
	Sst uint8  `json:"sst"`
	Sd  string `json:"sd"`
}

type dnnConfigurationsData map[string]dnnConfigurationsDataValues

type dnnConfigurationsDataValues struct {
	PduSessionTypes pduSessionTypesData    `json:"pduSessionTypes"`
	SscModes        sscModesData           `json:"sscModes"`
	FiveGQosProfile fiveGQosProfileData    `json:"5gQosProfile"`
	SessionAmbr     sessionAmbrData        `json:"sessionAmbr"`
	StaticIpAddress []*staticIpAddressData `json:"staticIpAddress,omitempty"`
}

type pduSessionTypesData struct {
	DefaultSessionType string `json:"defaultSessionType"`
}

type sscModesData struct {
	DefaultSscMode string `json:"defaultSscMode"`
}

type fiveGQosProfileData struct {
	FiveQI        uint8   `json:"5qi"`
	Arp           arpData `json:"arp"`
	PriorityLevel uint16  `json:"priorityLevel"`
}

type arpData struct {
	PriorityLevel uint8  `json:"priorityLevel"` // 1 to 15
	PreemptCap    string `json:"preemptCap"`
	PreemptVuln   string `json:"preemptVuln"`
}

type sessionAmbrData struct {
	Uplink   string `json:"uplink"`
	Downlink string `json:"downlink"`
}

type staticIpAddressData struct {
	Ipv4Addr string `json:"ipv4Addr,omitempty"`
}
