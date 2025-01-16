from usap_smc.core5g.config.database import MongoConnection
import signal

def initialize_database():
    """
    Inicializa a conexão com o MongoDB.
    """
    MongoConnection.initialize("mongodb://10.126.1.140:32017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.3")
    print("Conexão com MongoDB inicializada.")

def close_database():
    """
    Encerra a conexão com o MongoDB.
    """
    print("Encerrando conexão com MongoDB...")
    MongoConnection.close()
    print("Conexão com MongoDB encerrada.")

def setup_signal_handlers():
    """
    Configura handlers para sinais do sistema, como Ctrl+C.
    """
    def signal_handler(signum, frame):
        close_database()
        exit(0)

    signal.signal(signal.SIGINT, signal_handler)  # Captura Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Captura kill
