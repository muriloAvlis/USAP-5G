//
// Created by murilo on 1/14/25.
//

#include "wrapper.h"

E2AP_PDU_t* decode_E2AP_PDU(const void* buffer, size_t buf_size)
{
    asn_dec_rval_t decode_result;
    E2AP_PDU_t *pdu = 0;
    decode_result = aper_decode_complete(NULL, &asn_DEF_E2AP_PDU, (void **)&pdu, buffer, buf_size);
    if(decode_result.code == RC_OK) {
        return pdu;
    } else {
        ASN_STRUCT_FREE(asn_DEF_E2AP_PDU, pdu);
        return 0;
    }
}

/* RICindication */

RICindicationMsg* e2ap_decode_ric_indication_message(void *buffer, size_t buf_size)
{
    E2AP_PDU_t *pdu = decode_E2AP_PDU(buffer, buf_size);
    if ( pdu != NULL && pdu->present == E2AP_PDU_PR_initiatingMessage)
    {
        InitiatingMessage_t* initiatingMessage = pdu->choice.initiatingMessage;
        if ( initiatingMessage->procedureCode == ProcedureCode_id_RICindication
            && initiatingMessage->value.present == InitiatingMessage__value_PR_RICindication)
        {
            RICindication_t *indication = &(initiatingMessage->value.choice.RICindication);
            RICindicationMsg *msg = (RICindicationMsg *)calloc(1, sizeof(RICindicationMsg));
            for (int i = 0; i < indication->protocolIEs.list.count; ++i )
            {
                if (indication->protocolIEs.list.array[i]->id == ProtocolIE_ID_id_RICrequestID) {
                    msg->requestorID = indication->protocolIEs.list.array[i]->value.choice.RICrequestID.ricRequestorID;
                    msg->requestSequenceNumber = indication->protocolIEs.list.array[i]->value.choice.RICrequestID.ricInstanceID;
                }
                else if (indication->protocolIEs.list.array[i]->id == ProtocolIE_ID_id_RANfunctionID) {
                    msg->ranfunctionID = indication->protocolIEs.list.array[i]->value.choice.RANfunctionID;
                }
                else if (indication->protocolIEs.list.array[i]->id == ProtocolIE_ID_id_RICactionID) {
                    msg->actionID = indication->protocolIEs.list.array[i]->value.choice.RICactionID;
                }
                else if(indication->protocolIEs.list.array[i]->id == ProtocolIE_ID_id_RICindicationSN) {
                    msg->indicationSN = indication->protocolIEs.list.array[i]->value.choice.RICindicationSN;
                }
                else if(indication->protocolIEs.list.array[i]->id == ProtocolIE_ID_id_RICindicationType) {
                    msg->indicationType = indication->protocolIEs.list.array[i]->value.choice.RICindicationType;
                }
                else if(indication->protocolIEs.list.array[i]->id == ProtocolIE_ID_id_RICindicationHeader) {
                    size_t headerSize = indication->protocolIEs.list.array[i]->value.choice.RICindicationHeader.size;
                    msg->indicationHeader = calloc(1, headerSize);
                    if (!msg->indicationHeader) {
                        fprintf(stderr, "alloc RICindicationHeader failed\n");
                        e2ap_free_decoded_ric_indication_message(msg);
                        ASN_STRUCT_FREE(asn_DEF_E2AP_PDU, pdu);
                        return NULL;
                    }

                    memcpy(msg->indicationHeader, indication->protocolIEs.list.array[i]->value.choice.RICindicationHeader.buf, headerSize);
                    msg->indicationHeaderSize = headerSize;
                }
                else if(indication->protocolIEs.list.array[i]->id == ProtocolIE_ID_id_RICindicationMessage) {
                    size_t messsageSize = indication->protocolIEs.list.array[i]->value.choice.RICindicationMessage.size;
                    msg->indicationMessage = calloc(1, messsageSize);
                    if (!msg->indicationMessage) {
                        fprintf(stderr, "alloc RICindicationMessage failed\n");
                        e2ap_free_decoded_ric_indication_message(msg);
                        ASN_STRUCT_FREE(asn_DEF_E2AP_PDU, pdu);
                        return NULL;
                    }

                    memcpy(msg->indicationMessage, indication->protocolIEs.list.array[i]->value.choice.RICindicationMessage.buf, messsageSize);
                    msg->indicationMessageSize = messsageSize;
                }
                else if(indication->protocolIEs.list.array[i]->id == ProtocolIE_ID_id_RICcallProcessID) {
                    size_t callProcessIDSize = indication->protocolIEs.list.array[i]->value.choice.RICcallProcessID.size;
                    msg->callProcessID = calloc(1, callProcessIDSize);
                    if (!msg->callProcessID) {
                        fprintf(stderr, "alloc RICcallProcessID failed\n");
                        e2ap_free_decoded_ric_indication_message(msg);
                        ASN_STRUCT_FREE(asn_DEF_E2AP_PDU, pdu);
                        return NULL;
                    }

                    memcpy(msg->callProcessID, indication->protocolIEs.list.array[i]->value.choice.RICcallProcessID.buf, callProcessIDSize);
                    msg->callProcessIDSize = callProcessIDSize;
                }
            }
            return msg;
        }
    }

    if(pdu != NULL)
        ASN_STRUCT_FREE(asn_DEF_E2AP_PDU, pdu);
    return NULL;
}

void e2ap_free_decoded_ric_indication_message(RICindicationMsg* msg) {
    if(msg == NULL) {
        return;
    }

    if(msg->indicationHeader != NULL) {
        free(msg->indicationHeader);
        msg->indicationHeader = NULL;
    }
    if(msg->indicationMessage != NULL) {
        free(msg->indicationMessage);
        msg->indicationMessage = NULL;
    }
    if(msg->callProcessID != NULL) {
        free(msg->callProcessID);
        msg->callProcessID = NULL;
    }
    free(msg);
    msg = NULL;
}
