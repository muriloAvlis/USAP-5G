import threading
import time
from usap_smc.core5g.config.database import MongoConnection


def delete_ue(imsi):
    """
    Remove a UE específica pelo IMSI.
    """
    collection = MongoConnection.get_collection()
    result = collection.delete_one({"imsi": imsi})
    if result.deleted_count > 0:
        print(f"UE com IMSI {imsi} removida.")
    return result.deleted_count

def delete_older_ues():
    """
    Remove UEs mais antigas ou que atendam a um critério específico.
    """
    collection = MongoConnection.get_collection()
    # Exemplo: Deletar UEs criadas há mais de 1 minuto
    result = collection.delete_many({"creation_time": {"$lt": time.time() - 60}})
    print(f"{result.deleted_count} UEs mais antigas removidas.")
    return result.deleted_count




def start_delete():
    """
    Inicia a tarefa de exclusão de UEs com base em critérios específicos.
    """
    def task():
        while True:
            delete_older_ues()  # Exemplo: deletar UEs mais antigas
            time.sleep(30)  # Executa a cada 30 segundos

    threading.Thread(target=task, daemon=True).start()
