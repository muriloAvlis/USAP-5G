package asn1coder

import "google.golang.org/grpc"

type Asn1Coder struct {
	client *grpc.ClientConn
	Config
}

type Config struct {
	OranAsn1CoderEndpoint
}

type OranAsn1CoderEndpoint struct {
	Ip   string
	Port int
}
