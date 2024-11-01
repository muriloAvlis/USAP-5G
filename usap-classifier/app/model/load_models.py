import os
import joblib
from pathlib import Path

## Disable tf long messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from tensorflow.keras.models import load_model

local_path = Path(__file__).resolve().parent

def load_dnn_model():  # function called in running environment
    model = load_model(local_path / "compiled/dnn_model.keras")
    return model


def load_label_encoder():  # function called in running environment
    label_encoder = joblib.load(local_path / "compiled/label_encoder.pkl")
    return label_encoder


def load_scaler():  # function called in running environment
    scaler = joblib.load(local_path / "compiled/scaler.pkl")
    return scaler
