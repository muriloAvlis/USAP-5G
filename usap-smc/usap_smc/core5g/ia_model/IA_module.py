import os
import numpy as np
import tensorflow as tf
# from usap_smc.client.client import 

# Caminho para o modelo LSTM
MODEL_PATH = "/home/victor/usap-5g/usap-smc/usap_smc/core5g/ia_model/lstm-oran.keras"
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

def run_ia_task():
    """
    Executa a tarefa de IA usando as métricas recebidas do cliente gRPC.
    """
    if MODEL is None:
        print("O modelo não foi inicializado corretamente. Tarefa abortada.")
        return

    # Passo 1: Obter as métricas do gRPC
    metrics = get_metrics_from_grpc()
    if metrics is None:
        print("Erro ao obter as métricas do gRPC.")
        return

    # Passo 2: Realizar a previsão com o modelo LSTM
    try:
        # Convertendo as métricas para o formato esperado pelo modelo (reshape, normalização, etc)
        input_data = np.array([metrics])  # Supondo que as métricas já estejam no formato correto
        prediction = MODEL.predict(input_data)
        print(f"Predição do modelo: {prediction}")
    except Exception as e:
        print(f"Erro ao fazer a previsão com o modelo: {e}")

def close_ia():
    """
    Libera os recursos do módulo de IA.
    """
    print("Encerrando o módulo de IA...")
    global MODEL
    del MODEL  # Libera o modelo carregado
