from bson import ObjectId

DEFAULT_UE = {
    "_id": ObjectId(),
    "schema_version": 1,
    "imsi": "000000000000000",
    "msisdn": [],
    "imeisv": [],
    "mme_host": [],
    "mm_realm": [],
    "purge_flag": [],
    "slice": [
            {
                "sst": 128,
                "sd": "FFFFFF",
                "default_indicator": True,
                "session": [],
                "_id": ObjectId()
            }
    ],
    "security": {
        "k": "465B5CE8B199B49FAA5F0A2EE238A6BC",
        "op": None,
        "opc": "E8ED289DEBA952E4283B54E88E6183CA",
        "amf": "8000"
    },
    "ambr": {
        "downlink": {"value": 1000000000, "unit": 0},
        "uplink": {"value": 1000000000, "unit": 0}
    },
    "access_restriction_data": 32,
    "network_access_mode": 0,
    "subscriber_status": 0,
    "__v": 0
}
