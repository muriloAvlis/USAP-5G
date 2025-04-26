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
import time

current_dir = os.getcwd()

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
df = pd.read_csv(current_dir + "/assets/datasets/fix-dataset/dataset_sem_colunas.csv")

# 2. DEFINIR FEATURES E LABELS
#features = ['IndLatency', 'DRB.UEThpDl', 'DRB.UEThpUl']
features = ['IndLatency', 'DRB.AirIfDelayUl', 'DRB.PacketSuccessRateUlgNBUu', 'DRB.RlcDelayUl',
             'DRB.RlcPacketDropRateDl', 'DRB.RlcSduDelayDl', 'DRB.RlcSduTransmittedVolumeDL',
             'DRB.RlcSduTransmittedVolumeUL', 'DRB.UEThpDl', 'DRB.UEThpUl']
X = df[features].values
y = df['label'].values

# 3. SETUP DO K-FOLD
n_splits = 5
skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

fold = 1
tempo_total = 0
tempos_folds = []

# Armazenar métricas de Recall para cada fold
recall_scores = []
best_model = None  # Para salvar o melhor modelo

for train_index, val_index in skf.split(X, y):
    inicio_fold = time.time()
    print(f"\n🔁 Fold {fold}")

    # DIVIDIR EM TREINO E VALIDAÇÃO PARA O FOLD ATUAL
    X_train, X_val = X[train_index], X[val_index]
    y_train, y_val = y[train_index], y[val_index]

    # NORMALIZAR
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)

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
    X_val_lstm = X_val.reshape((X_val.shape[0], X_val.shape[1], 1))

    # SALVAR DADOS DO FOLD
    os.makedirs(f'{current_dir}/experimentos_all_metrics/fold_{fold}', exist_ok=True)
    pd.DataFrame(np.hstack([X_train_augmented, y_train_augmented.reshape(-1, 1)]), columns=features + ['label']).to_csv(
        f'{current_dir}/experimentos_all_metrics/fold_{fold}/train_data.csv', index=False)
    pd.DataFrame(np.hstack([X_val, y_val.reshape(-1, 1)]), columns=features + ['label']).to_csv(
        f'{current_dir}/experimentos_all_metrics/fold_{fold}/val_data.csv', index=False)

    # CONSTRUIR E TREINAR MODELO
    model = build_lstm((X_train_augmented_lstm.shape[1], 1))
    model.fit(X_train_augmented_lstm, y_train_augmented,
              epochs=20, batch_size=128,
              validation_data=(X_val_lstm, y_val),
              class_weight=class_weights_dict)

    # AVALIAÇÃO COM BASE NO CONJUNTO DE VALIDAÇÃO
    y_pred = model.predict(X_val_lstm).flatten()
    y_pred_labels = (y_pred > 0.5).astype(int)

    # Relatório de Classificação e Métricas
    print("\nRelatório de Classificação:")
    print(classification_report(y_val, y_pred_labels))
    report = classification_report(y_val, y_pred_labels, output_dict=True)
    report_df = pd.DataFrame(report).transpose()
    report_df.to_csv(f"{current_dir}/experimentos_all_metrics/fold_{fold}/classification_report.csv", index=True)

    cm = confusion_matrix(y_val, y_pred_labels)
    tn, fp, fn, tp = cm.ravel()
    print("\nMatriz de Confusão:")
    print(cm)
    print(f"Falso Positivo (FP): {fp}")
    print(f"Falso Negativo (FN): {fn}")
    cm_df = pd.DataFrame(cm, index=['Real:0', 'Real:1'], columns=['Pred:0', 'Pred:1'])
    cm_df.to_csv(f"{current_dir}/experimentos_all_metrics/fold_{fold}/confusion_matrix.csv")

    # Salvar o modelo para cada fold (opcional, caso queira analisar mais tarde)
    model.save(f"{current_dir}/experimentos_all_metrics/fold_{fold}/lstm_model_fold{fold}.keras")

    # Armazenar o Recall para escolher o melhor modelo
    report_metrics = report['1']
    recall_scores.append(report_metrics['recall'])

    # Armazenar o melhor modelo
    if recall_scores[-1] == max(recall_scores):
        best_model = model
        best_fold = fold

    final_fold = time.time()
    tempo_fold = final_fold - inicio_fold
    tempos_folds.append({'Fold': fold, 'Tempo (s)': tempo_fold})
    tempo_total += tempo_fold
    fold += 1

# Armazenar o tempo total
tempos_folds.append({'Fold': 'Total', 'Tempo (s)': tempo_total})
tempos_df = pd.DataFrame(tempos_folds)
tempos_df.to_csv(f"{current_dir}/experimentos_all_metrics/tempos_folds.csv", index=False)

# Exibir o melhor fold com base no Recall
print(f"\n🌟 Melhor Fold (baseado em Recall): {best_fold}")

# Salvar o melhor modelo (o que teve maior recall)
best_model.save(f"{current_dir}/experimentos_all_metrics/best_model_with_highest_recall.keras")
print(f"Modelo com melhor recall salvo como: best_model_with_highest_recall.keras")

# Agora, podemos testar o modelo com os dados de validação (ou outro conjunto de dados)
# CARREGAR O MELHOR MODELO SALVO
loaded_model = tf.keras.models.load_model(f"{current_dir}/experimentos_all_metrics/best_model_with_highest_recall.keras")

# Testar o modelo carregado no conjunto de validação de um fold específico
print(f"\nTestando o modelo com o melhor recall no Fold {best_fold}")

X_test, y_test = X[skf.split(X, y).__next__()[1]], y[skf.split(X, y).__next__()[1]]  # Obter um conjunto de validação de exemplo

# Pré-processar o conjunto de dados de teste
X_test = scaler.transform(X_test)
X_test_lstm = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

# Fazer previsões
y_pred_test = loaded_model.predict(X_test_lstm).flatten()
y_pred_labels_test = (y_pred_test > 0.5).astype(int)

# Relatório de Classificação do Teste
print("\nRelatório de Classificação do Teste:")
report_test = classification_report(y_test, y_pred_labels_test, output_dict=True)
report_test_df = pd.DataFrame(report_test).transpose()
report_test_df.to_csv(f"{current_dir}/experimentos_all_metrics/best_model_classification_report.csv", index=True)

# Matriz de Confusão do Teste
cm_test = confusion_matrix(y_test, y_pred_labels_test)
tn_test, fp_test, fn_test, tp_test = cm_test.ravel()
print("\nMatriz de Confusão do Teste:")
print(cm_test)
print(f"Falso Positivo (FP): {fp_test}")
print(f"Falso Negativo (FN): {fn_test}")
cm_test_df = pd.DataFrame(cm_test, index=['Real:0', 'Real:1'], columns=['Pred:0', 'Pred:1'])
cm_test_df.to_csv(f"{current_dir}/experimentos_all_metrics/best_model_confusion_matrix.csv")
