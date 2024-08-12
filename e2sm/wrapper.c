//
// Created by Murilo Silva on 05/08/24.
//

#include "wrapper.h"

#include <TestCond-Value.h>

actFmtType_t buildRanCellUeKpi(const char* ranFuncDefinition)
{Deferral
    actFmtType_t res;

    // Calculate the length of the hex string
    const size_t rfDefLen = strlen(ranFuncDefinition);

    // Allocate memory for a char array to store the hex values
    char *rfDefBuffer = malloc(rfDefLen/2 + 1);  // Each byte is represented by 2 characters, +1 for null terminator
    assert(rfDefBuffer != NULL && "[ERROR] Failed to allocate memory!");
    Defer(free(rfDefBuffer));

    // Convert the rfDefinition string to binary data
    for (size_t i = 0; i < rfDefLen; i += 2)
    {
        const char byte[3] = {ranFuncDefinition[i], ranFuncDefinition[i+1], '\0'};
        rfDefBuffer[i/2] = (char)(strtol(byte, NULL, 16)); // convert to long int | 16 == hex
    }

    // Null-terminate the char array
    rfDefBuffer[rfDefLen / 2] = '\0';

    // Now hex_buffer contains the binary data corresponding to the RF Definitions values
    // Print the result
    printf("[INFO] RAN Function definition values as a string: %s", rfDefBuffer);

    char ** act_fmt_type1 = NULL;
    char ** act_fmt_type2 = NULL;
    char ** act_fmt_type3 = NULL;
    char ** act_fmt_type4 = NULL;
    char ** act_fmt_type5 = NULL;
    int act_fmt_type1_size = 0;
    int act_fmt_type2_size = 0;
    int act_fmt_type3_size = 0;
    int act_fmt_type4_size = 0;
    int act_fmt_type5_size = 0;

    E2SM_KPM_RANfunction_Description_t *e2smKpmRanFunctDescrip = (E2SM_KPM_RANfunction_Description_t *)(calloc(1, sizeof(E2SM_KPM_RANfunction_Description_t)));

    // decode asn.1 format
    const enum asn_transfer_syntax syntax = ATS_ALIGNED_BASIC_PER;
    asn_dec_rval_t rval = asn_decode(NULL, syntax, &asn_DEF_E2SM_KPM_RANfunction_Description, (void**)&e2smKpmRanFunctDescrip, rfDefBuffer, rfDefLen);

    if (rval.code == RC_OK)
    {
        printf( "[INFO] E2SM KPM RAN Function Description decode successfull rval.code = %d \n", rval.code);
        // iterate over report styles | act_def
        for (size_t i = 0; i < e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.count; i++)
        {
            switch (e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->ric_ActionFormat_Type)
            {
            case 1: // act_fmt_type_1
                act_fmt_type1_size = e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.count;
                act_fmt_type1 = (char **)malloc(act_fmt_type1_size * sizeof(char *));
                for (size_t j = 0; j < act_fmt_type1_size; j++)
                {
                    size_t bufsize=e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.size;
                    act_fmt_type1[j] = (char*)malloc(bufsize);
                    act_fmt_type1[j] = (char*)e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.buf;
                }
                break;
            case 2: // act_fmt_type_2
                act_fmt_type2_size = e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.count;
                act_fmt_type2 = (char **)malloc(act_fmt_type2_size * sizeof(char *));
                for (size_t j = 0; j < act_fmt_type2_size; j++)
                {
                    size_t bufsize=e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.size;
                    act_fmt_type2[j] = (char*)malloc(bufsize);
                    act_fmt_type2[j] = (char*)e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.buf;
                }
                break;
            case 3: // act_fmt_type_3
                act_fmt_type3_size = e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.count;
                act_fmt_type3 = (char **)malloc(act_fmt_type3_size * sizeof(char *));
                for (size_t j = 0; j < act_fmt_type3_size; j++)
                {
                    size_t bufsize=e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.size;
                    act_fmt_type3[j] = (char*)malloc(bufsize);
                    act_fmt_type3[j] = (char*)e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.buf;
                }
                break;
            case 4: // act_fmt_type_4
                act_fmt_type4_size = e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.count;
                act_fmt_type4 = (char **)malloc(act_fmt_type4_size * sizeof(char *));
                for (size_t j = 0; j < act_fmt_type4_size; j++)
                {
                    size_t bufsize=e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.size;
                    act_fmt_type4[j] = (char*)malloc(bufsize);
                    act_fmt_type4[j] = (char*)e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.buf;
                }
                break;
            case 5: // act_fmt_type_5
                act_fmt_type5_size = e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.count;
                act_fmt_type5 = (char **)malloc(act_fmt_type5_size * sizeof(char *));
                for (size_t j = 0; j < act_fmt_type5_size; j++)
                {
                    size_t bufsize=e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.size;
                    act_fmt_type5[j] = (char*)malloc(bufsize);
                    act_fmt_type5[j] = (char*)e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.buf;
                }
                break;
            default:
                printf("[WARN] Unknown action definition format %ld!", e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->ric_ActionFormat_Type);
                break;
            }
        }
    } else
    {
        printf("[WARN] E2SM KPM RAN Function Description decode failed rval.code = %d \n", rval.code);
    }

    // set RAN Func definitions to res
    res.act_fmt_type1 = act_fmt_type1;
    res.act_fmt_type2 = act_fmt_type2;
    res.act_fmt_type3 = act_fmt_type3;
    res.act_fmt_type4 = act_fmt_type4;
    res.act_fmt_type5 = act_fmt_type5;
    res.act_fmt_type1_size = act_fmt_type1_size;
    res.act_fmt_type2_size = act_fmt_type2_size;
    res.act_fmt_type3_size = act_fmt_type3_size;
    res.act_fmt_type4_size = act_fmt_type4_size;
    res.act_fmt_type5_size = act_fmt_type5_size;
    return res;
}

