import random
import threading
import time
from bson import ObjectId
from usap_smc.core5g.config.database import MongoConnection

def create_ue():
    """
    Cria uma nova UE automaticamente.
    """
    collection = MongoConnection.get_collection()

    # Gerar IMSI único
    imsi = f"{random.randint(100000000000000, 999999999999999)}"

    ue_data = {
        "_id": ObjectId(),
        "schema_version": 1,
        "imsi": imsi,
        "msisdn": [],
        "imeisv": [],
        "mme_host": [],
        "mm_realm": [],
        "purge_flag": [],
        "slice": [
            {
                "sst": random.randint(0, 999),
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

    result = collection.insert_one(ue_data)
    print(f"Nova UE criada com IMSI: {imsi}")
    return imsi




def start_create():
    """
    Inicia a tarefa de criação e exclusão de UEs.
    """
    def task():
        while True:
            imsi = create_ue()  # Cria a UE
            time.sleep(20)  # Espera 20 segundos
            from core5g.delete import delete_ue
            delete_ue(imsi)  # Deleta a UE
            time.sleep(20)  # Espera antes de criar outra

    threading.Thread(target=task, daemon=True).start()
