from usap_smc.core5g.config.database import MongoConnection
import threading
import time

def get_all_ues():
    """
    Retorna todas as UEs armazenadas no banco de dados.
    """
    collection = MongoConnection.get_collection()
    ues = list(collection.find())
    return ues

def start_read():
    """
    Inicia a tarefa de leitura periódica das UEs.
    """
    def task():
        while True:
            print("Buscando todas as UEs...")
            ues = get_all_ues()
            print(f"Encontradas {len(ues)} UEs.")
            for ue in ues:
                print(f"UE encontrada: IMSI={ue.get('imsi', 'Desconhecido')}")
            time.sleep(30)  # Intervalo de leitura (ajustável)

    threading.Thread(target=task, daemon=True).start()
