//
// Created by murilo on 1/14/25.
//

#ifndef WRAPPER_H
#define WRAPPER_H

#include <stdio.h>
#include <stdlib.h>
#include "RICsubscriptionRequest.h"
#include "RICsubscriptionResponse.h"
#include "RICsubscriptionDeleteRequest.h"
#include "RICsubscriptionDeleteResponse.h"
#include "RICcontrolRequest.h"
#include "RICindication.h"
#include "E2AP-PDU.h"
#include "InitiatingMessage.h"
#include "SuccessfulOutcome.h"
#include "UnsuccessfulOutcome.h"
#include "ProtocolIE-Container.h"
#include "ProtocolIE-Field.h"
#include "RICactionDefinition.h"
#include "RICsubsequentAction.h"
#include "CauseE2node.h"
#include "Cause.h"
#include "CauseMisc.h"
#include "CauseProtocol.h"
#include "CauseRICrequest.h"
#include "CauseRICservice.h"
#include "CauseTransport.h"
#include "RICsubscription-List-withCause.h"
#include "RICsubscription-withCause-Item.h"

typedef struct RICindicationMessage {
    long requestorID;
    long requestSequenceNumber;
    long ranfunctionID;
    long actionID;
    long indicationSN;
    long indicationType;
    uint8_t *indicationHeader;
    size_t indicationHeaderSize;
    uint8_t *indicationMessage;
    size_t indicationMessageSize;
    uint8_t *callProcessID;
    size_t callProcessIDSize;
} RICindicationMsg;

RICindicationMsg* e2ap_decode_ric_indication_message(void *buffer, size_t buf_size);

void e2ap_free_decoded_ric_indication_message(RICindicationMsg* msg);

#endif //WRAPPER_H
