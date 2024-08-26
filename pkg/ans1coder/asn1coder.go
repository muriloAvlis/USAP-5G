package asn1coder

import (
	"log"
	"strconv"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

// Create a new gRPC connection with oranASN1Coder
func NewAsn1Coder(config Config) *Asn1Coder {
	conn, err := grpc.NewClient(config.Ip+":"+strconv.Itoa(config.Port), grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("Failed to connect to gRPC server: %s", err.Error())
		return nil
	}

	return &Asn1Coder{
		client: conn,
		Config: Config{
			OranAsn1CoderEndpoint{
				Ip:   config.Ip,
				Port: config.Port,
			},
		},
	}
}

// TODO: How call this?
func (c *Asn1Coder) Stop() {
	c.client.Close()
}
