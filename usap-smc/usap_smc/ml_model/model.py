import os
import numpy as np
import tensorflow as tf
from usap_smc.logger.logger import Log
from tensorflow.keras.models import load_model

logger = Log().get_logger()


class Model(object):
    def __init__(self):
        # Caminho para o modelo LSTM
        my_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = my_dir + "/models/lstm-oran.keras"
        self.model = None

        # Load model
        logger.info("Carregando modelo...")
        try:
            self.model = tf.keras.models.load_model(model_path)
            logger.info("Modelo carregado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao carregar o modelo: {e}")

    def get_sst_inference(self, buffer, imsi):
        """
        Executa a tarefa de IA usando as métricas recebidas do cliente gRPC.
        """
        try:
            # Converte o buffer em um array NumPy
            X = np.array(buffer)

            # Adiciona a dimensão esperada pelo modelo
            input = np.expand_dims(X, axis=0)
            logger.debug(
                f"Entrada processada: {input} para a UE com IMSI: {imsi}")

            # Faz a previsão com o modelo
            sst_inference = np.argmax(self.model.predict(input), axis=1)[0]

            logger.info(
                f"Resultado da inferência: sst {sst_inference} para UE: {imsi}")

            return sst_inference

        except Exception as e:
            logger.error(f"Erro durante a inferência: {e}")
            return

    def stop(self):
        """
        Libera os recursos do módulo de IA.
        """
        logger.info("Encerrando o módulo de IA...")
        del self.model
