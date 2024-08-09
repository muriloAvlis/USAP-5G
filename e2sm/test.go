package main

/*
#cgo CFLAGS:  -I /usr/local/include/e2sm
#cgo LDFLAGS: -lm -le2smwrapper
#include <e2sm/wrapper.h>
*/
import "C"
import (
	"errors"
	"fmt"
	"log"
	"unsafe"
)

// Encode Event Trigger Definition (only format 1 is available on KPM)
func EncodeEventTriggerDefinitionFormat1(reportingPeriod uint64) ([]int64, error) {
	encoded := C.encodeEventTriggerDefinitionFormat1(C.u_int64_t(reportingPeriod))
	// Check if buffer is null
	if encoded.buffer == nil {
		return nil, errors.New("failed to encode EventTriggerDefinitionFormat1")
	}

	// free C buffer
	defer C.free(unsafe.Pointer(encoded.buffer))

	// Convert the buffer to Go slice
	bufferSize := int(encoded.size)
	eventTriggerFmt1 := make([]int64, bufferSize)
	for idx, v := range unsafe.Slice(encoded.buffer, encoded.size) {
		eventTriggerFmt1[idx] = int64(v)
	}
	return eventTriggerFmt1, nil
}

func main() {
	res, err := EncodeEventTriggerDefinitionFormat1(10000)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println(res)
}
