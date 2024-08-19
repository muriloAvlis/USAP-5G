//
// Created by murilo on 19/08/24.
//

#include "wrapper.h"

// TODO: fix empty metrics return when call this func
actFmtTypes_t decodeActionFormatTypes(const char* ranFuncDefinition)
{
    actFmtTypes_t res = {};

    // Calculate the length of the hex string
    size_t rfDefLen = strlen(ranFuncDefinition);

    // Allocate memory for a char array to store the hex values
    char *rfDefBuffer = (char *)malloc((rfDefLen / 2) + 1); // Each byte is represented by 2 characters, +1 for null terminator
    if (rfDefBuffer == NULL) {
        fprintf(stderr, "rfDefBuffer memory allocation failed\n");
        return res;
    }

    // Convert the hex string to binary data
    for (size_t i = 0; i < rfDefLen; i += 2) {
        char byte[3] = {ranFuncDefinition[i], ranFuncDefinition[i + 1], '\0'};
        rfDefBuffer[i / 2] = (char)strtol(byte, NULL, 16);
    }

    // Null-terminate the char array
    rfDefBuffer[rfDefLen / 2] = '\0';

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
    if (e2smKpmRanFunctDescrip == NULL) {
        fprintf(stderr, "e2smKpmRanFunctDescrip memory allocation failed\n");
        return res;
    }

    // decode asn.1 format
    const enum asn_transfer_syntax syntax = ATS_ALIGNED_BASIC_PER;
    asn_dec_rval_t rval = asn_decode(NULL, syntax, &asn_DEF_E2SM_KPM_RANfunction_Description, (void**)&e2smKpmRanFunctDescrip, rfDefBuffer, rfDefLen);

    if (rval.code == RC_OK)
    {
        printf( "[INFO] E2SM-KPM RAN Function Description decode successfull!! :)\n");
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
        printf("[WARN] E2SM-KPM RAN Function Description decode failed rval.code = %d \n", rval.code);
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

    free(rfDefBuffer);
    free(e2smKpmRanFunctDescrip);

    return res;
}