package server

import (
	"log"
	"net"
	"strings"

	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
	"github.com/muriloAvlis/usap-5g/pkg/pb"
	"google.golang.org/grpc"
)

func (s *UeMetricsServer) StreamUeMetrics(req *pb.StreamUeMetricsRequest, stream pb.UeMeasIndication_StreamUeMetricsServer) error {
	xapp.Logger.Debug("Received UE metrics request from client: %s", req.ClientId)

	// Gera métricas continuamente
	for ind := range s.UEMetrics {
		ueListResponse := make([]*pb.UeList, 0, len(ind.UeList))

		// iterate over UE list
		for _, ueData := range ind.UeList {
			// iterate over UE measurements
			ueMeasList := make([]*pb.UeMeas, 0, len(ueData.MeasData))
			for _, meas := range ueData.MeasData {
				ueMeasData := &pb.UeMeas{}
				ueMeasData.MeasName = meas.MeasName

				// Check meas value type | TODO: exist a better form to do it?
				switch measVal := meas.MeasValue.(type) {
				case *pb.UeMeas_ValueInt:
					ueMeasData.MeasValue = &pb.UeMeas_ValueInt{
						ValueInt: measVal.ValueInt,
					}
				case *pb.UeMeas_ValueFloat:
					ueMeasData.MeasValue = &pb.UeMeas_ValueFloat{
						ValueFloat: measVal.ValueFloat,
					}
				case *pb.UeMeas_NoValue:
					ueMeasData.MeasValue = &pb.UeMeas_NoValue{
						NoValue: measVal.NoValue,
					}
				default:
					log.Fatal("Unknow type in meas value!")
				}

				ueMeasList = append(ueMeasList, ueMeasData)
			}

			ueDataResponse := &pb.UeList{
				UeID:         ueData.UeID,
				UeMeas:       ueMeasList,
				GranulPeriod: ueData.GranularityPeriod,
			}

			ueListResponse = append(ueListResponse, ueDataResponse)
		}

		response := &pb.StreamUeMetricsResponse{
			TimestampMs: float32(ind.Latency),
			UeList:      ueListResponse,
		}

		// send response
		if err := stream.Send(response); err != nil {
			xapp.Logger.Error("Error sending metric: %s", err.Error())
			return err
		}
	}

	return nil
}

func (s *UeMetricsServer) StartServer() {
	// Start gRPC server
	s.Server = grpc.NewServer()
	pb.RegisterUeMeasIndicationServer(s.Server, &UeMetricsServer{})

	address := "0.0.0.0:5051"

	lis, err := net.Listen("tcp", address)
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	xapp.Logger.Info("Metrics server is running on :%s", strings.Split(address, ":")[1])
	if err := s.Server.Serve(lis); err != nil {
		log.Fatalf("Failed to serve: %v", err)
	}
}

func (s *UeMetricsServer) StopServer() {
	// Stop server
	s.Server.Stop()
}
