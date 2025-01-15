import time
from usap_smc.core5g.config.database import MongoConnection

def delete_ue(imsi):
    """
    Remove uma UE específica pelo IMSI, exceto a UE fixa. Mede o tempo de execução.
    """
    FIXED_IMSI = "001010000000001"

    if imsi == FIXED_IMSI:
        print(f"A UE fixa com IMSI {imsi} não pode ser deletada.")
        return

    collection = MongoConnection.get_collection()

    # Medir o tempo de exclusão
    start_time = time.time()
    result = collection.delete_one({"imsi": imsi})
    elapsed_time_ms = (time.time() - start_time) * 1000

    if result.deleted_count > 0:
        print(f"UE com IMSI {imsi} removida em {elapsed_time_ms:.3f} ms.")
    else:
        print(f"Nenhuma UE encontrada com IMSI {imsi}. Tempo gasto: {elapsed_time_ms:.3f} ms.")
