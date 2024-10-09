package server

import (
	"fmt"
	"net"

	"github.com/muriloAvlis/usap-5g/usap-xapp/pkg/logger"
	"github.com/muriloAvlis/usap-5g/usap-xapp/pkg/pb"
	"google.golang.org/grpc"
)

var log = logger.GetLogger()

func (s *Server) GetIndicationStream(req *pb.KPMIndicationRequest, stream pb.E2SM_KPM_Service_GetIndicationStreamServer) error {
	log.Infof("Received request: %s", req.SvcName)

	// Infinite flow or until the request stops or an error occurs
	for {
		select {
		case kpmInd := <-s.IndCh:
			// response
			res := &pb.KPMIndicationResponse{
				Latency: uint64(kpmInd.Latency),
				Node: &pb.E2NodeInfos{
					NodebId:      uint32(kpmInd.E2NodeInfos.NodebID),
					NodeTypeName: kpmInd.E2NodeInfos.NodeTypeName,
					Mcc:          uint32(kpmInd.E2NodeInfos.Mcc),
					Mnc:          uint32(kpmInd.E2NodeInfos.Mnc),
					MncDigitLen:  uint32(kpmInd.E2NodeInfos.MncDigitLen),
				},
				Ue: &pb.UEInfos{
					UeId: &pb.UEIDs{
						GnbCuUeF1ApId: uint64(kpmInd.UEInfos.GnbCuUeF1ApId),
						AmfUeNgApId:   kpmInd.UEInfos.AmfUeNgApId,
						Guami: &pb.GuamiT{
							Plmn: &pb.PlmnId{
								Mcc:         uint32(kpmInd.UEInfos.Guami.Plmn.Mcc),
								Mnc:         uint32(kpmInd.UEInfos.Guami.Plmn.Mnc),
								MncDigitLen: uint32(kpmInd.UEInfos.Guami.Plmn.MncDigitLen),
							},
							AmfRegionId: uint32(kpmInd.UEInfos.Guami.AmfRegionId),
							AmfSetId:    uint32(kpmInd.UEInfos.Guami.AmfSetId),
						},
						GnbCuCpUeE1ApId: uint32(kpmInd.UEInfos.GnbCuCpUeE1ApId),
						RanUeId:         kpmInd.RanUeId,
					},
				},
			}

			// check if CU/DU ID is not empty
			if kpmInd.CuDuID != nil {
				res.Node.CuDuId = kpmInd.CuDuID
			}

			// send response
			if err := stream.Send(res); err != nil {
				return fmt.Errorf("error to sending gRPC stream: %v", err)
			}

		case <-stream.Context().Done():
			return stream.Context().Err()
		}
	}
}

func NewManager(config Config) *Server {
	// replace indication channel
	server := &Server{
		IndCh: config.IndCh,
	}

	return server
}

func (s *Server) Run() {
	grpcServer := grpc.NewServer()

	// register services
	pb.RegisterE2SM_KPM_ServiceServer(grpcServer, s)

	// start server
	listen, err := net.Listen("tcp", ":5051")
	if err != nil {
		log.Fatalf("Failed to listen: %s", err.Error())
	}

	log.Infof("Starting gRPC server on port 5051...")

	if err := grpcServer.Serve(listen); err != nil {
		log.Fatalf("Failed to serve: %v", err)
	}
}
