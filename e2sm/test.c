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
#include <TestCond-Type.h>
#include <TestCond-Value.h>
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
#include <unistd.h>
#include <errno.h>

typedef struct test
{
    u_int8_t * buffer;
    size_t size;
} test_t;

test_t testFunc(char **metricNames, const size_t numOfMetrics, const unsigned long granularityPeriod)
{
    // Initialize the result
    test_t encoded = {NULL, 0};

    // E2SM_KPM_ActionDefinition allocation
    E2SM_KPM_ActionDefinition_t *actDef = calloc(1, sizeof(E2SM_KPM_ActionDefinition_t));
    if (actDef == NULL) {
        fprintf(stderr, "[ERROR] E2SM_KPM_ActionDefinition memory allocation failure!\n");
        ASN_STRUCT_FREE(asn_DEF_E2SM_KPM_ActionDefinition, actDef);
        return encoded;
    }

    // Set Action Definition to format 4 (UE-level Measurement)
    actDef->ric_Style_Type = 4;
    actDef->actionDefinition_formats.present = E2SM_KPM_ActionDefinition__actionDefinition_formats_PR_actionDefinition_Format4;

    // ActionDefinitionFormat4 memory allocation
    E2SM_KPM_ActionDefinition_Format4_t * actDefFmt4 = calloc(1, sizeof(E2SM_KPM_ActionDefinition_Format4_t));
    if(actDefFmt4 == NULL) {
        fprintf(stderr, "[ERROR] E2SM_KPM_ActionDefinition_Format4 memory allocation failure!\n");
        ASN_STRUCT_FREE(asn_DEF_E2SM_KPM_ActionDefinition, actDef);
        return encoded;
    }

    // Matching UE test condition
    MatchingUeCondPerSubItem_t *matchingUeCondItem = (MatchingUeCondPerSubItem_t *)calloc(1, sizeof(MatchingUeCondPerSubItem_t));
    if(matchingUeCondItem == NULL) {
        fprintf(stderr, "[ERROR] matchingUeCondItem memory allocation failure!\n");
        ASN_STRUCT_FREE(asn_DEF_E2SM_KPM_ActionDefinition, actDef);
        return encoded;
    }
    matchingUeCondItem->testCondInfo.testType.present = TestCond_Type_PR_ul_rSRP;
    matchingUeCondItem->testCondInfo.testType.choice.ul_rSRP = TestCond_Type__ul_rSRP_true;

    //// Test Condition expression
    static TestCond_Expression_t testConditionExp = TestCond_Expression_lessthan;
    matchingUeCondItem->testCondInfo.testExpr = &testConditionExp;

    //// test Value
    TestCond_Value_t *testVal = (TestCond_Value_t *)calloc(1, sizeof(TestCond_Value_t));
    if(testVal == NULL) {
        fprintf(stderr, "[ERROR] testVal memory allocation failure!\n");
        ASN_STRUCT_FREE(asn_DEF_E2SM_KPM_ActionDefinition, actDef);
        return encoded;
    }
    testVal->present = TestCond_Value_PR_valueInt;
    testVal->choice.valueInt = 1000;

    matchingUeCondItem->testCondInfo.testValue = testVal;

    // Add to test list
    ASN_SEQUENCE_ADD(&actDefFmt4->matchingUeCondList.list, matchingUeCondItem);

    // Set meas info list
    for (size_t i = 0; i < numOfMetrics; i++)
    {
        MeasurementInfoItem_t *measInfoItem = (MeasurementInfoItem_t *)calloc(1, sizeof(MeasurementInfoItem_t));
        if(measInfoItem == NULL) {
            fprintf(stderr, "[ERROR] measInfoItem memory allocation failure!\n");
            ASN_STRUCT_FREE(asn_DEF_E2SM_KPM_ActionDefinition, actDef);
            return encoded;
        }
        // meas type
        measInfoItem->measType.present = MeasurementType_PR_measName;
        //// meas name
        size_t measNameSize = strlen(metricNames[i]);
        measInfoItem->measType.choice.measName.buf = (uint8_t *)calloc(measNameSize + 1, sizeof(uint8_t));
        if(measInfoItem->measType.choice.measName.buf == NULL) {
            fprintf(stderr, "[ERROR] measName buffer memory allocation failure!\n");
            ASN_STRUCT_FREE(asn_DEF_E2SM_KPM_ActionDefinition, actDef);
            return encoded;
        }
        memcpy(measInfoItem->measType.choice.measName.buf, metricNames[i], measNameSize);
        measInfoItem->measType.choice.measName.buf[measNameSize] = '\0'; // for null character
        measInfoItem->measType.choice.measName.size = measNameSize;

        // label info list
        LabelInfoItem_t *labelInfoItem = (LabelInfoItem_t *)calloc(1, sizeof(LabelInfoItem_t));
        labelInfoItem->measLabel.noLabel = (long *)calloc(1, sizeof(long));
        if(labelInfoItem->measLabel.noLabel == NULL) {
            fprintf(stderr, "[ERROR] NoLabel buffer memory allocation failure!\n");
            ASN_STRUCT_FREE(asn_DEF_E2SM_KPM_ActionDefinition, actDef);
            return encoded;
        }
        static long label = MeasurementLabel__noLabel_true;
        labelInfoItem->measLabel.noLabel = &label;

        // add labelInfoitem to list
        ASN_SEQUENCE_ADD(&measInfoItem->labelInfoList.list, labelInfoItem);
        // Add to measInfoitem to list
        ASN_SEQUENCE_ADD(&actDefFmt4->subscriptionInfo.measInfoList.list, measInfoItem);
    }

    // Granularity period
    actDefFmt4->subscriptionInfo.granulPeriod = granularityPeriod;

    // Set action definition format 4
    actDef->actionDefinition_formats.choice.actionDefinition_Format4 = actDefFmt4;

    // Create an encoding buffer
    void *buffer = NULL;

    // xer_fprint(stdout, &asn_DEF_E2SM_KPM_ActionDefinition, actDef);

    // Encoding
    size_t buffer_size = aper_encode_to_new_buffer(&asn_DEF_E2SM_KPM_ActionDefinition, NULL, actDef, &buffer);
    printf("Buffer size %ld\n", buffer_size);

    encoded.size = buffer_size; // truncate
    encoded.buffer = calloc(1, encoded.size);
    if (encoded.buffer == NULL) {
        fprintf(stderr, "Memory allocation failure\n");
        return encoded;
    }
    memcpy(encoded.buffer, buffer, encoded.size);

    return encoded;
}

// Don't compile with this
// int main() {
//     char * metrics[] = {"CQI"};
// 	size_t numOfMetrics = sizeof(metrics) / sizeof(metrics[0]);
// 	u_int64_t granPer = 1000;
//
// 	test_t res = testFunc(metrics, numOfMetrics, granPer);
//
//     // Exibir o resultado (apenas como exemplo, ajuste conforme necessário)
//     printf("Encoded buffer size: %zu\n", res.size);
//     printf("Encoded buffer: ");
//     for (size_t i = 0; i < res.size; i++) {
//         printf("%d ", res.buffer[i]);
//     }
//     printf("\n");
//
//     free(res.buffer);
//
//     return 0;
// }
