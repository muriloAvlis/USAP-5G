package asn1coder

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/muriloAvlis/USAP/pkg/pb"
)

// O-RAN E2SM-KPM 7.4.1: REPORT Service Style Type (1-5)
func (c *Asn1Coder) DecodeMeasNameListbyReportStyle(ranFunctionDefinition string, ricReportStyle uint32) []string {
	client := pb.NewRanFuncDefDecoderClient(c.client)

	// timeout ctx
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()

	// Request
	request := &pb.MeasListByReportStyleRequest{
		EncodedRanFunctionDefinition: ranFunctionDefinition,
		ReportStyleType:              ricReportStyle,
	}

	// call RPC method
	response, err := client.GetMeasListbyRicReportStyle(ctx, request)
	if err != nil {
		log.Fatalf("Error to call gRPC method: %v", &err)
	}

	return response.MeasList
}

// O-RAN E2SM-KPM 7.3.2 Event Trigger Style 1: Periodic Report (only format 1 is available on KPM)
func (c *Asn1Coder) EncodeEventTriggerDefinitionFormat1(reportingPeriod uint64) []int64 {
	client := pb.NewEventTriggerFmtEncoderClient(c.client)

	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()

	request := &pb.EventTriggerDefFmt1Resquest{
		ReportingPeriod: reportingPeriod,
	}

	// call RPC method
	response, err := client.EncodeEventTriggerFmt1(ctx, request)
	if err != nil {
		log.Fatalf("Error to call gRPC method: %s", err.Error())
	}

	return response.EncodedEventTriggerDefinition
}

// O-RAN E2SM-KPM 7.4.1: Common Condition-based, UE-level Measurement
func (c *Asn1Coder) EncodeActionDefinitionFmt4(measNameList []string, granularityPeriod uint64) []int64 {
	// create a new gRPC connection with oranASN1Coder microservice
	client := pb.NewActDefEncoderClient(c.client)

	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()

	request := &pb.ActDefFmt4Request{
		MeasNameList:      measNameList,
		GranularityPeriod: granularityPeriod,
	}

	// Measure time
	startTime := time.Now()

	// call RPC method
	response, err := client.EncodeActionDefinitionFmt4(ctx, request)
	if err != nil {
		log.Fatalf("Error to call gRPC method: %s", err.Error())
	}

	// Measure time
	duration := time.Since(startTime)

	// Print the time taken
	fmt.Printf("gRPC call took %v\n", duration)

	return response.EncodedActionDefinition
}
