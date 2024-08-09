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
    u_int8_t * buffer;
    size_t size;
} eventTriggerFmt_t;

eventTriggerFmt_t encodeEventTriggerDefinitionFormat1(u_int64_t reportingPeriod)
{Deferral
    // Initialize the result
    eventTriggerFmt_t encoded = {NULL, 0};

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
    size_t buffer_size = 64;
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
    encoded.buffer = (u_int8_t *)calloc(1, encoded.size);
    for (size_t i = 0; i < encoded.size; i++) {
        encoded.buffer[i] = buffer[i];
    }

    return encoded;
}

int main() {Deferral
    eventTriggerFmt_t eventTriggerFmt1 = encodeEventTriggerDefinitionFormat1(100000000);
    printf("%zu bytes encodeds\n", eventTriggerFmt1.size);
    for (size_t i = 0; i < eventTriggerFmt1.size; i++) {
        printf("%d ", eventTriggerFmt1.buffer[i]);
    }
    printf("\n");

    return 0;
}