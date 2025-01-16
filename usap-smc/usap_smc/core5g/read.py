from usap_smc.core5g.config.database import MongoConnection
from usap_smc.core5g.update import check_slice_ue
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
            for ue in ues:
                imsi = ue.get('imsi', 'Desconhecido')  # Obtém o IMSI ou 'Desconhecido'
                sst_ue = None  # Valor padrão caso não exista o slice ou o sst
            
                # Tenta acessar o valor de 'sst' se existir
                if 'slice' in ue and ue['slice']:
                    sst_ue = ue['slice'][0].get('sst', 'Desconhecido')
                    check_slice_ue(int(sst_ue))
                print(f"UE encontrada: IMSI={imsi}, SST={sst_ue}")
        
            print(f"Encontradas {len(ues)} UEs.")
            time.sleep(30)  # Intervalo de leitura (ajustável)

    threading.Thread(target=task, daemon=True).start()