encodedData_t encodeEventTriggerDefinitionFormat1(const u_int64_t reportingPeriod)
{Deferral
    // Initialize the result
    encodedData_t encoded = {NULL, 0};

    // E2SM_KPM_EventTriggerDefinition allocation
    E2SM_KPM_EventTriggerDefinition_t *eventTriggerDef = (E2SM_KPM_EventTriggerDefinition_t *)calloc(1, sizeof(E2SM_KPM_EventTriggerDefinition_t));
    if (eventTriggerDef == NULL) {
        fprintf(stderr, "[ERROR] E2SM_KPM_EventTriggerDefinition memory allocation failure!\n");
        return encoded;
    }
    Defer(ASN_STRUCT_FREE(asn_DEF_E2SM_KPM_EventTriggerDefinition, eventTriggerDef)); // free memory in the end

    // EventTriggerFormat1 memory allocation
    E2SM_KPM_EventTriggerDefinition_Format1_t * eventTriggerDefFmt1 = (E2SM_KPM_EventTriggerDefinition_Format1_t *)calloc(1, sizeof(E2SM_KPM_EventTriggerDefinition_Format1_t));
    if(eventTriggerDefFmt1 == NULL) {
        fprintf(stderr, "[ERROR] E2SM_KPM_EventTriggerDefinition_Format1 memory allocation failure!\n");
        return encoded;
    }
    Defer(ASN_STRUCT_FREE(asn_DEF_E2SM_KPM_EventTriggerDefinition_Format1, eventTriggerDefFmt1)); // free memory in the end

    // Set event trigger definition to format 1
    eventTriggerDef->eventDefinition_formats.choice.eventDefinition_Format1 = eventTriggerDefFmt1;
    eventTriggerDef->eventDefinition_formats.present = E2SM_KPM_EventTriggerDefinition__eventDefinition_formats_PR_eventDefinition_Format1;

    // Set Reporting Period
    eventTriggerDefFmt1->reportingPeriod = reportingPeriod;

    // Create an encoding buffer
    const size_t buffer_size = 64;
    u_int8_t *buffer = (uint8_t *)calloc(1, buffer_size);
    if(buffer == NULL) {
        fprintf(stderr, "[ERROR] Buffer memory allocation failure!\n");
        return encoded;
    }
    Defer(free(buffer)); // free memory in the end

    // Compare buffers size
    memcpy(buffer, eventTriggerDef, buffer_size);

    // Encoding
    asn_enc_rval_t enc_rval = aper_encode_to_buffer(&asn_DEF_E2SM_KPM_EventTriggerDefinition, NULL, eventTriggerDef, buffer, buffer_size);

    // Failed to encoding
    if (enc_rval.encoded == -1) {
        fprintf(stderr, "[ERROR] Failed to encode E2SM_KPM_EventTriggerDefinition!\n");
        return encoded;
    }

    // Adjust size (1 byte == 8 bits)
    encoded.size = enc_rval.encoded / 8;
    encoded.buffer = calloc(1, encoded.size);
    for (size_t i = 0; i < encoded.size; i++) {
        encoded.buffer[i] = buffer[i];
    }

    return encoded;
}

