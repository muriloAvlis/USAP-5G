package server

import (
	"github.com/muriloAvlis/usap-5g/usap-xapp/pkg/kpimon"
	"github.com/muriloAvlis/usap-5g/usap-xapp/pkg/pb"
)

type Server struct {
	pb.UnimplementedE2SM_KPM_ServiceServer
	IndCh chan kpimon.KPMIndication
}

type Config struct {
	IndCh chan kpimon.KPMIndication
}
