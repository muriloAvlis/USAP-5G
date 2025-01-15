package e2ap

/*
#include <stdlib.h>
#include <e2ap/wrapper.h>
#cgo LDFLAGS: -le2ap
#cgo CFLAGS: -I/usr/local/include/e2ap
*/
import "C"
import (
	"errors"
	"unsafe"
)

/* RICindication */

func (c *E2ap) DecodeRicIndMsg(payload []byte) (decodedMsg *DecodedIndicationMessage, err error) {
	cptr := unsafe.Pointer(&payload[0])
	decodedMsg = &DecodedIndicationMessage{}
	decodedCMsg := C.e2ap_decode_ric_indication_message(cptr, C.size_t(len(payload)))
	if decodedCMsg == nil {
		return decodedMsg, errors.New("e2ap wrapper is unable to decode indication message due to wrong or invalid payload")
	}
	defer C.e2ap_free_decoded_ric_indication_message(decodedCMsg)

	decodedMsg.RequestID = int32(decodedCMsg.requestorID)
	decodedMsg.RequestSequenceNumber = int32(decodedCMsg.requestSequenceNumber)
	decodedMsg.FuncID = int32(decodedCMsg.ranfunctionID)
	decodedMsg.ActionID = int32(decodedCMsg.actionID)
	decodedMsg.IndSN = int32(decodedCMsg.indicationSN)
	decodedMsg.IndType = int32(decodedCMsg.indicationType)
	indhdr := unsafe.Pointer(decodedCMsg.indicationHeader)
	decodedMsg.IndHeader = C.GoBytes(indhdr, C.int(decodedCMsg.indicationHeaderSize))
	decodedMsg.IndHeaderLength = int32(decodedCMsg.indicationHeaderSize)
	indmsg := unsafe.Pointer(decodedCMsg.indicationMessage)
	decodedMsg.IndMessage = C.GoBytes(indmsg, C.int(decodedCMsg.indicationMessageSize))
	decodedMsg.IndMessageLength = int32(decodedCMsg.indicationMessageSize)
	callproc := unsafe.Pointer(decodedCMsg.callProcessID)
	decodedMsg.CallProcessID = C.GoBytes(callproc, C.int(decodedCMsg.callProcessIDSize))
	decodedMsg.CallProcessIDLength = int32(decodedCMsg.callProcessIDSize)
	return
}
