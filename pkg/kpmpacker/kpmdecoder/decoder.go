package kpmdecoder

/*
#cgo LDFLAGS: -lm -le2sm_kpm_decoder
#cgo CFLAGS: -I /usr/local/include/e2sm/kpm_decoder
#include <e2sm/kpm_decoder/wrapper.h>
*/
import "C"
import (
	"fmt"
	"unsafe"
)

// E2SM-KPM spec: 7.4.1 REPORT Service Style Type (1-5)
func DecodeActFmtTypebyReportStyle(ranFunctionDefinition string, ricReportStyle int) []string {
	RfDefCString := C.CString(ranFunctionDefinition)
	defer C.free(unsafe.Pointer(RfDefCString))                  // free buffer
	rfDefActFmtTypes := C.decodeActionFormatTypes(RfDefCString) // get RAN Function definitions from C wrapper

	switch ricReportStyle {
	case 1:
		actionFormatType1 := make([]string, 0, rfDefActFmtTypes.act_fmt_type1_size)
		for _, v := range unsafe.Slice(rfDefActFmtTypes.act_fmt_type1, rfDefActFmtTypes.act_fmt_type1_size) {
			actionFormatType1 = append(actionFormatType1, C.GoString(v))
		}
		return actionFormatType1
	case 2:
		actionFormatType2 := make([]string, 0, rfDefActFmtTypes.act_fmt_type2_size)
		for _, v := range unsafe.Slice(rfDefActFmtTypes.act_fmt_type2, rfDefActFmtTypes.act_fmt_type2_size) {
			actionFormatType2 = append(actionFormatType2, C.GoString(v))
		}
		return actionFormatType2
	case 3:
		actionFormatType3 := make([]string, 0, rfDefActFmtTypes.act_fmt_type3_size)
		for _, v := range unsafe.Slice(rfDefActFmtTypes.act_fmt_type3, rfDefActFmtTypes.act_fmt_type3_size) {
			actionFormatType3 = append(actionFormatType3, C.GoString(v))
		}
		return actionFormatType3
	case 4:
		actionFormatType4 := make([]string, 0, rfDefActFmtTypes.act_fmt_type4_size)
		for _, v := range unsafe.Slice(rfDefActFmtTypes.act_fmt_type4, rfDefActFmtTypes.act_fmt_type4_size) {
			actionFormatType4 = append(actionFormatType4, C.GoString(v))
		}
		return actionFormatType4
	case 5:
		actionFormatType5 := make([]string, 0, rfDefActFmtTypes.act_fmt_type5_size)
		for _, v := range unsafe.Slice(rfDefActFmtTypes.act_fmt_type5, rfDefActFmtTypes.act_fmt_type5_size) {
			actionFormatType5 = append(actionFormatType5, C.GoString(v))
		}
		return actionFormatType5
	default:
		fmt.Println("[WARN] Unknown RAN Fuction Report Style!")
	}

	return nil
}
