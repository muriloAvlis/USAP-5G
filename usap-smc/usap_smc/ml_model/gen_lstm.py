import numpy as np
import pandas as pd
import os
import shutil

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split
from keras_tuner import Hyperband
from sklearn.metrics import classification_report


class GenModel(object):
    def __init__(self):
        # Params
        self.test_size = 0.3
        self.num_classes = 4

        self.samples_per_block = 5
        self.max_epochs_tunner = 3000
        self.epochs_model = 1000
        self.model_patience = 100
        self.factor = 3

        features = [
            'tx_brate downlink (kbps)', 'rx_brate uplink (kbps)', 'sum_granted_prbs']

        self.my_dir = os.path.dirname(os.path.abspath(__file__))

        tuning_dir = os.path.abspath("hyperband_tuning")
        if os.path.exists(tuning_dir):
            print(f"Removendo a pasta existente {tuning_dir}")
            shutil.rmtree(tuning_dir)

        # load data
        self.df = pd.read_csv(self.my_dir + "/data/oran-ds.csv")

        X_lstm, y_lstm = self.create_time_blocks(
            self.df, 'ue_id', features, self.samples_per_block)

        # Preprocess data
        self.preprocess_data(X_lstm, y_lstm)

    def create_time_blocks(self, df, ue_id_col, features, block_size):
        df_sorted = df.sort_values(by=[ue_id_col, 'Timestamp'])
        ue_ids = df_sorted[ue_id_col].unique()

        blocks = []
        targets = []

        for ue_id in ue_ids:
            ue_data = df_sorted[df_sorted[ue_id_col] == ue_id]
            ue_values = ue_data[features].values
            num_records = len(ue_values)

            for start_idx in range(0, num_records - block_size + 1, block_size):
                end_idx = start_idx + block_size
                if end_idx <= num_records:
                    block = ue_values[start_idx:end_idx]
                    target = ue_data.iloc[end_idx - 1]['slice_target']
                    blocks.append(block)
                    targets.append(target)

        return np.array(blocks), np.array(targets)

    def preprocess_data(self, X_lstm, y_lstm):
        y_categorical = to_categorical(y_lstm, num_classes=self.num_classes)
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X_lstm, y_categorical, test_size=self.test_size, random_state=42)

    def build_params(self, hp):
        model = Sequential()
        model.add(
            LSTM(
                units=hp.Int('units', min_value=32, max_value=512,
                             step=16),  # Unidades LSTM
                activation=hp.Choice('activation', values=[
                                     'relu', 'tanh']),  # Função de ativação
                input_shape=(self.X_train.shape[1], self.X_train.shape[2]),
            )
        )
        model.add(Dense(self.num_classes, activation='softmax'))
        model.compile(
            optimizer=tf.keras.optimizers.Adam(
                learning_rate=hp.Choice('learning_rate', values=[
                                        1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8, 1e-9])  # Taxa de aprendizado
            ),
            loss='categorical_crossentropy',
            metrics=['accuracy'],
        )
        return model

    def build_model(self):
        # Inicializar o tuner
        tuner = Hyperband(
            self.build_params,
            objective='val_accuracy',
            max_epochs=self.max_epochs_tunner,
            factor=self.factor,
            directory='hyperband_tuning',
            project_name='lstm_tuning',
        )

        # Treinar o modelo com tuning
        tuner.search(self.X_train, self.y_train, validation_split=0.2,
                     epochs=self.max_epochs_tunner, verbose=1)

        # Melhor modelo encontrado
        best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]

        print(f"""
        Melhores hiperparâmetros:
        - Unidades LSTM: {best_hps.get('units')}
        - Função de ativação: {best_hps.get('activation')}
        - Taxa de aprendizado: {best_hps.get('learning_rate')}
        """)

        # Treinar o melhor modelo com os dados
        model = tuner.hypermodel.build(best_hps)

        # Configurando o Early Stopping
        early_stopping = EarlyStopping(
            # Pode ser 'val_loss'
            monitor='val_accuracy',
            # Número de épocas sem melhoria antes de parar
            patience=self.model_patience,
            restore_best_weights=True  # Restaura os pesos do modelo na melhor época
        )

        history = model.fit(self.X_train, self.y_train,
                            validation_split=0.2, epochs=self.epochs_model, callbacks=[early_stopping], verbose=1)

        model.save(self.my_dir + "/models/oran-lstm.keras")

        return model

    def model_evaluate(self, model):
        # Avaliar no conjunto de teste
        loss, accuracy = model.evaluate(self.X_test, self.y_test, verbose=0)
        print(f'Loss: {loss}')
        print(f'Accuracy: {accuracy}')

        # Fazer previsões no conjunto de teste
        y_pred = model.predict(self.X_test)
        # Converter para rótulos (se one-hot)
        y_pred_classes = y_pred.argmax(axis=1)
        y_true_classes = self.y_test.argmax(axis=1)

        print("Relatório de classificação:")
        print(classification_report(y_true_classes, y_pred_classes))


if __name__ == "__main__":
    genModel = GenModel()

    model = genModel.build_model()

    genModel.model_evaluate(model)
