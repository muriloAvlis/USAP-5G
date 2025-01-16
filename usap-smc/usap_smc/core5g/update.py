import random
import threading
import time
from usap_smc.core5g.config.database import MongoConnection

def check_inference_slice(sst_inference):
    print(f"o slice de inferencia é {sst_inference}")
    check_slice_ue()
    if not sst_inference == hold:
        print(f"Mudar o slice da UE {imsi} de {hold} para {sst_inference}")



def check_slice_ue(imsi,sst_ue):
    print(f"o slice da ue {imsi} é {sst_ue}")
    global hold
    global id
    id = imsi
    hold = sst_ue



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
            #print("Atualizando todos os SSTs na rede...")
            #update_all_slices_sst()
            print("Vamos printar o slice de inferencia")
            #check_inference_slice()
            #time.sleep(10)  # Atualiza a cada 10 segundos

    threading.Thread(target=task, daemon=True).start()
