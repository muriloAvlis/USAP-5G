from usap_smc.core5g.config.database import MongoConnection

def get_all_documents():
    """
    Retorna todos os documentos da coleção `subscribers`.
    """
    collection = MongoConnection.get_collection()  # Acessa a coleção 'subscribers'
    documents = list(collection.find())  # Busca todos os documentos
    return documents
