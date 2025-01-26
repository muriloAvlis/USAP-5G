from pymongo import MongoClient
from usap_smc.logger.logger import Log
from usap_smc.utils.utils import get_ip_by_hostname
import signal


from loguru import logger


class MongoConnection(object):
    def __init__(self):
        self._client = None

        # TODO: obter a partir de configuração/values.yaml
        db_hostname = "10.21.2.5"
        db_port = "27017"
        self.uri = "mongodb://" + db_hostname + ":" + db_port + \
            "/?directConnection=true&serverSelectionTimeoutMS=1000&appName=usap-smc"

        self.new_client()

    def new_client(self):
        """
        Inicializa a conexão com o MongoDB.
        :param uri: URI de conexão com o MongoDB.
        """
        if self._client is None:
            try:
                logger.info("Inicializando conexão com MongoDB...")
                self._client = MongoClient(self.uri)
            except Exception as e:
                logger.error(f"Error to initialize MongoDB connection: {e}")
                signal.raise_signal(signal.SIGINT)
        else:
            logger.warning("Conexão com MongoDB já inicializada.")

    def get_client(self):
        """
        Retorna a instância do cliente MongoDB.
        """
        if self._client is None:
            raise Exception("A conexão com o MongoDB não foi inicializada.")
        return self._client

    def get_database(self, database_name="open5gs"):
        """
        Retorna o banco de dados especificado.
        """
        return self.get_client()[database_name]

    def get_collection(self, collection_name="subscribers"):
        """
        Retorna a coleção especificada.
        """
        return self.get_database()[collection_name]

    def close(self):
        """
        Encerra a conexão com o MongoDB.
        """
        if self._client:
            self._client.close()
            self._client = None
            logger.info("Conexão com MongoDB encerrada.")
