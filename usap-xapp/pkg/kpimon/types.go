package kpimon

import (
	"os"

	xapp "github.com/muriloAvlis/usap-5g/usap-xapp/pkg/xapp_sdk"
)

//--------------------------------------------------------//
//------------- Transmission Time Intervals -------------//
//------------------------------------------------------//

var ttis = map[int]xapp.Interval{
	1:    xapp.Interval_ms_1,
	2:    xapp.Interval_ms_2,
	5:    xapp.Interval_ms_5,
	10:   xapp.Interval_ms_10,
	100:  xapp.Interval_ms_100,
	1000: xapp.Interval_ms_1000,
}

//-------------------------------------//
//------------- KPM RF ID ------------//
//-----------------------------------//

const KPM_RF_ID uint16 = 2

type Config struct {
	StopSignal chan os.Signal
}

//-----------------------------------//

type Kpimon struct {
	Config
	IndCh chan KPMIndication
}

type KPMHandler struct {
	hdlr []interface{}
	len  int
}

// --------------------------------------------------//
// ------------- KPM Indication Metrics ------------//
// ------------------------------------------------//

type KPMIndication struct {
	Latency int64
	E2NodeInfos
	UEInfos
}

type E2NodeInfos struct {
	NodebID      int
	NodeTypeName string
	Mcc          uint16
	Mnc          uint16
	MncDigitLen  byte
	CuDuID       *uint32 // Optional
}

type UEInfos struct {
	UEIDs
	UEMeasList []UEMeasInfo
}

type UEIDs struct {
	GnbCuUeF1ApId   uint
	AmfUeNgApId     uint64
	Guami           Guami_t
	GnbCuCpUeE1ApId uint
	RanUeId         uint64
}

type Guami_t struct {
	Plmn        PlmnId
	AmfRegionId byte
	AmfSetId    uint16
}

type PlmnId struct {
	Mcc         uint16
	Mnc         uint16
	MncDigitLen byte
}

type UEMeasInfo struct {
	MeasName  string
	MeasValue interface{} // Real or Int
}

//-------------------------------------------------//
