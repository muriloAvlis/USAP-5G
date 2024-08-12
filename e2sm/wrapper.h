//
// Created by Murilo Silva on 05/08/24.
//

#ifndef WRAPPER_H
#define WRAPPER_H

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
// Ue cond
#include <MatchingUeCondPerSubItem.h>
#include <TestCondInfo.h>
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
#include "defer.h"

typedef struct actFmtType
{
    char ** act_fmt_type1; // E2 Node Measurement
    char ** act_fmt_type2; // E2 Node Measurement for a single UE
    char ** act_fmt_type3; // Condition-based, UE-level E2 Node Measuremen
    char ** act_fmt_type4; // Common Condition-based, UE-level Measurement
    char ** act_fmt_type5; // E2 Node Measurement for multiple UEs
    int act_fmt_type1_size;
    int act_fmt_type2_size;
    int act_fmt_type3_size;
    int act_fmt_type4_size;
    int act_fmt_type5_size;
} actFmtType_t;

typedef struct encodedData
{
    u_int64_t * buffer;
    int size;
} encodedData_t;

actFmtType_t buildRanCellUeKpi(const char *ranFuncDefinition);

// Encode Event Trigger Definition (only format 1 is available on KPM)
encodedData_t encodeEventTriggerDefinitionFormat1(u_int64_t reportingPeriod);

// Encode event Action Definition 4
encodedData_t encodeActionDefinitionFormat4(unsigned char **metricNames, size_t numOfMetrics, u_int64_t granularityPeriod);

#endif //WRAPPER_H
