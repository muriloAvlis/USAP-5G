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
#include "defer.h"
#include <unistd.h>

typedef struct test
{
    u_int8_t * buffer;
    size_t size;
} test_t;

test_t testFunc(unsigned char **metricNames, size_t numOfMetrics, u_int64_t granularityPeriod)
{Deferral
    // Initialize the result
    test_t encoded = {NULL, 0};

    // E2SM_KPM_ActionDefinition allocation
    E2SM_KPM_ActionDefinition_t *actDef = (E2SM_KPM_ActionDefinition_t *)calloc(1, sizeof(E2SM_KPM_ActionDefinition_t));
    if (actDef == NULL) {
        fprintf(stderr, "[ERROR] E2SM_KPM_ActionDefinition memory allocation failure!\n");
        return encoded;
    }
    Defer(ASN_STRUCT_FREE(asn_DEF_E2SM_KPM_ActionDefinition, actDef)); // free memory in the end

    // ActionDefinitionFormat1 memory allocation
    E2SM_KPM_ActionDefinition_Format4_t * actDefFmt4 = (E2SM_KPM_ActionDefinition_Format4_t *)calloc(1, sizeof(E2SM_KPM_ActionDefinition_Format4_t));
    if(actDefFmt4 == NULL) {
        fprintf(stderr, "[ERROR] E2SM_KPM_ActionDefinition_Format1 memory allocation failure!\n");
        return encoded;
    }
    Defer(ASN_STRUCT_FREE(asn_DEF_E2SM_KPM_ActionDefinition_Format4, actDefFmt4)); // free memory in the end

    // Set Action Definition to format 4 (UE-level Measurement)
    actDef->ric_Style_Type = 4;
    actDef->actionDefinition_formats.choice.actionDefinition_Format4 = actDefFmt4;
    actDef->actionDefinition_formats.present = E2SM_KPM_ActionDefinition__actionDefinition_formats_PR_actionDefinition_Format4;

    // Set test Condition
    size_t numOfTestsCond = 1;
    actDefFmt4->matchingUeCondList.list.array = (MatchingUeCondPerSubItem_t **)calloc(numOfTestsCond, sizeof(MatchingUeCondPerSubItem_t *));
    if (actDefFmt4->matchingUeCondList.list.array == NULL) {
        fprintf(stderr, "[ERROR] Memory allocation failure for MatchingUeCondPerSubItem_t array!\n");
        return encoded;
    }
    Defer(free(actDefFmt4->matchingUeCondList.list.array));
    actDefFmt4->matchingUeCondList.list.count = 0;
    actDefFmt4->matchingUeCondList.list.size = numOfTestsCond;

    // Alloc memory to each internal structure
    for (size_t i = 0; i < numOfTestsCond; i++) {
        actDefFmt4->matchingUeCondList.list.array[i] = (MatchingUeCondPerSubItem_t *)calloc(1, sizeof(MatchingUeCondPerSubItem_t));
        if (actDefFmt4->matchingUeCondList.list.array[i] == NULL) {
            fprintf(stderr, "[ERROR] Memory allocation failure for MatchingUeCondPerSubItem_t at index %zu!\n", i);
            return encoded;
        }
        Defer(free(actDefFmt4->matchingUeCondList.list.array[i]));

        // alloc memory for test conditions
        //// testValue
        actDefFmt4->matchingUeCondList.list.array[i]->testCondInfo.testValue = (TestCond_Value_t *)calloc(1, sizeof(TestCond_Value_t));
        if (actDefFmt4->matchingUeCondList.list.array[i]->testCondInfo.testValue == NULL) {
            fprintf(stderr, "[ERROR] Memory allocation failure for TestCond_Value_t at index %zu!\n", i);
            return encoded;
        }
        Defer(free(actDefFmt4->matchingUeCondList.list.array[i]->testCondInfo.testValue));
        //// Test Expression
        actDefFmt4->matchingUeCondList.list.array[i]->testCondInfo.testExpr = (long *)malloc(sizeof(long));
        if (actDefFmt4->matchingUeCondList.list.array[i]->testCondInfo.testExpr == NULL) {
            fprintf(stderr, "[ERROR] Memory allocation failure for testExpr at index %zu!\n", i);
            return encoded;
        }
        Defer(free(actDefFmt4->matchingUeCondList.list.array[i]->testCondInfo.testExpr));

        // Set conditions
        *(actDefFmt4->matchingUeCondList.list.array[i]->testCondInfo.testExpr) = TestCond_Expression_lessthan;
        actDefFmt4->matchingUeCondList.list.array[i]->testCondInfo.testType.present = TestCond_Type_PR_ul_rSRP;
        actDefFmt4->matchingUeCondList.list.array[i]->testCondInfo.testType.choice.ul_rSRP = TestCond_Type__ul_rSRP_true;
        actDefFmt4->matchingUeCondList.list.array[i]->testCondInfo.testValue->present = TestCond_Value_PR_valueInt;
        actDefFmt4->matchingUeCondList.list.array[i]->testCondInfo.testValue->choice.valueInt = 1000;

        actDefFmt4->matchingUeCondList.list.count++;
    }

    // set meas info list
    //// alloc memory for info list
    actDefFmt4->subscriptionInfo.measInfoList.list.array = (MeasurementInfoItem_t **)calloc(numOfMetrics, sizeof(MeasurementInfoItem_t *));
    if (actDefFmt4->subscriptionInfo.measInfoList.list.array == NULL) {
        fprintf(stderr, "[ERROR] Memory allocation failure for MeasurementInfoItem_t array!\n");
        return encoded;
    }
    Defer(free(actDefFmt4->subscriptionInfo.measInfoList.list.array));
    actDefFmt4->subscriptionInfo.measInfoList.list.count = 0;
    actDefFmt4->subscriptionInfo.measInfoList.list.size = numOfMetrics;

    for (size_t i = 0; i < numOfMetrics; i++)
    {
        // alloc memory for meas name
        actDefFmt4->subscriptionInfo.measInfoList.list.array[i] = (MeasurementInfoItem_t *)calloc(1, sizeof(MeasurementInfoItem_t));
        if (actDefFmt4->subscriptionInfo.measInfoList.list.array[i] == NULL) {
            fprintf(stderr, "[ERROR] Memory allocation failure for MatchingUeCondPerSubItem_t at index %zu!\n", i);
            return encoded;
        }
        Defer(free(actDefFmt4->subscriptionInfo.measInfoList.list.array[i]));

        // Set meas name
        actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->measType.present = MeasurementType_PR_measName;
        size_t measNameSize = strlen((const char*)metricNames[i]);
        actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->measType.choice.measName.buf = (uint8_t *)malloc((measNameSize) * sizeof(uint8_t)); // +1 for null terminator
        if(actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->measType.choice.measName.buf == NULL) {
            fprintf(stderr, "[ERROR] Meas name buffer memory allocation failure!\n");
            return encoded;
        }
        Defer(free(actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->measType.choice.measName.buf));
        memcpy(actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->measType.choice.measName.buf, metricNames[i], measNameSize);
        actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->measType.choice.measName.size = measNameSize;

        // set label info lst
        size_t n_of_labels = 1;
        //// alloc memory for labelInfoLst
        actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->labelInfoList.list.array = (LabelInfoItem_t **)calloc(n_of_labels, sizeof(LabelInfoItem_t));
        if (actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->labelInfoList.list.array == NULL)
        {
            fprintf(stderr, "[ERROR] Memory allocation failure for LabelInfoItem_t at index %zu!\n", i);
            return encoded;
        }
        Defer(free(actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->labelInfoList.list.array));

        actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->labelInfoList.list.count = 0;
        actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->labelInfoList.list.size = n_of_labels;

        for (size_t j = 0; j < n_of_labels; j++)
        {
            // Allocate memory for LabelInfoItem
            actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->labelInfoList.list.array[j] = (LabelInfoItem_t *)calloc(1, sizeof(LabelInfoItem_t));
            if (actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->labelInfoList.list.array[j] == NULL) {
                fprintf(stderr, "[ERROR] Memory allocation failure for LabelInfoItem_t at index %zu, label index %zu!\n", i, j);
                return encoded;
            }
            Defer(free(actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->labelInfoList.list.array[j]));

            // Initialize labelInfoItem
            actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->labelInfoList.list.array[j]->measLabel.noLabel = (long *)calloc(1, sizeof(long));
            if (actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->labelInfoList.list.array[j]->measLabel.noLabel == NULL) {
                fprintf(stderr, "[ERROR] Memory allocation failure for noLabel at index %zu, label index %zu!\n", i, j);
                return encoded;
            }
            Defer(free(actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->labelInfoList.list.array[j]->measLabel.noLabel));

            *(actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->labelInfoList.list.array[j]->measLabel.noLabel) = MeasurementLabel__noLabel_true;
        }

        // increment arrays count
        actDefFmt4->subscriptionInfo.measInfoList.list.count++;
        actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->labelInfoList.list.count++;
    }

   	// Set granularity period
    actDefFmt4->subscriptionInfo.granulPeriod = granularityPeriod;

    // Create an encoding buffer
    const size_t buffer_size = 1024;
    u_int8_t *buffer = (uint8_t *)calloc(1, buffer_size);
    if(buffer == NULL) {
        fprintf(stderr, "[ERROR] Buffer memory allocation failure!\n");
        return encoded;
    }
    Defer(free(buffer)); // free memory in the end

    // Compare buffers size
    // memcpy(buffer, actDef, buffer_size);

	xer_fprint(stdout, &asn_DEF_E2SM_KPM_ActionDefinition, actDef);

    // Encoding
    asn_enc_rval_t enc_rval = aper_encode_to_buffer(&asn_DEF_E2SM_KPM_ActionDefinition, NULL, actDef, buffer, buffer_size);

    // Failed to encoding
	if (enc_rval.encoded == -1) {
    	fprintf(stderr, "[ERROR] Failed to encode E2SM_KPM_ActionDefinition format 4!\n");
    	fprintf(stderr, "[ERROR] Encoding error: %s\n", enc_rval.failed_type ? enc_rval.failed_type->name : "Unknown type");
    	if (enc_rval.structure_ptr) {
        	fprintf(stderr, "[ERROR] Failed structure pointer: %p\n", enc_rval.structure_ptr);
    	}
    	return encoded;
	}

    // Adjust size (1 byte == 8 bits)
    encoded.size = (enc_rval.encoded + 7) / 8; // truncate
    encoded.buffer = calloc(1, encoded.size);
    for (size_t i = 0; i < encoded.size; i++) {
        encoded.buffer[i] = buffer[i];
    }

    return encoded;
}

// Don't compile with this
/*
int main() {Deferral
    unsigned char *metrics[] = {"Metric1"};
	size_t numOfMetrics = sizeof(metrics) / sizeof(metrics[0]);
	u_int64_t granPer = 1000;
	test_t res = encodeActionDefinitionFormat4(metrics, numOfMetrics, granPer);
	Defer(free(res.buffer));

    // Exibir o resultado (apenas como exemplo, ajuste conforme necessário)
    printf("Encoded buffer size: %zu\n", res.size);
    printf("Encoded buffer: ");
    for (size_t i = 0; i < res.size; i++) {
        printf("%d ", res.buffer[i]);
    }
    printf("\n");

    return 0;
}
*/