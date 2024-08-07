//
// Created by Murilo Silva on 05/08/24.
//

#ifndef WRAPPER_HPP
#define WRAPPER_HPP

// event triggers
#include <E2SM-KPM-EventTriggerDefinition.h>
#include <E2SM-KPM-EventTriggerDefinition-Format1.h>
// action definitions
#include <E2SM-KPM-ActionDefinition.h>
#include <E2SM-KPM-ActionDefinition-Format1.h>
#include <E2SM-KPM-ActionDefinition-Format2.h>
#include <E2SM-KPM-ActionDefinition-Format3.h>
#include <E2SM-KPM-ActionDefinition-Format4.h>
#include <E2SM-KPM-ActionDefinition-Format5.h>
// Measurements
#include <MeasurementInfoList.h>
#include <GranularityPeriod.h>
#include <MeasurementInfoItem.h>
#include <MeasurementType.h>
#include <MeasurementTypeID.h>
#include <MeasurementLabel.h>
#include<MeasurementCondList.h>
#include <MeasurementCondItem.h>
#include <MatchingCondItem.h>
#include<MeasurementInfo-Action-Item.h>


#include<E2SM-KPM-RANfunction-Description.h>
#include<RIC-ReportStyle-Item.h>

// labels
#include <LabelInfoItem.h>
#include <LabelInfoList.h>
#include <CGI.h>
#include <PLMNIdentity.h>
// Ind header
#include <E2SM-KPM-IndicationHeader.h>
#include <E2SM-KPM-IndicationHeader-Format1.h>
// Ind msg
#include <E2SM-KPM-IndicationMessage.h>
#include <E2SM-KPM-IndicationMessage-Format1.h>
#include <E2SM-KPM-IndicationMessage-Format2.h>
#include <E2SM-KPM-IndicationMessage-Format3.h>
// NodeB IDs
#include <GlobalENB-ID.h>
#include <GlobalenGNB-ID.h>
#include <GlobalNgENB-ID.h>
#include <GlobalGNB-ID.h>
#include <GNB-ID.h>
#include <GNB-CU-UP-ID.h>
#include <GNB-DU-ID.h>
#include <EN-GNB-ID.h>
#include <ENB-ID.h>
#include <NR-CGI.h>
#include <S-NSSAI.h>
#include <TimeStamp.h>
#include <per_encoder.h>

#include "asn_application.h"

#include "include/defer.hpp"

using actDefFmt_t = struct
{
    std::vector<uint8_t*> act_def_format1; // E2 Node Measurement
    std::vector<uint8_t*> act_def_format2; // E2 Node Measurement for a single UE
    std::vector<uint8_t*> act_def_format3; // Condition-based, UE-level E2 Node Measuremen
    std::vector<uint8_t*> act_def_format4; // Common Condition-based, UE-level Measurement
    std::vector<uint8_t*> act_def_format5; // E2 Node Measurement for multiple UEs
    int act_def_format1_size;
    int act_def_format2_size;
    int act_def_format3_size;
    int act_def_format4_size;
    int act_def_format5_size;
};

actDefFmt_t buildRanCellUeKpi(const char *ranFuncDefinition);

#endif //WRAPPER_HPP
