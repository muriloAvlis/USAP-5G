import os
import numpy as np
import signal

from usap_smc.logger.logger import Log
from tensorflow.keras.models import load_model

from loguru import logger


class Model(object):
    def __init__(self):
        # Caminho para o modelo LSTM
        my_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = my_dir + "/models/oran-lstm.keras"
        self.model = None

        # Load model
        logger.info("Carregando modelo...")
        try:
            self.model = load_model(model_path)

            logger.info("Modelo carregado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao carregar o modelo: {e}")
            # Gera um sinal de interrupção da aplicação
            signal.raise_signal(signal.SIGINT)

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
                f"Resultado da inferência: SST={sst_inference} para o UE={imsi}")

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


# For tests
if __name__ == "__main__":
    data = [[0, 0, 200], [0, 0, 150]]
    model = Model()
    sst = model.get_sst_inference(data, "000000000000001")
