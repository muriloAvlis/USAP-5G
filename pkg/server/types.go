package server

import (
	"github.com/muriloAvlis/usap-5g/pkg/e2sm"
	"github.com/muriloAvlis/usap-5g/pkg/pb"
	"google.golang.org/grpc"
)

type UeMetricsServer struct {
	pb.UnimplementedUeMeasIndicationServer
	Server    *grpc.Server
	UEMetrics chan *e2sm.IndicationResponse
}