encodedData_t encodeActionDefinitionFormat4(char **metricNames, size_t numOfMetrics, u_int64_t granularityPeriod)
{Deferral
    // Initialize the result
    encodedData_t encoded = {NULL, 0};

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
    actDefFmt4->matchingUeCondList.list.count = 0;
    actDefFmt4->matchingUeCondList.list.size = numOfTestsCond;

    // Alloc memory to each internal structure
    for (size_t i = 0; i < numOfTestsCond; i++) {
        actDefFmt4->matchingUeCondList.list.array[i] = (MatchingUeCondPerSubItem_t *)calloc(1, sizeof(MatchingUeCondPerSubItem_t));
        if (actDefFmt4->matchingUeCondList.list.array[i] == NULL) {
            fprintf(stderr, "[ERROR] Memory allocation failure for MatchingUeCondPerSubItem_t at index %zu!\n", i);
            return encoded;
        }

        // alloc memory for test conditions
        //// testValue
        actDefFmt4->matchingUeCondList.list.array[i]->testCondInfo.testValue = (TestCond_Value_t *)calloc(1, sizeof(TestCond_Value_t));
        if (actDefFmt4->matchingUeCondList.list.array[i]->testCondInfo.testValue == NULL) {
            fprintf(stderr, "[ERROR] Memory allocation failure for TestCond_Value_t at index %zu!\n", i);
            return encoded;
        }
        //// Test Expression
        actDefFmt4->matchingUeCondList.list.array[i]->testCondInfo.testExpr = (long *)malloc(sizeof(long));
        if (actDefFmt4->matchingUeCondList.list.array[i]->testCondInfo.testExpr == NULL) {
            fprintf(stderr, "[ERROR] Memory allocation failure for testExpr at index %zu!\n", i);
            return encoded;
        }

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
    actDefFmt4->subscriptionInfo.measInfoList.list.count = 0;
    actDefFmt4->subscriptionInfo.measInfoList.list.size = numOfMetrics;

    // set number of labels by meas_name
    size_t numOfLabels = 1;

    for (size_t i = 0; i < numOfMetrics; i++)
    {
        // alloc memory for meas name
        actDefFmt4->subscriptionInfo.measInfoList.list.array[i] = (MeasurementInfoItem_t *)calloc(1, sizeof(MeasurementInfoItem_t));
        if (actDefFmt4->subscriptionInfo.measInfoList.list.array[i] == NULL) {
            fprintf(stderr, "[ERROR] Memory allocation failure for MatchingUeCondPerSubItem_t at index %zu!\n", i);
            return encoded;
        }

        // Set meas name
        actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->measType.present = MeasurementType_PR_measName;
        size_t measNameSize = strlen(metricNames[i]);
        actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->measType.choice.measName.buf = (uint8_t *)malloc(measNameSize * sizeof(uint8_t));
        if(actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->measType.choice.measName.buf == NULL) {
            fprintf(stderr, "[ERROR] Meas name buffer memory allocation failure!\n");
            return encoded;
        }
        memcpy(actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->measType.choice.measName.buf, metricNames[i], measNameSize);
        actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->measType.choice.measName.size = measNameSize;

        //// alloc memory for labelInfoLst
        actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->labelInfoList.list.array = (LabelInfoItem_t **)calloc(numOfLabels, sizeof(LabelInfoItem_t *));
        if (actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->labelInfoList.list.array == NULL)
        {
            fprintf(stderr, "[ERROR] Memory allocation failure for LabelInfoItem_t at index %zu!\n", i);
            return encoded;
        }

        actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->labelInfoList.list.count = 0;
        actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->labelInfoList.list.size = numOfLabels;

        for (size_t j = 0; j < numOfLabels; j++)
        {
            // Allocate memory for LabelInfoItem
            actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->labelInfoList.list.array[j] = (LabelInfoItem_t *)calloc(1, sizeof(LabelInfoItem_t));
            if (actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->labelInfoList.list.array[j] == NULL) {
                fprintf(stderr, "[ERROR] Memory allocation failure for LabelInfoItem_t at index %zu, label index %zu!\n", i, j);
                return encoded;
            }

            // Initialize labelInfoItem
            actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->labelInfoList.list.array[j]->measLabel.noLabel = (long *)calloc(1, sizeof(long));
            if (actDefFmt4->subscriptionInfo.measInfoList.list.array[i]->labelInfoList.list.array[j]->measLabel.noLabel == NULL) {
                fprintf(stderr, "[ERROR] Memory allocation failure for noLabel at index %zu, label index %zu!\n", i, j);
                return encoded;
            }

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

	// xer_fprint(stdout, &asn_DEF_E2SM_KPM_ActionDefinition, actDef);

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


