import os
import numpy as np
import tensorflow as tf
from usap_smc.logger.logger import Log
from tensorflow.keras.models import load_model
from usap_smc.core5g.update import check_inference_slice
#from usap_smc.client.client import buffer

logger = Log().get_logger()
# Caminho para o modelo LSTM
my_dir = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = my_dir + "lstm-oran.keras"
MODEL = None

def initialize_ia():
    """
    Inicializa o módulo de IA, carregando o modelo.
    """
    global MODEL
    print("Inicializando o módulo de IA...")
    try:
        MODEL = tf.keras.models.load_model(MODEL_PATH)
        print("Modelo carregado com sucesso.")
    except Exception as e:
        print(f"Erro ao carregar o modelo: {e}")

def run_ia_task(buffer):
    """
    Executa a tarefa de IA usando as métricas recebidas do cliente gRPC.
    """
    if MODEL is None:
        print("O modelo não foi inicializado corretamente. Tarefa abortada.")
        return

    # Passo 1: Obter as métricas do gRPC
    # X = np.array(hold)
    # entrada = np.expand_dims(X, axis=0)
    # if entrada is None:
    #     print("Erro ao obter as métricas do gRPC.")
    #     return

    # # Passo 2: Realizar a previsão com o modelo LSTM
    # try:
    #     # Convertendo as métricas para o formato esperado pelo modelo (reshape, normalização, etc)
    #     saida = np.argmax(MODEL.predict(entrada), axis=1)
    #     logger.info(f"Entrada modelo:\n{X}")
    #     logger.info(f"Entrada modelo convertida:\n{entrada}")
    #     logger.info(f"Entrada modelo convertida:\n{entrada}")
    #     logger.info(f"Predição modelo: {saida}")
    # except Exception as e:
    #     print(f"Erro ao fazer a previsão com o modelo: {e}")
    try:
        # Converte o buffer em um array NumPy
        X = np.array(buffer)
        #logger.info(f"Dados recebidos para inferência: {X}")

        # Adiciona a dimensão esperada pelo modelo
        entrada = np.expand_dims(X, axis=0)
        logger.debug(f"Entrada processada: {entrada}")

        # Faz a previsão com o modelo
        sst_inference = np.argmax(MODEL.predict(entrada), axis=1)[0]
        check_inference_slice(sst_inference)
        logger.info(f"Resultado da inferência: {sst_inference}")

    except Exception as e:
        logger.error(f"Erro durante a inferência: {e}")

def close_ia():
    """
    Libera os recursos do módulo de IA.
    """
    print("Encerrando o módulo de IA...")
    global MODEL
    del MODEL  # Libera o modelo carregado
