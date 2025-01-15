import random
import threading
import time
from usap_smc.core5g.config.database import MongoConnection


def update_all_slices_sst():
    """
    Atualiza o campo `sst` de todos os assinantes na coleção `subscribers`.
    """
    collection = MongoConnection.get_collection()
    assinantes = collection.find({"slice.0": {"$exists": True}})
    for assinante in assinantes:
        imsi = assinante["imsi"]
        novo_sst = random.randint(0, 999)
        collection.update_one(
            {"imsi": imsi, "slice.0": {"$exists": True}},
            {"$set": {"slice.0.sst": novo_sst}}
        )
        print(f"SST atualizado para {novo_sst} no IMSI {imsi}")


        

def start_update():
    """
    Inicia a tarefa de atualização de SSTs.
    """
    def task():
        while True:
            print("Atualizando todos os SSTs na rede...")
            update_all_slices_sst()
            time.sleep(10)  # Atualiza a cada 10 segundos

    threading.Thread(target=task, daemon=True).start()
