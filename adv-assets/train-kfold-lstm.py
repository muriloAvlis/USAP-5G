import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import SMOTE
from sklearn.metrics import classification_report, confusion_matrix
import os

# FUNÇÃO AUXILIAR PARA DATA AUGMENTATION
def augment_syn_attack(data, noise=0.01):
    return data + noise * np.random.randn(*data.shape)

# FUNÇÃO PARA CONSTRUIR MODELO LSTM
def build_lstm(input_shape):
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=input_shape),
        Dropout(0.3),
        LSTM(32, return_sequences=False),
        Dropout(0.3),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])
    return model

# 1. CARREGAR O DATASET
df = pd.read_csv('/home/victor/test-victor/datasets/fix-dataset/dataset_sem_colunas.csv')

# 2. DEFINIR FEATURES E LABELS
features = ['IndLatency', 'DRB.UEThpDl', 'DRB.UEThpUl']
X = df[features].values
y = df['label'].values

# 3. SETUP DO K-FOLD
n_splits = 5
skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

fold = 1
for train_index, test_index in skf.split(X, y):
    print(f"\n🔁 Fold {fold}")

    # DIVIDIR EM TREINO E TESTE PARA O FOLD ATUAL
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]

    # NORMALIZAR
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # OVERSAMPLING COM SMOTE
    smote = SMOTE(sampling_strategy=0.2, random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

    # AUGMENTAÇÃO
    X_aug = augment_syn_attack(X_train_resampled[y_train_resampled == 1])
    X_train_augmented = np.vstack([X_train_resampled, X_aug])
    y_train_augmented = np.hstack([y_train_resampled, np.ones(len(X_aug))])

    # CLASS WEIGHTS
    class_weights = compute_class_weight('balanced', classes=np.unique(y_train_augmented), y=y_train_augmented)
    class_weights_dict = {0: class_weights[0], 1: class_weights[1]}

    # REFORMATAR PARA LSTM
    X_train_augmented_lstm = X_train_augmented.reshape((X_train_augmented.shape[0], X_train_augmented.shape[1], 1))
    X_test_lstm = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

    # SALVAR DADOS DO FOLD
    os.makedirs(f'/home/victor/test-victor/experimentos/fold_{fold}', exist_ok=True)
    pd.DataFrame(np.hstack([X_train_augmented, y_train_augmented.reshape(-1, 1)]), columns=features + ['label']).to_csv(
        f'/home/victor/test-victor/experimentos/fold_{fold}/train_data.csv', index=False)
    pd.DataFrame(np.hstack([X_test, y_test.reshape(-1, 1)]), columns=features + ['label']).to_csv(
        f'/home/victor/test-victor/experimentos/fold_{fold}/test_data.csv', index=False)

    # CONSTRUIR E TREINAR MODELO
    model = build_lstm((X_train_augmented_lstm.shape[1], 1))
    model.fit(X_train_augmented_lstm, y_train_augmented,
              epochs=20, batch_size=32,
              validation_data=(X_test_lstm, y_test),
              class_weight=class_weights_dict)

    # AVALIAÇÃO
    y_pred = model.predict(X_test_lstm).flatten()
    y_pred_labels = (y_pred > 0.5).astype(int)

    print("\nRelatório de Classificação:")
    print(classification_report(y_test, y_pred_labels))

    cm = confusion_matrix(y_test, y_pred_labels)
    tn, fp, fn, tp = cm.ravel()
    print("\nMatriz de Confusão:")
    print(cm)
    print(f"🔹 Falso Positivo (FP): {fp}")
    print(f"🔹 Falso Negativo (FN): {fn}")

    # SALVAR MODELO
    model.save(f"/home/victor/test-victor/experimentos/fold_{fold}/lstm_model_fold{fold}.keras")

    fold += 1
