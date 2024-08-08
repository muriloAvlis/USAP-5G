package kpmmanager

/*
#include <e2sm/wrapper.h>
#cgo LDFLAGS: -lm -le2smwrapper
#cgo CFLAGS:  -I /usr/local/include/e2sm
*/
import "C"
import (
	"fmt"
	"unsafe"
)

// Encode Event Trigger Definition (only format 1 is available on KPM)
func EncodeEventTriggerDefinitionFormat1(reportingPeriod uint64) ([]string, error) {
	encoded := C.encodeEventTriggerDefinitionFormat1(C.ulong(reportingPeriod))
	defer C.free(unsafe.Pointer(&encoded))

	if encoded.size == 0 {
		return nil, fmt.Errorf("failed to encode EventTriggerDefinition")
	}

	eventTriggerFmt1 := make([]string, encoded.size)

	for _, v := range unsafe.Slice(encoded.buffer, encoded.size) {
		eventTriggerFmt1 = append(eventTriggerFmt1, C.GoString(v))
	}

	return eventTriggerFmt1, nil
}
