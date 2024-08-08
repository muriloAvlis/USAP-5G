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
#include "defer.h"


typedef struct eventTriggerFmt
{
    u_int64_t * buffer;
    int size;
} eventTriggerFmt_t;

eventTriggerFmt_t encodeEventTriggerDefinitionFormat1(u_int64_t reportingPeriod)
{Deferral
    eventTriggerFmt_t res = {NULL, 0};
    E2SM_KPM_EventTriggerDefinition_t *evTriggerDef = (E2SM_KPM_EventTriggerDefinition_t *)calloc(1, sizeof(E2SM_KPM_EventTriggerDefinition_t));
    if (evTriggerDef == NULL)
    {
        fprintf(stderr, "[ERROR] E2SM_KPM_EventTriggerDefinition memory allocation failure!");
        return res;
    }

    // allocate memory to EventTriggerDefinitionFormat1
    evTriggerDef->eventDefinition_formats.choice.eventDefinition_Format1 = (E2SM_KPM_EventTriggerDefinition_Format1_t *)calloc(1, sizeof(E2SM_KPM_EventTriggerDefinition_Format1_t));
    if (evTriggerDef->eventDefinition_formats.choice.eventDefinition_Format1 == NULL)
    {
        fprintf(stderr, "[ERROR] E2SM_KPM_EventTriggerDefinition_Format1 memory allocation failure!");
        ASN_STRUCT_FREE(asn_DEF_E2SM_KPM_EventTriggerDefinition, evTriggerDef);
        return res;
    }

    // set format 1
    evTriggerDef->eventDefinition_formats.present = E2SM_KPM_EventTriggerDefinition__eventDefinition_formats_PR_eventDefinition_Format1;
    // set reporting period
    evTriggerDef->eventDefinition_formats.choice.eventDefinition_Format1->reportingPeriod = reportingPeriod;

    // create a buffer
    size_t buffer_size = 1024; // is a correct value?
    void *buffer = malloc(buffer_size);
    Defer(free(buffer));
    if (buffer == NULL)
    {
        fprintf(stderr, "[ERROR] Memory allocation failed!\n");
        return res;
    }

    asn_enc_rval_t enc_res = aper_encode_to_buffer(&asn_DEF_E2SM_KPM_EventTriggerDefinition, NULL, evTriggerDef, buffer, buffer_size);
    ASN_STRUCT_FREE(asn_DEF_E2SM_KPM_EventTriggerDefinition, evTriggerDef);
    if (enc_res.encoded == -1)
    {
        fprintf(stderr, "[ERROR] Failed to encode EventTriggerDefinition!\n");
        return res;
    }

    // alloc to correct size
    void * f_buf = realloc(buffer, enc_res.encoded);
    Defer(free(f_buf));
    if (f_buf == NULL)
    {
        fprintf(stderr, "[ERROR] Memory reallocation failed!\n");
        return res;
    }

    res.size = (enc_res.encoded + sizeof(u_int64_t) - 1) / sizeof(u_int64_t); // Calculate number of uint64_t elements
    res.buffer = (u_int64_t *)malloc(res.size * sizeof(u_int64_t));
    if (res.buffer == NULL)
    {
        fprintf(stderr, "[ERROR] Memory allocation failed!\n");
        return res;
    }

    memcpy(res.buffer, f_buf, enc_res.encoded);

    return res;
}

int main(){
    eventTriggerFmt_t res = encodeEventTriggerDefinitionFormat1(1000);
    if (res.buffer != NULL)
    {
        printf("Encoded size: %d\n", res.size);
        printf("Encoded buffer: ");
        for (int i = 0; i < res.size; i++)
        {
            printf("%016lX", res.buffer[i]);
        }
        printf("\n");
        free(res.buffer);
    }
    else
    {
        fprintf(stderr, "Failed to encode event trigger definition.\n");
    }
    return 0;
}