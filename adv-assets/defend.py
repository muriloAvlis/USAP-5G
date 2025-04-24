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

# Setup
current_dir = os.getcwd()
df = pd.read_csv(current_dir + "/assets/datasets/fix-dataset/dataset_sem_colunas.csv")
features = ['IndLatency', 'DRB.UEThpDl', 'DRB.UEThpUl']
X = df[features].values
y = df['label'].values

# Utilitários
def augment_syn_attack(data, noise=0.01):
    return data + noise * np.random.randn(*data.shape)

def build_lstm(input_shape):
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=input_shape),
        Dropout(0.3),
        LSTM(32),
        Dropout(0.3),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer=Adam(0.001), loss='binary_crossentropy', metrics=['accuracy'])
    return model

def create_adversarial_pattern(input_data, target_label, model, epsilon, method="fgsm", alpha=0.01, iters=40):
    input_tensor = tf.convert_to_tensor(input_data, dtype=tf.float32)
    target_tensor = tf.convert_to_tensor(target_label, dtype=tf.float32)

    if method == "fgsm":
        with tf.GradientTape() as tape:
            tape.watch(input_tensor)
            prediction = model(input_tensor, training=False)
            loss = tf.keras.losses.binary_crossentropy(target_tensor, prediction)
        gradient = tape.gradient(loss, input_tensor)
        return tf.clip_by_value(input_tensor + epsilon * tf.sign(gradient), -1, 1)

    elif method == "pgd":
        adv = tf.Variable(input_tensor)
        for _ in range(iters):
            with tf.GradientTape() as tape:
                tape.watch(adv)
                prediction = model(adv, training=False)
                loss = tf.keras.losses.binary_crossentropy(target_tensor, prediction)
            gradient = tape.gradient(loss, adv)
            adv.assign_add(alpha * tf.sign(gradient))
            perturb = tf.clip_by_value(adv - input_tensor, -epsilon, epsilon)
            adv.assign(tf.clip_by_value(input_tensor + perturb, -1, 1))
        return adv

# K-Fold + Treinamento
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
fold = 1
recall_scores = []
best_model = None
tempo_total = 0
tempos_folds = []
epsilon_values = [0.1, 0.2, 0.3]

for train_idx, val_idx in skf.split(X, y):
    print(f"\n🔁 Fold {fold}")
    start_time = time.time()

    X_train, X_val = X[train_idx], X[val_idx]
    y_train, y_val = y[train_idx], y[val_idx]

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)

    smote = SMOTE(sampling_strategy=0.2, random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

    X_aug = augment_syn_attack(X_resampled[y_resampled == 1])
    X_train_aug = np.vstack([X_resampled, X_aug])
    y_train_aug = np.hstack([y_resampled, np.ones(len(X_aug))])

    class_weights = compute_class_weight('balanced', classes=np.unique(y_train_aug), y=y_train_aug)
    class_weights_dict = {0: class_weights[0], 1: class_weights[1]}

    X_train_lstm = X_train_aug.reshape((X_train_aug.shape[0], X_train_aug.shape[1], 1))
    X_val_lstm = X_val.reshape((X_val.shape[0], X_val.shape[1], 1))

    # Modelo base
    model = build_lstm((X_train_lstm.shape[1], 1))
    model.fit(X_train_lstm, y_train_aug, epochs=20, batch_size=128,
              validation_data=(X_val_lstm, y_val),
              class_weight=class_weights_dict)

    # Adversarial training
    X_attack = X_val_lstm[y_val == 1]
    y_attack = np.ones(len(X_attack))

    X_fgsm_total, X_pgd_total = [], []
    for eps in epsilon_values:
        X_fgsm_eps = np.vstack([
            create_adversarial_pattern(X_attack[i:i+1], [[1.]], model, epsilon=eps, method="fgsm").numpy()
            for i in range(len(X_attack))
        ])
        X_pgd_eps = np.vstack([
            create_adversarial_pattern(X_attack[i:i+1], [[1.]], model, epsilon=eps, method="pgd").numpy()
            for i in range(len(X_attack))
        ])
        X_fgsm_total.append(X_fgsm_eps)
        X_pgd_total.append(X_pgd_eps)

    X_fgsm = np.vstack(X_fgsm_total)
    X_pgd = np.vstack(X_pgd_total)

    X_defended = np.vstack([X_train_lstm, X_fgsm, X_pgd])
    y_defended = np.hstack([y_train_aug, np.ones(len(X_fgsm) + len(X_pgd))])

    model_defended = build_lstm((X_train_lstm.shape[1], 1))
    model_defended.fit(X_defended, y_defended, epochs=20, batch_size=128,
                       validation_data=(X_val_lstm, y_val),
                       class_weight=class_weights_dict)

    # Avaliação
    y_pred = model_defended.predict(X_val_lstm).flatten()
    y_pred_labels = (y_pred > 0.5).astype(int)
    report = classification_report(y_val, y_pred_labels, output_dict=True)
    cm = confusion_matrix(y_val, y_pred_labels)
    recall = report['1']['recall']
    recall_scores.append(recall)

    os.makedirs(f"{current_dir}/experimentos_defesa/fold_{fold}", exist_ok=True)
    pd.DataFrame(report).transpose().to_csv(f"{current_dir}/experimentos_defesa/fold_{fold}/classification_report.csv")
    pd.DataFrame(cm, index=['Real:0', 'Real:1'], columns=['Pred:0', 'Pred:1']).to_csv(f"{current_dir}/experimentos_defesa/fold_{fold}/confusion_matrix.csv")
    model_defended.save(f"{current_dir}/experimentos_defesa/fold_{fold}/lstm_defended_fold{fold}.keras")

    if recall == max(recall_scores):
        best_model = model_defended
        best_fold = fold

    end_time = time.time()
    tempo_total += (end_time - start_time)
    tempos_folds.append({'Fold': fold, 'Tempo (s)': end_time - start_time})
    fold += 1

# Final
tempos_folds.append({'Fold': 'Total', 'Tempo (s)': tempo_total})
pd.DataFrame(tempos_folds).to_csv(f"{current_dir}/experimentos_defesa/tempos_folds.csv", index=False)

print(f"\n🌟 Melhor Fold (baseado em Recall): {best_fold}")
best_model.save(f"{current_dir}/experimentos_defesa/best_defended_model.keras")
print("✅ Modelo defendido com melhor recall salvo.")