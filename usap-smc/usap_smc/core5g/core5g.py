from usap_smc.core5g.config.db_manager import initialize_database, close_database, setup_signal_handlers
from usap_smc.core5g.create import start_create
from usap_smc.core5g.update import start_update
from usap_smc.core5g.read import start_read
from usap_smc.client.client import run_client
from usap_smc.core5g.ia_model.IA_module import initialize_ia, run_ia_task, close_ia
import time
import asyncio

def run():
    """
    Função principal do projeto Core5G.
    """
    print("Iniciando o sistema Core5G...")

    # Inicializar o banco de dados
    initialize_database()

    # Configurar signal handlers
    setup_signal_handlers()

    # Iniciar as tarefas
    #start_create()
    #start_update()
    initialize_ia()
    start_read()
    asyncio.run(run_client())
    # Manter o programa principal ativo
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        close_database()
        close_ia
        print("Sistema encerrado com sucesso.")
        exit(0)

if __name__ == "__main__":
    run()
