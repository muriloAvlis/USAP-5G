import numpy as np
import pandas as pd
import joblib

from pathlib import Path
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.utils.class_weight import compute_class_weight
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping


class Model(object):
    def __init__(self):
        self.local_path = Path(__file__).resolve().parent
        file_path = self.local_path.parent / \
            'data/oran-dataset-slice-traffic.csv'
        self.df = pd.read_csv(file_path)

        # Data preprocessor
        self.scaler = MinMaxScaler()

        # Encoder
        self.label_encoder = LabelEncoder()

        self.__pre_processing_data()

    def __create_default_slice(self):
        mask = (self.df["tx_brate_downlink_kbps"] == 0) & \
            (self.df["tx_pkts_downlink"] == 0) & \
            (self.df["rx_brate_uplink_kbps"] == 0) & \
            (self.df["rx_pkts_uplink"] == 0)

        self.df.loc[mask, "slice_target"] = 128

    # data for train, validation and tests
    def __pre_processing_data(self):
        # Rename columns
        self.df.rename(
            columns={
                "tx_brate downlink (kbps)": "tx_brate_downlink_kbps",
                "tx_pkts downlink": "tx_pkts_downlink",
                "rx_brate uplink (kbps)": "rx_brate_uplink_kbps",
                "rx_pkts uplink": "rx_pkts_uplink"  # and slice_target
            }, inplace=True)

        # create a default slice in ds
        self.__create_default_slice()

        X = self.df.drop("slice_target", axis=1).values

        # Normalization data
        X_scaled = self.scaler.fit_transform(X)
        self.y = self.df["slice_target"].values
        joblib.dump(self.scaler, self.local_path /
                    "compiled/scaler.pkl")  # export scaler

        # Encode Y
        self.y = self.label_encoder.fit_transform(self.y)
        # export encoder
        joblib.dump(self.label_encoder, Path(
            __file__).resolve().parent / "compiled/label_encoder.pkl")

        # Split data (train and validation)
        self.X_train, self.X_val, self.y_train, self.y_val = train_test_split(
            X_scaled, self.y, test_size=0.2, random_state=42)

    def train_dnn_model(self):
        # Calcule class weights
        class_weights = compute_class_weight(
            "balanced", classes=np.unique(self.y_train), y=self.y_train)
        class_weights = dict(enumerate(class_weights))

        # Build model
        self.model = Sequential([
            Input(shape=(self.X_train.shape[1],)),  # input with X_columns neurons
            Dense(512, activation="relu"),
            Dropout(0.3),  # reduces overfitting by deactivating 30% of neurons
            Dense(512, activation="relu"),
            Dropout(0.3),
            Dense(256, activation="relu"),
            Dropout(0.3),
            Dense(128, activation="relu"),
            Dropout(0.2),
            Dense(64, activation="relu"),
            Dense(4, activation="softmax")
        ])

        # model parameters
        learning_rate = 0.001
        batch_size = 32
        epochs = 100
        opt = Adam(learning_rate=learning_rate)  # optimizer

        # Compile model
        self.model.compile(loss="sparse_categorical_crossentropy",
                           optimizer=opt, metrics=["accuracy"])

        # stop training if validation does not improve
        early_stopping = EarlyStopping(
            monitor='val_loss', patience=15, restore_best_weights=True)

        # train model
        self.model.fit(self.X_train, self.y_train, epochs=epochs,
                       batch_size=batch_size, class_weight=class_weights, validation_split=0.1, callbacks=[early_stopping])

    def export_dnn_model(self):
        if self.model != None:
            self.model.save(self.local_path /
                            "compiled/dnn_model.keras", overwrite=True)
            print("DNN model exported in ./compiled/dnn_model.keras path")


# Training process
if __name__ == "__main__":
    model = Model()
    model.train_dnn_model()
    model.export_dnn_model()