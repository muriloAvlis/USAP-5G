package server

import (
	"net"
	"sync"

	"github.com/muriloAvlis/usap-5g/pkg/e2sm"
	"github.com/muriloAvlis/usap-5g/pkg/pb"
	"google.golang.org/grpc"
)

type UeMetricsServer struct {
	pb.UnimplementedUeMeasIndicationServer
	Address   string
	Server    *grpc.Server
	UEMetrics chan *e2sm.IndicationResponse
	listener  net.Listener
	Mtx       sync.Mutex
}
