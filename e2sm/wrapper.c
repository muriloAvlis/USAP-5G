//
// Created by Murilo Silva on 05/08/24.
//

#include "wrapper.hpp"

actDefFmt_t buildRanCellUeKpi(const char* ranFuncDefinition)
{
    actDefFmt_t res = {};

    // Calculate the length of the hex string
    const size_t rfDefLen = strlen(ranFuncDefinition);

    // Allocate memory for a char array to store the hex values
    auto *rfDefBuffer = static_cast<char *>(malloc(rfDefLen/2));  // Each byte is represented by 2 characters, +1 for null terminator
    assert(rfDefBuffer != nullptr && "[ERROR] Failed to allocate memory!");
    defer(free(rfDefBuffer));

    rfDefBuffer = rfDefBuffer + 1;

    // Convert the rfDefinition string to binary data
    for (size_t i = 0; i < rfDefLen; i += 2)
    {
        const char byte[3] {ranFuncDefinition[i], ranFuncDefinition[i+1], '\0'};
        rfDefBuffer[i/2] = {static_cast<char>(strtol(byte, nullptr, 16))};
    }

    // Null-terminate the char array
    rfDefBuffer[rfDefLen / 2] = '\0';

    // Now hex_buffer contains the binary data corresponding to the RF Definitions values
    // Print the result
    printf("[INFO] RAN Function definition values as a string: %s", rfDefBuffer);

    std::vector<uint8_t *> act_def_format1 {};
    std::vector<uint8_t *> act_def_format2 {};
    std::vector<uint8_t *> act_def_format3 {};
    std::vector<uint8_t *> act_def_format4 {};
    std::vector<uint8_t *> act_def_format5 {};
    int act_def_format1_size {};
    int act_def_format2_size {};
    int act_def_format3_size {};
    int act_def_format4_size {};
    int act_def_format5_size {};

    auto *e2smKpmRanFunctDescrip = static_cast<E2SM_KPM_RANfunction_Description_t *>(calloc(1, sizeof(E2SM_KPM_RANfunction_Description_t)));

    // decode asn.1 format
    constexpr asn_transfer_syntax syntax = ATS_ALIGNED_BASIC_PER;
    auto [code, consumed] = asn_decode(nullptr, syntax, &asn_DEF_E2SM_KPM_RANfunction_Description,
                                       reinterpret_cast<void**>(&e2smKpmRanFunctDescrip), rfDefBuffer, rfDefLen);

    if (code == RC_OK)
    {
        printf( "[INFO] E2SM KPM RAN Function Description decode successfull rval.code = %d \n", code);
        // iterate over report styles | act_def
        for (size_t i = 0; i < e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.count; i++)
        {
            switch (e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->ric_ActionFormat_Type)
            {
            case 1: // act_def_fmt_1
                act_def_format1_size = {e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.count};
                for (size_t j = 0; j < act_def_format1_size; j++)
                {
                    act_def_format1.push_back(e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.buf);
                }
                break;
            case 2: // act_def_fmt_2
                act_def_format2_size = {e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.count};
                for (size_t j = 0; j < act_def_format2_size; j++)
                {
                    act_def_format2.push_back(e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.buf);
                }
                break;
            case 3: // act_def_fmt_3
                act_def_format3_size = {e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.count};
                for (size_t j = 0; j < act_def_format3_size; j++)
                {
                    act_def_format3.push_back(e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.buf);
                }
                break;
            case 4: // act_def_fmt_4
                act_def_format4_size = {e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.count};
                for (size_t j = 0; j < act_def_format4_size; j++)
                {
                    act_def_format4.push_back(e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.buf);
                }
                break;
            case 5: // act_def_fmt_5
                act_def_format5_size = {e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.count};
                for (size_t j = 0; j < act_def_format5_size; j++)
                {
                    act_def_format5.push_back(e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->measInfo_Action_List.list.array[j]->measName.buf);
                }
                break;
            default:
                printf("[WARN] Unknown action definition format %ld!", e2smKpmRanFunctDescrip->ric_ReportStyle_List->list.array[i]->ric_ActionFormat_Type);
                break;
            }
        }
    } else
    {
        printf("[WARN] E2SM KPM RAN Function Description decode failed rval.code = %d \n", code);
    }

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
