package server

import (
	"log"
	"net"
	"strings"
	"sync"
	"time"

	"gerrit.o-ran-sc.org/r/ric-plt/xapp-frame/pkg/xapp"
	"github.com/muriloAvlis/usap-5g/pkg/e2sm"
	"github.com/muriloAvlis/usap-5g/pkg/pb"
	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
)

func NewServer(address string) *UeMetricsServer {
	lis, err := net.Listen("tcp", address)
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	// create server
	server := grpc.NewServer()
	reflection.Register(server)

	// create UE metrics channel
	ueMetricsCh := make(chan *e2sm.IndicationResponse, 1)

	return &UeMetricsServer{
		Address:   address,
		listener:  lis,
		Server:    server,
		UEMetrics: ueMetricsCh,
		Mtx:       sync.Mutex{},
	}
}

func (s *UeMetricsServer) StreamUeMetrics(req *pb.StreamUeMetricsRequest, stream pb.UeMeasIndication_StreamUeMetricsServer) error {
	xapp.Logger.Debug("Received UE metrics request from client: %s", req.ClientId)

	for {
		select {
		case ind := <-s.UEMetrics:
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
					case *pb.MeasData_ValueInt:
						ueMeasData.MeasValue = &pb.UeMeas_ValueInt{
							ValueInt: measVal.ValueInt,
						}
					case *pb.MeasData_ValueReal:
						ueMeasData.MeasValue = &pb.UeMeas_ValueReal{
							ValueReal: measVal.ValueReal,
						}
					case *pb.MeasData_NoValue:
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
				LatencyMs: ind.Latency,
				UeList:    ueListResponse,
			}

			// send response
			if err := stream.Send(response); err != nil {
				xapp.Logger.Error("Error sending metric: %s", err.Error())
				return err
			}
		case <-time.After(2 * time.Second): // Timeout if not have metrics in 2 seconds
			xapp.Logger.Warn("No UE metrics available at the moment.")

		case <-stream.Context().Done(): // Connection closed by client
			xapp.Logger.Info("Client closed the connection.")
			return nil
		}
	}
}

func (s *UeMetricsServer) StartServer() {
	// Start gRPC server
	pb.RegisterUeMeasIndicationServer(s.Server, s)

	xapp.Logger.Info("Metrics server is running on :%s", strings.Split(s.Address, ":")[1])
	if err := s.Server.Serve(s.listener); err != nil {
		log.Fatalf("Failed to serve: %v", err)
	}
}

func (s *UeMetricsServer) StopServer() {
	// Stop server
	s.Server.Stop()
}
