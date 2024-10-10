package kpimon

import (
	"os"
	"strings"
	"time"

	"github.com/muriloAvlis/usap-5g/usap-xapp/pkg/logger"
	"github.com/muriloAvlis/usap-5g/usap-xapp/pkg/utils"
	xapp "github.com/muriloAvlis/usap-5g/usap-xapp/pkg/xapp_sdk"
)

var log = logger.GetLogger()

func NewManager(config Config) *Kpimon {
	// creates a KPM Ind chan (without buffer)
	indCh := make(chan KPMIndication, 1)

	return &Kpimon{
		Config: config,
		IndCh:  indCh,
	}
}

func (k *Kpimon) Run() {
	xapp.Init(xapp.SlToStrVec(os.Args))

	// get O-RAN SMs from config
	oranSm := xapp.Get_oran_sm_conf()

	// get E2 nodes
	nodes := xapp.Conn_e2_nodes()
	if nodes.Size() <= 0 {
		log.Info("No connected E2 node, finalizing the xApp...")
		return
	}

	kpmHdlr := KPMHandler{}

	for i := 0; i < int(nodes.Size()); i++ {
		e2node := nodes.Get(i)
		for j := 0; j < int(oranSm.Size()); j++ {
			smInfo := oranSm.Get(j) // from config
			smName := smInfo.GetName()

			switch smName {
			case "KPM":
				// check if E2 node has support to E2SM-KPM
				if !utils.CheckRfByID(e2node.GetRan_func(), KPM_RF_ID) {
					log.Warnf("E2 Node %d doesn't support to E2SM-KPM!", e2node.GetId().GetNb_id().GetNb_id())
					continue
				}

				smTime := smInfo.GetTime()
				tti := getOranTTI(smTime)
				cfgRanType := smInfo.GetRan_type()
				actions := smInfo.GetActions()

				// prepare meas name list
				measNameList := make([]string, 0, actions.Size())
				for k := 0; k < int(actions.Size()); k++ {
					actId := actions.Get(k)
					actName := actId.GetName()
					measNameList = append(measNameList, actName)
				}

				ranTypeName := xapp.Get_e2ap_ngran_name(e2node.GetId().GetXtype())

				// Ignore 4G networks
				if strings.Contains(ranTypeName, "eNB") {
					log.Warnf("%s %d isn't part of 5G SA infrastructure, ignoring it...", ranTypeName, e2node.GetId().GetNb_id().GetNb_id())
					continue
				}

				// Ignore RAN types not in the configuration file
				if ranTypeName != cfgRanType {
					// log.Debugf("%s isn't equal to %s, ignoring...", cfgRanType, ranTypeName)
					continue
				}

				log.Infof("E2 Node %s with NbID %d has support to E2SM-KPM, sending subscription...", ranTypeName, e2node.GetId().GetNb_id().GetNb_id())

				log.Debug(xapp.SlToStrVec(measNameList).Size())

				callback := xapp.NewDirectorKpm_cb(k)
				hdlr := xapp.Report_kpm_sm(e2node.GetId(), tti, xapp.SlToStrVec(measNameList), callback)
				kpmHdlr.hdlr = append(kpmHdlr.hdlr, hdlr)
				kpmHdlr.len++
			default:
				log.Warnf("Service Model %s doesn't implemented!", smName)
				continue
			}
		}
	}

	// time.Sleep(1 * time.Minute)
	<-k.StopSignal // wait for stop signal

	for i := 0; i < kpmHdlr.len; i++ {
		if val, ok := kpmHdlr.hdlr[i].(int); ok {
			xapp.Rm_report_kpm_sm(val)
		} else {
			log.Error("Handler isn't of type int")
		}
	}

	// Stop the xApp. Avoid deadlock.
	for !xapp.Try_stop() {
		time.Sleep(1 * time.Second)
	}

	log.Info("KPM monitor finish with successfully!")
}

// Transmission Time Interval (gNB/CU/DU -> RIC -> xApp)
func getOranTTI(smTime int) xapp.Interval {
	if tti, ok := ttis[smTime]; ok {
		return tti
	}

	panic("Unknown SM time") // stop here
}

