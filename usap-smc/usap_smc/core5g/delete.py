import time
from usap_smc.core5g.config.database import MongoConnection

def delete_ue(imsi):
    """
    Remove a UE específica pelo IMSI, exceto a UE fixa.
    """
    FIXED_IMSI = "001010000000001"

    if imsi == FIXED_IMSI:
        print(f"A UE fixa com IMSI {imsi} não pode ser deletada.")
        return

    collection = MongoConnection.get_collection()
    result = collection.delete_one({"imsi": imsi})
    if result.deleted_count > 0:
        print(f"UE com IMSI {imsi} removida.")
    else:
        print(f"Nenhuma UE encontrada com IMSI {imsi}.")
