import random
import threading
import time
from bson import ObjectId
from usap_smc.core5g.config.database import MongoConnection

# Variável global para armazenar a UE fixa
FIXED_UE_IMSI = "001010000000001"

def create_fixed_ue():
    """
    Cria uma UE fixa na coleção se ela ainda não existir.
    """
    collection = MongoConnection.get_collection()

    # Verificar se a UE fixa já existe
    if not collection.find_one({"imsi": FIXED_UE_IMSI}):
        fixed_ue = {
            "_id": ObjectId(),
            "schema_version": 1,
            "imsi": FIXED_UE_IMSI,
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
        collection.insert_one(fixed_ue)
        print(f"UE fixa criada com IMSI: {FIXED_UE_IMSI}")
    else:
        print(f"UE fixa já existe com IMSI: {FIXED_UE_IMSI}")


def create_ue():
    """
    Cria uma nova UE dinamicamente.
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
    Inicia a tarefa de criar e alternar UEs.
    """
    def task():
        create_fixed_ue()  # Garantir que a UE fixa esteja na coleção
        while True:
            # Criar uma nova UE
            imsi = create_ue()
            time.sleep(20)  # Esperar 20 segundos

            # Deletar a UE criada
            from usap_smc.core5g.delete import delete_ue
            delete_ue(imsi)
            time.sleep(20)  # Esperar 20 segundos antes de repetir

    threading.Thread(target=task, daemon=True).start()
