package asn1coder

/*
#include <stdlib.h>
#include <riclibe2ap/wrapper.h>
#cgo LDFLAGS: -lriclibe2ap
#cgo CFLAGS: -I/usr/local/include/riclibe2ap
*/
import "C"
import (
	"errors"
	"unsafe"
)

func (c *Asn1Coder) DecodeRICIndicationMsg(payload []byte) (*DecodedIndicationMessage, error) {
	buffer := unsafe.Pointer(&payload[0])
	decodedCMsg := C.e2ap_decode_ric_indication_message(buffer, C.size_t(len(payload))) // C decoded result

	if decodedCMsg == nil {
		return &DecodedIndicationMessage{}, errors.New("E2AP library cannot decoded indication message due to wrong or invalid payload")
	}

	defer C.e2ap_free_decoded_ric_indication_message(decodedCMsg)

	decodedMsg := &DecodedIndicationMessage{
		RequestID:             int32(decodedCMsg.requestorID),
		RequestSequenceNumber: int32(decodedCMsg.requestSequenceNumber),
		RanFuncID:             int32(decodedCMsg.ranfunctionID),
		ActionID:              int32(decodedCMsg.actionID),
		IndSN:                 int32(decodedCMsg.indicationSN),
		IndType:               int32(decodedCMsg.indicationType),
		IndHeader:             C.GoBytes(unsafe.Pointer(decodedCMsg.indicationHeader), C.int(decodedCMsg.indicationHeaderSize)),
		IndHeaderLength:       int32(decodedCMsg.indicationHeaderSize),
		IndMessage:            C.GoBytes(unsafe.Pointer(decodedCMsg.indicationMessage), C.int(decodedCMsg.indicationMessageSize)),
		IndMessageLength:      int32(decodedCMsg.indicationMessageSize),
		CallProcessID:         C.GoBytes(unsafe.Pointer(decodedCMsg.callProcessID), C.int(decodedCMsg.callProcessIDSize)),
		CallProcessIDLength:   int32(decodedCMsg.callProcessIDSize),
	} // result

	return decodedMsg, nil
}
