package utils

import (
	xapp "github.com/muriloAvlis/usap-5g/usap-xapp/pkg/xapp_sdk"
)

// Check if E2 Node has support to determined RAN Function ID
func CheckRfByID(RanFunctionList xapp.RANVector, RanFuncID uint16) bool {
	// iterate over supported RFs
	for i := 0; i < int(RanFunctionList.Size()); i++ {
		if RanFunctionList.Get(i).GetId() == RanFuncID {
			return true
		}
	}

	return false
}

func CheckNodeIsMonolitic(ranType int) bool {
	if ranType == Ngran_eNB || ranType == Ngran_ng_eNB || ranType == Ngran_gNB {
		return true
	}

	return false
}

func CheckNodeIsCu(ranType int) bool {
	if ranType == Ngran_eNB_CU || ranType == Ngran_ng_eNB_CU || ranType == Ngran_gNB_CU || ranType == Ngran_gNB_CUCP || ranType == Ngran_gNB_CUUP {
		return true
	}

	return false
}

func CheckNodeIsDu(ranType int) bool {
	if ranType == Ngran_eNB_DU || ranType == Ngran_gNB_DU {
		return true
	}

	return false
}

func CheckNodeIsMbms(ranType int) bool {
	return ranType == Ngran_eNB_MBMS_STA
}