// Indication handler
func (k *Kpimon) Handle(ind xapp.Swig_kpm_ind_data_t) {
	kpmInd := KPMIndication{}

	// process message header
	if ind.GetHdr() != nil {
		tNow := time.Now().UnixMicro()
		tReport := ind.GetHdr().GetKpm_ric_ind_hdr_format_1().GetCollectStartTime()
		tDiff := tNow - int64(tReport)

		ranTypeName := xapp.Get_e2ap_ngran_name(ind.GetId().GetXtype())

		log.Infof("Received a KPM indication message from %s with ID %d", ranTypeName, ind.GetId().GetNb_id().GetNb_id())

		kpmInd.Latency = tDiff

		kpmInd.E2NodeInfos = E2NodeInfos{
			NodebID:      int(ind.GetId().GetNb_id().GetNb_id()),
			NodeTypeName: ranTypeName,
			Mcc:          ind.GetId().GetPlmn().GetMcc(),
			Mnc:          ind.GetId().GetPlmn().GetMnc(),
			MncDigitLen:  ind.GetId().GetPlmn().GetMnc_digit_len(),
			CuDuID:       nil,
		}

		// check if Node is CU || DU (FIXME: cu_du_id has a invalid number)
		if !utils.CheckNodeIsMonolitic(int(ind.GetId().GetXtype())) {
			kpmInd.E2NodeInfos.CuDuID = nil
		}
	}

	// process message payload
	if ind.GetMsg() != nil {
		switch int(ind.GetMsg().GetXtype()) {
		case xapp.FORMAT_1_INDICATION_MESSAGE:
			log.Warn("KPM Indication Message Format 1 not implemented!")
		case xapp.FORMAT_2_INDICATION_MESSAGE:
			log.Warn("KPM Indication Message Format 2 not implemented!")
		case xapp.FORMAT_3_INDICATION_MESSAGE:
			msgFmt3 := ind.GetMsg().GetFrm_3()
			for i := 0; i < int(msgFmt3.GetUe_meas_report_lst_len()); i++ {
				ueMeasurementReportItem := msgFmt3.GetMeas_report_per_ue().Get(i)
				// process UEID
				// check UE ID by Node Type
				switch int(ind.GetId().GetXtype()) { // FIXME: Not working with E2AP UE ID Type
				case utils.Ngran_gNB: // gNB | CU | CU-CP
					if ueMeasurementReportItem.GetUe_meas_report_lst().GetGnb().GetGnb_cu_ue_f1ap_lst_len() != 0 {
						// F1AP UE ID (only for CU and DU)
						kpmInd.UEIDs.GnbCuUeF1ApId = *ueMeasurementReportItem.GetUe_meas_report_lst().GetGnb().GetGnb_cu_ue_f1ap_lst()
					}

					// AMF UE NGAP ID
					kpmInd.UEIDs.AmfUeNgApId = ueMeasurementReportItem.GetUe_meas_report_lst().GetGnb().GetAmf_ue_ngap_id()

					// GUAMI (PLMN ID + AMF ID (AMF Region ID + AMF Set ID))
					kpmInd.UEIDs.Guami.Plmn.Mcc = ueMeasurementReportItem.GetUe_meas_report_lst().GetGnb().GetGuami().GetPlmn_id().GetMcc()
					kpmInd.UEIDs.Guami.Plmn.Mnc = ueMeasurementReportItem.GetUe_meas_report_lst().GetGnb().GetGuami().GetPlmn_id().GetMnc()
					kpmInd.UEIDs.Guami.Plmn.MncDigitLen = ueMeasurementReportItem.GetUe_meas_report_lst().GetGnb().GetGuami().GetPlmn_id().GetMnc_digit_len()
					kpmInd.UEIDs.Guami.AmfRegionId = ueMeasurementReportItem.GetUe_meas_report_lst().GetGnb().GetGuami().GetAmf_region_id()
					kpmInd.UEIDs.Guami.AmfSetId = ueMeasurementReportItem.GetUe_meas_report_lst().GetGnb().GetGuami().GetAmf_set_id()

					// RAN UE ID
					if ueMeasurementReportItem.GetUe_meas_report_lst().GetGnb_cu_up().GetRan_ue_id() != nil {
						kpmInd.UEIDs.RanUeId = *ueMeasurementReportItem.GetUe_meas_report_lst().GetGnb_cu_up().GetRan_ue_id()
					}
				case utils.Ngran_gNB_DU:
					// F1AP UE ID (only for CU and DU)
					kpmInd.UEIDs.GnbCuUeF1ApId = ueMeasurementReportItem.GetUe_meas_report_lst().GetGnb_du().GetGnb_cu_ue_f1ap()

					// RAN UE ID
					if ueMeasurementReportItem.GetUe_meas_report_lst().GetGnb_cu_up().GetRan_ue_id() != nil {
						kpmInd.UEIDs.RanUeId = *ueMeasurementReportItem.GetUe_meas_report_lst().GetGnb_cu_up().GetRan_ue_id()
					}
				case utils.Ngran_gNB_CUUP:
					// gNB-CU-CP UE E1AP ID
					kpmInd.UEIDs.GnbCuCpUeE1ApId = ueMeasurementReportItem.GetUe_meas_report_lst().GetGnb_cu_up().GetGnb_cu_cp_ue_e1ap()

					// RAN UE ID
					if ueMeasurementReportItem.GetUe_meas_report_lst().GetGnb_cu_up().GetRan_ue_id() != nil {
						kpmInd.UEIDs.RanUeId = *ueMeasurementReportItem.GetUe_meas_report_lst().GetGnb_cu_up().GetRan_ue_id()
					}
				default:
					log.Warnf("UE ID node type %v not supported!", ueMeasurementReportItem.GetUe_meas_report_lst().GetXtype())
					continue
				}

				// process measReport
				msgFmt1 := ueMeasurementReportItem.GetInd_msg_format_1()
				// ueMeasList := make([]UEMeasInfo, 0, int(msgFmt1.GetMeas_data_lst_len()))
				for j := 0; j < int(msgFmt1.GetMeas_data_lst_len()); j++ {
					for k := 0; k < int(msgFmt1.GetMeas_data_lst().Get(j).GetMeas_record_len()); k++ {
						if msgFmt1.GetMeas_info_lst_len() > 0 { // meas list
							log.Debug(msgFmt1.GetMeas_info_lst_len())
							os.Exit(0)
							ueMeasList := make([]UEMeasInfo, 0, msgFmt1.GetMeas_info_lst_len())
							switch int(msgFmt1.GetMeas_info_lst().Get(k).GetMeas_type().GetXtype()) {
							case xapp.NAME_MEAS_TYPE:
								// Meas Name
								measName := msgFmt1.GetMeas_info_lst().Get(k).GetMeas_type().GetName()

								// Meas Value
								var measValue interface{}
								switch int(msgFmt1.GetMeas_data_lst().Get(j).GetMeas_record_lst().Get(k).GetValue()) {
								case xapp.INTEGER_MEAS_VALUE:
									measValue = msgFmt1.GetMeas_data_lst().Get(j).GetMeas_record_lst().Get(k).GetInt_val()
								case xapp.REAL_MEAS_VALUE:
									measValue = msgFmt1.GetMeas_data_lst().Get(j).GetMeas_record_lst().Get(k).GetReal_val()
								default:
									log.Warnf("%s meas value not recognized", measName)
									continue
								}

								ueMeasList = append(ueMeasList, UEMeasInfo{
									MeasName:  measName,
									MeasValue: measValue,
								})
							default:
								log.Warnf("Measurement type %v not yet implemented", msgFmt1.GetMeas_info_lst().Get(k).GetMeas_type().GetXtype())
								continue
							}

							// check if value is reliable
							if int(msgFmt1.GetMeas_data_lst().Get(j).GetIncomplete_flag()) == xapp.TRUE_ENUM_VALUE {
								log.Warn("Measurement record not reliable!")
							}

							// Add UE meas to list
							kpmInd.UEInfos.UEMeasList = ueMeasList
						}
					}
				}
			}
		default:
			log.Error("Unknown KPM Indication Message Format")
		}
	}

	// sending indications to channel
	select {
	case k.IndCh <- kpmInd:
		log.Infof("KPM indication message from %s with ID %d consumed", kpmInd.NodeTypeName, kpmInd.NodebID)
	default:
		log.Warnf("KPM indication message from %s with ID %d not consumed, discarding...", kpmInd.NodeTypeName, kpmInd.NodebID)
	}

}
