from pymongo import MongoClient

class MongoConnection:
    _client = None

    @classmethod
    def initialize(cls, uri):
        """
        Inicializa a conexão com o MongoDB.
        :param uri: URI de conexão com o MongoDB.
        """
        if cls._client is None:
            print("Inicializando conexão com MongoDB...")
            cls._client = MongoClient(uri)
        else:
            print("Conexão com MongoDB já inicializada.")

    @classmethod
    def get_client(cls):
        """
        Retorna a instância do cliente MongoDB.
        """
        if cls._client is None:
            raise Exception("A conexão com o MongoDB não foi inicializada.")
        return cls._client

    @classmethod
    def get_database(cls, database_name="open5gs"):
        """
        Retorna o banco de dados especificado.
        """
        return cls.get_client()[database_name]

    @classmethod
    def get_collection(cls, collection_name="subscribers"):
        """
        Retorna a coleção especificada.
        """
        return cls.get_database()[collection_name]

    @classmethod
    def close(cls):
        """
        Encerra a conexão com o MongoDB.
        """
        if cls._client:
            cls._client.close()
            cls._client = None
            print("Conexão com MongoDB encerrada.")
