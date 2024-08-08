package kpmmanager

/*
#include <e2sm/wrapper.h>
#cgo LDFLAGS: -lm -le2smwrapper
#cgo CFLAGS:  -I /usr/local/include/e2sm
*/
import "C"
import (
	"bytes"
	"encoding/binary"
	"fmt"
	"unsafe"
)

// Encode Event Trigger Definition (only format 1 is available on KPM)
func EncodeEventTriggerDefinitionFormat1(reportingPeriod uint64) ([]int64, error) {
	encoded := C.encodeEventTriggerDefinitionFormat1(C.ulong(reportingPeriod))
	defer C.free(unsafe.Pointer(&encoded))

	if encoded.size == 0 {
		return nil, fmt.Errorf("failed to encode EventTriggerDefinition")
	}

	// convert C buffer to Go slice
	goBuffer := C.GoBytes(unsafe.Pointer(&encoded.buffer), C.int(encoded.size))

	var eventTriggerFmt1 []int64
	buffer := bytes.NewBuffer(goBuffer)

	for {
		var val int64
		err := binary.Read(buffer, binary.BigEndian, &val)
		if err != nil {
			break
		}
		eventTriggerFmt1 = append(eventTriggerFmt1, val)
	}

	return eventTriggerFmt1, nil
}
