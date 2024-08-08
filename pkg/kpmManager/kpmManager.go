package kpmmanager

/*
#include <e2sm/wrapper.h>
#cgo LDFLAGS: -lm -le2smwrapper
#cgo CFLAGS:  -I /usr/local/include/e2sm
*/
import "C"
import (
	"errors"
	"unsafe"
)

// Encode Event Trigger Definition (only format 1 is available on KPM)
func EncodeEventTriggerDefinitionFormat1(reportingPeriod uint64) ([]int64, error) {
	encoded := C.encodeEventTriggerDefinitionFormat1(C.u_int64_t(reportingPeriod))
	defer C.free(unsafe.Pointer(&encoded))

	// Check if buffer is null
	if encoded.buffer == nil {
		return nil, errors.New("failed to encode EventTriggerDefinitionFormat1")
	}

	size := int(encoded.size)
	eventTriggerFmt1 := make([]int64, size)
	cBuffer := (*[1 << 30]C.u_int64_t)(unsafe.Pointer(encoded.buffer))[:size:size]

	for i := 0; i < size; i++ {
		eventTriggerFmt1[i] = int64(cBuffer[i])
	}

	return eventTriggerFmt1, nil
}
