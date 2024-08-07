//
// Created by Murilo Silva on 05/08/24.
//

#include "wrapper.h"

actDefFmt_t buildRanCellUeKpi(const char* ranFuncDefinition)
{Deferral
    actDefFmt_t res;

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
        rfDefBuffer[i/2] = (char)(strtol(byte, NULL, 16));
    }

    // Null-terminate the char array
    rfDefBuffer[rfDefLen / 2] = '\0';

    // Now hex_buffer contains the binary data corresponding to the RF Definitions values
    // Print the result
    printf("[INFO] RAN Function definition values as a string: %s", rfDefBuffer);

    char ** act_def_format1 = NULL;
    char ** act_def_format2 = NULL;
    char ** act_def_format3 = NULL;
    char ** act_def_format4 = NULL;
    char ** act_def_format5 = NULL;
    int act_def_format1_size = 0;
    int act_def_format2_size = 0;
    int act_def_format3_size = 0;
    int act_def_format4_size = 0;
    int act_def_format5_size = 0;

    E2SM_KPM_RANfunction_Description_t *e2smKpmRanFunctDescrip = (E2SM_KPM_RANfunction_Description_t *)(calloc(1, sizeof(E2SM_KPM_RANfunction_Description_t)));

    // decode asn1.1 format
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
            case 1: // act_def_fmt_1
                act_def_format1_size = e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.count;
                act_def_format1 = (char **)malloc(act_def_format1_size * sizeof(char *));
                for (size_t j = 0; j < act_def_format1_size; j++)
                {
                    size_t bufsize=e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.size;
                    act_def_format1[j] = (char*)malloc(bufsize);
                    act_def_format1[j] = (char*)e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.buf;
                }
                break;
            case 2: // act_def_fmt_2
                act_def_format2_size = e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.count;
                act_def_format2 = (char **)malloc(act_def_format2_size * sizeof(char *));
                for (size_t j = 0; j < act_def_format2_size; j++)
                {
                    size_t bufsize=e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.size;
                    act_def_format2[j] = (char*)malloc(bufsize);
                    act_def_format2[j] = (char*)e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.buf;
                }
                break;
            case 3: // act_def_fmt_3
                act_def_format3_size = e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.count;
                act_def_format3 = (char **)malloc(act_def_format3_size * sizeof(char *));
                for (size_t j = 0; j < act_def_format3_size; j++)
                {
                    size_t bufsize=e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.size;
                    act_def_format3[j] = (char*)malloc(bufsize);
                    act_def_format3[j] = (char*)e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.buf;
                }
                break;
            case 4: // act_def_fmt_4
                act_def_format4_size = e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.count;
                act_def_format4 = (char **)malloc(act_def_format4_size * sizeof(char *));
                for (size_t j = 0; j < act_def_format4_size; j++)
                {
                    size_t bufsize=e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.size;
                    act_def_format4[j] = (char*)malloc(bufsize);
                    act_def_format4[j] = (char*)e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.buf;
                }
                break;
            case 5: // act_def_fmt_5
                act_def_format5_size = e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.count;
                act_def_format5 = (char **)malloc(act_def_format5_size * sizeof(char *));
                for (size_t j = 0; j < act_def_format5_size; j++)
                {
                    size_t bufsize=e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.size;
                    act_def_format5[j] = (char*)malloc(bufsize);
                    act_def_format5[j] = (char*)e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.buf;
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
    res.act_def_format1 = act_def_format1;
    res.act_def_format2 = act_def_format2;
    res.act_def_format3 = act_def_format3;
    res.act_def_format4 = act_def_format4;
    res.act_def_format5 = act_def_format5;
    res.act_def_format1_size = act_def_format1_size;
    res.act_def_format2_size = act_def_format2_size;
    res.act_def_format3_size = act_def_format3_size;
    res.act_def_format4_size = act_def_format4_size;
    res.act_def_format5_size = act_def_format5_size;
    return res;
}
