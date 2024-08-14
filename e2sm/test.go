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

// EncodeActionDefinitionFormat4 chama a função C e converte os resultados
func EncodeActionDefinitionFormat4(metricNames []string, granularityPeriod uint64) ([]int64, error) {
	// Alloc memory to char**
	cArray := C.malloc(C.size_t(len(metricNames)) * C.size_t(unsafe.Sizeof(uintptr(0))))
	cStringArray := (**C.char)(cArray)
	defer C.free(unsafe.Pointer(cStringArray))

	// Slice to free C String pointers
	cStrSlice := make([]*C.char, len(metricNames))

	// Put values in char **
	for i, s := range metricNames {
		cstr := C.CString(s)
		cStrSlice[i] = cstr // storage C string pointers
		// Calcule pointer
		pointer := (**C.char)(unsafe.Pointer(uintptr(cArray) + uintptr(i)*unsafe.Sizeof(uintptr(0))))
		*pointer = cstr
	}

	// Free C strings in the end
	defer func() {
		for _, cstr := range cStrSlice {
			C.free(unsafe.Pointer(cstr))
		}
	}()

	numOfMetrics := len(metricNames)

	// Convert n_of_metrics to size_t
	cNumOfMetrics := C.size_t(numOfMetrics)

	// Call C encoder
	encoded := C.encodeActionDefinitionFormat4(
		cStringArray,
		cNumOfMetrics,
		C.uint64_t(granularityPeriod),
	)

	// Check encode buffer
	if encoded.buffer == nil {
		return nil, fmt.Errorf("failed to encode ActionDefinitionFormat4")
	}
	defer C.free(unsafe.Pointer(encoded.buffer))

	// Convert encoded buffer to Go []int64
	// Convert the buffer to Go slice
	bufferSize := int(encoded.size)
	actionDefFmt4 := make([]int64, bufferSize)
	for idx, v := range unsafe.Slice(encoded.buffer, encoded.size) {
		actionDefFmt4[idx] = int64(v)
	}
	return actionDefFmt4, nil
}

func main() {
	metricNames := []string{
		"CQI",
		"DRB.AirIfDelayUl",
		"DRB.PacketSuccessRateUlgNBUu",
		"DRB.RlcDelayUl",
		"DRB.RlcPacketDropRateDl",
		"DRB.RlcSduDelayDl",
		"DRB.RlcSduTransmittedVolumeDL",
		"DRB.RlcSduTransmittedVolumeUL",
		"DRB.UEThpDl",
		"DRB.UEThpUl",
		"RRU.PrbAvailDl",
		"RRU.PrbAvailUl",
		"RRU.PrbTotDl",
		"RRU.PrbTotUl",
		"RSRP",
		"RSRQ",
	}

	encodedData, err := EncodeActionDefinitionFormat4(metricNames, 1000)

	if err != nil {
		log.Fatal(err)
	}

	// Exiba os resultados
	fmt.Printf("Encoded data size: %d\n", len(encodedData))
	fmt.Printf("Encoded data: %v\n", encodedData)
}
