package e2sm

import "google.golang.org/grpc"

type E2sm struct {
	conn *grpc.ClientConn
	Kpm
}

type Kpm struct {
	RanUeKpis       map[string][]string // E2Node ID : Meas
	ReportStyleType int
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
