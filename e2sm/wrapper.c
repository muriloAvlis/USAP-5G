//
// Created by Murilo Silva on 05/08/24.
//

#include "wrapper.h"

#include <TestCond-Value.h>

// TODO: fix empty metrics return when call this func
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
    printf("[INFO] RAN Function definition values as a string: %s\n", rfDefBuffer);

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

encodedData_t encodeActionDefinitionFormat4(char **metricNames, const size_t numOfMetrics, const u_int64_t granularityPeriod)
{Deferral
    // test
    // for (size_t i = 0; i < numOfMetrics; i++)
    // {
    //     printf("Metric %ld:  %s\n", i, metricNames[i]);
    // }

    // Initialize the result
    encodedData_t encoded = {NULL, 0};

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
    const size_t buffer_size = 1024;
    char *buffer = (char *)calloc(1, buffer_size);
    if(buffer == NULL) {
        fprintf(stderr, "[ERROR] Buffer memory allocation failure!\n");
        return encoded;
    }

    xer_fprint(stdout, &asn_DEF_E2SM_KPM_ActionDefinition, actDef);

    // Encoding
    asn_enc_rval_t enc_val = aper_encode_to_buffer(&asn_DEF_E2SM_KPM_ActionDefinition, NULL, actDef, buffer, buffer_size);

    if (enc_val.encoded == -1)
    {
        fprintf(stderr, "[ERROR] Failed to encode ASN.1 structure!\n");
    }

    encoded.size = (enc_val.encoded + 7) / 8; // convert to bytes
    encoded.buffer = calloc(1, encoded.size);
    if (encoded.buffer == NULL) {
        fprintf(stderr, "Memory allocation failure\n");
        return encoded;
    }

    memcpy(encoded.buffer, buffer, encoded.size);

    free(buffer);

    return encoded;
}


