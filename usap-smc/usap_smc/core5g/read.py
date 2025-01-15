from usap_smc.core5g.config.database import MongoConnection
import threading
import time

def get_all_ues():
    """
    Retorna todas as UEs armazenadas no banco de dados, com tempo de execução em milissegundos.
    """
    collection = MongoConnection.get_collection()

    # Início da medição de tempo
    start_time = time.time()
    ues = list(collection.find())
    # Fim da medição de tempo
    end_time = time.time()

    # Calcula o tempo total da requisição em milissegundos
    elapsed_time_ms = (end_time - start_time) * 1000
    print(f"Tempo para obter UEs: {elapsed_time_ms:.3f} ms")

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
