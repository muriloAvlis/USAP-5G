package e2sm

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/muriloAvlis/usap-5g/pkg/pb"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

func NewClient(address string, port string) *E2sm {
	conn, err := grpc.NewClient(fmt.Sprintf("%s:%s", address, port), grpc.WithTransportCredentials(insecure.NewCredentials()))

	if err != nil {
		log.Fatalf("Failed to connect to server: %s", err.Error())
	}

	return &E2sm{
		conn: conn,
	}
}

func (e *E2sm) EncodeEventTriggerDef(reportingPeriod int64) []int64 {
	client := pb.NewEventTriggerDefinitionClient(e.conn)

	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()

	req := &pb.EncodeEventTriggerRequest{
		ReportingPeriod: reportingPeriod, // Substitua pelo valor desejado
	}

	// Send request
	response, err := client.EncodeEventTriggerDefFormat1(ctx, req)
	if err != nil {
		log.Fatalf("Error while calling EncodeEventTriggerDef: %s", err.Error())
	}

	return response.GetEventTriggerDef()
}

func (e *E2sm) DecodeRanFuncDefinition(ranFuncDefEncoded string) map[string]interface{} {
	// Prepare request
	client := pb.NewRanFunctionDefinitionClient(e.conn)

	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()

	req := &pb.DecodeRanFunctionRequest{
		RanFuncDefinition: ranFuncDefEncoded,
	}

	// Send request
	response, err := client.DecodeRanFunctionDefinition(ctx, req)
	if err != nil {
		log.Fatalf("Error while calling DecodeRanFunctionDefinition: %s", err.Error())
	}

	// Parse JSON response to map
	var ranFuncDefDecoded map[string]interface{}
	err = json.Unmarshal([]byte(response.GetDecodedRanFuncDef()), &ranFuncDefDecoded)
	if err != nil {
		log.Fatalf("Failed to parse decoded response: %s", err.Error())
	}

	return ranFuncDefDecoded
}

func (e *E2sm) EncodeActionDefFormat4(machingUEConds MatchingUEConds, measNameList []string, granularityPeriod int64) []int64 {
	// Prepare request
	client := pb.NewActionDefinitionClient(e.conn)

	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()

	// Check value
	testCondValue := pb.TestCondValue{}

	switch v := machingUEConds.TestCondInfo.TestValue.(type) {
	case int:
		testCondValue.Value = &pb.TestCondValue_ValueInt{ValueInt: int64(v)}
	case int64:
		testCondValue.Value = &pb.TestCondValue_ValueInt{ValueInt: v}
	case bool:
		testCondValue.Value = &pb.TestCondValue_ValueBool{ValueBool: v}
	case string:
		testCondValue.Value = &pb.TestCondValue_ValuePrtS{ValuePrtS: v}
	case []byte:
		testCondValue.Value = &pb.TestCondValue_ValueOctS{ValueOctS: v}
	case float64:
		testCondValue.Value = &pb.TestCondValue_ValueReal{ValueReal: v}
	default:
		log.Fatalf("Unsupported type for testCondValue: %T", v)
	}

	req := &pb.EncodeActDefFormat4Request{
		MatchingUEConds: &pb.MatchingUEConds{
			TestCondInfo: &pb.TestCondInfo{
				TestType:      machingUEConds.TestCondInfo.TestType,
				TestExpr:      machingUEConds.TestCondInfo.TestExpr,
				TestCondValue: &testCondValue,
			},
		},
		MeasNameList:      measNameList,
		GranularityPeriod: granularityPeriod,
	}

	// Send request
	response, err := client.EncodeActionDefinitionFormat4(ctx, req)
	if err != nil {
		log.Fatalf("Error while calling EncodeActionDefinitionFormat4: %s", err.Error())
	}

	return response.GetActionDefinitionEnc()
}

func (e *E2sm) DecodeIndicationMessage(timestamp float64, indicationHeader []byte, indicationMessage []byte) *IndicationResponse {
	// Prepare request
	client := pb.NewIndicationMessageClient(e.conn)

	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()

	req := &pb.DecodeIndMessageRequest{
		Timestamp:         timestamp,
		IndicationHeader:  indicationHeader,
		IndicationMessage: indicationMessage,
	}

	// Send request
	response, err := client.DecodeIndicationMessage(ctx, req)
	if err != nil {
		log.Fatalf("Error while calling DecodeIndicationMessage: %s", err.Error())
	}

	ueList := make([]UeData, 0, len(response.GetUeMeasData()))

	for _, v := range response.GetUeMeasData() {
		measDataList := make([]MeasData, 0, len(v.GetMeasData()))

		for _, measurement := range v.GetMeasData() {
			measDataList = append(measDataList, MeasData{
				MeasName:  measurement.MeasName,
				MeasValue: measurement.MeasValue,
			})
		}

		ueData := UeData{
			UeID:              v.UEID,
			MeasData:          measDataList,
			GranularityPeriod: v.GetGranularityPeriod(),
		}

		ueList = append(ueList, ueData)
	}

	res := &IndicationResponse{
		Timestamp:  timestamp,
		IndLatency: response.LatencyMs,
		UeList:     ueList,
	}

	return res
}

func (e *E2sm) Stop() {
	e.conn.Close()
}
