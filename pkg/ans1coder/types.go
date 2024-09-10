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

/*
* RIC Indication
 */

type DecodedIndicationMessage struct {
	RequestID             int32
	RequestSequenceNumber int32
	RanFuncID             int32
	ActionID              int32
	IndSN                 int32
	IndType               int32
	IndHeader             []byte
	IndHeaderLength       int32
	IndMessage            []byte
	IndMessageLength      int32
	CallProcessID         []byte
	CallProcessIDLength   int32
}
