package e2sm

import "google.golang.org/grpc"

type E2sm struct {
	conn *grpc.ClientConn
	Kpm
}

type Kpm struct {
	E2Node          map[string]E2NodeData // E2Node ID : Meas
	ReportStyleType int
}

type E2NodeData struct {
	PlmnId     string
	UeImsiList []string
	RanUeKpis  []string
}

// TestCondInfo struct
type TestCondInfo struct {
	TestType  string      `json:"testType"`
	TestExpr  string      `json:"testExpr"`
	TestValue interface{} `json:"testValue"`
}

// MatchingUEConds
type MatchingUEConds struct {
	TestCondInfo TestCondInfo `json:"testCondInfo"`
}

// type MeasValue struct {
// 	ValueInt   int64
// 	ValueFloat float32
// 	NoValue    bool
// }

type MeasData struct {
	MeasName  string
	MeasValue interface{}
}

type UeData struct {
	UeID              int64
	Imsi              string
	MeasData          []MeasData
	GranularityPeriod int64
}

type IndicationResponse struct {
	Timestamp  int64 // is ms
	IndLatency int64 // in ms
	UeList     []UeData
}
