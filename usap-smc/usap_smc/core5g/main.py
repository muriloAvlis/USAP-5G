from config.db_manager import initialize_database, close_database, setup_signal_handlers
from core5g.create import start_create
from core5g.update import start_update
from core5g.delete import start_delete
import time

def main():
    # Inicializar o banco de dados
    initialize_database()

    # Configurar signal handlers
    setup_signal_handlers()

    # Iniciar as tarefas de criação, atualização e exclusão
    start_create()
    start_update()
    start_delete()

    # Manter o programa principal ativo
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        close_database()
        exit(0)

if __name__ == "__main__":
    main()
