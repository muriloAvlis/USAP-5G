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

# AUGMENTAÇÃO SINTÉTICA BASEADA EM RUÍDO GAUSSIANO
def augment_syn_attack(data, noise=0.01):
    return data + noise * np.random.randn(*data.shape)

# FGSM (em batch)
def create_adversarial_fgsm_batch(model, X, y, epsilon):
    with tf.GradientTape() as tape:
        tape.watch(X)
        prediction = model(X, training=False)
        loss = tf.keras.losses.binary_crossentropy(y, prediction)
    gradient = tape.gradient(loss, X)
    adv_x = X + epsilon * tf.sign(gradient)
    return tf.clip_by_value(adv_x, -1, 1)

# PGD (em batch)
def create_adversarial_pgd_batch(model, X, y, epsilon, alpha=0.01, num_iter=40):
    adv_x = tf.identity(X)
    for _ in range(num_iter):
        with tf.GradientTape() as tape:
            tape.watch(adv_x)
            prediction = model(adv_x, training=False)
            loss = tf.keras.losses.binary_crossentropy(y, prediction)
        gradient = tape.gradient(loss, adv_x)
        adv_x = adv_x + alpha * tf.sign(gradient)
        adv_x = tf.clip_by_value(adv_x, X - epsilon, X + epsilon)
        adv_x = tf.clip_by_value(adv_x, -1, 1)
    return adv_x

# MODELO LSTM
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

# CARREGAR DATASET
df = pd.read_csv(current_dir + "/assets/datasets/fix-dataset/dataset_sem_colunas.csv")

features = ['IndLatency', 'DRB.UEThpDl', 'DRB.UEThpUl']
X = df[features].values
y = df['label'].values

# K-FOLD SETUP
n_splits = 5
skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

fold = 1
tempo_total = 0
tempos_folds = []
for train_index, test_index in skf.split(X, y):
    inicio_fold = time.time()
    print(f"\n🔁 Fold {fold}")

    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    smote = SMOTE(sampling_strategy=0.2, random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

    X_aug = augment_syn_attack(X_train_resampled[y_train_resampled == 1])
    X_train_augmented = np.vstack([X_train_resampled, X_aug])
    y_train_augmented = np.hstack([y_train_resampled, np.ones(len(X_aug))])

    class_weights = compute_class_weight('balanced', classes=np.unique(y_train_augmented), y=y_train_augmented)
    class_weights_dict = {0: class_weights[0], 1: class_weights[1]}

    X_train_augmented_lstm = X_train_augmented.reshape((X_train_augmented.shape[0], X_train_augmented.shape[1], 1))
    X_test_lstm = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

    model = build_lstm((X_train_augmented_lstm.shape[1], 1))

    epsilon_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    X_all_adv = []
    y_all_adv = []

    X_input_tensor = tf.convert_to_tensor(X_train_augmented_lstm, dtype=tf.float32)
    y_input_tensor = tf.convert_to_tensor(y_train_augmented.reshape(-1, 1), dtype=tf.float32)

    adv_path = f"{current_dir}/experimentos-defesa/fold_{fold}/adversarials"
    os.makedirs(adv_path, exist_ok=True)

    for epsilon in epsilon_values:
        print(f"  Gerando exemplos adversariais com epsilon = {epsilon}")

        X_adv_fgsm = create_adversarial_fgsm_batch(model, X_input_tensor, y_input_tensor, epsilon).numpy()
        X_adv_pgd = create_adversarial_pgd_batch(model, X_input_tensor, y_input_tensor, epsilon, alpha=0.01, num_iter=40).numpy()

        X_all_adv.append(np.vstack([X_adv_fgsm, X_adv_pgd]))
        y_all_adv.append(np.hstack([y_train_augmented, y_train_augmented]))

        pd.DataFrame(X_adv_fgsm.squeeze().reshape(X_adv_fgsm.shape[0], -1), columns=features).to_csv(f"{adv_path}/fgsm_eps_{epsilon}.csv", index=False)
        pd.DataFrame(X_adv_pgd.squeeze().reshape(X_adv_pgd.shape[0], -1), columns=features).to_csv(f"{adv_path}/pgd_eps_{epsilon}.csv", index=False)

    X_adv_combined = np.vstack(X_all_adv)
    y_adv_combined = np.hstack(y_all_adv)

    X_train_combined = np.vstack([X_train_augmented_lstm, X_adv_combined])
    y_train_combined = np.hstack([y_train_augmented, y_adv_combined])

    os.makedirs(f'{current_dir}/experimentos-defesa/fold_{fold}', exist_ok=True)
    pd.DataFrame(np.hstack([X_train_augmented, y_train_augmented.reshape(-1, 1)]), columns=features + ['label']).to_csv(
        f'{current_dir}/experimentos-defesa/fold_{fold}/train_data.csv', index=False)
    pd.DataFrame(np.hstack([X_test, y_test.reshape(-1, 1)]), columns=features + ['label']).to_csv(
        f'{current_dir}/experimentos-defesa/fold_{fold}/test_data.csv', index=False)

    model.fit(
        X_train_combined, y_train_combined,
        epochs=20, batch_size=128,
        validation_data=(X_test_lstm, y_test),
        class_weight=class_weights_dict,
        verbose=1
    )

    y_pred = model.predict(X_test_lstm).flatten()
    y_pred_labels = (y_pred > 0.5).astype(int)

    print("\nRelatório de Classificação:")
    print(classification_report(y_test, y_pred_labels))
    report = classification_report(y_test, y_pred_labels, output_dict=True)
    report_df = pd.DataFrame(report).transpose()
    report_df.to_csv(f"{current_dir}/experimentos-defesa/fold_{fold}/classification_report.csv", index=True)

    cm = confusion_matrix(y_test, y_pred_labels)
    tn, fp, fn, tp = cm.ravel()
    print("\nMatriz de Confusão:")
    print(cm)
    print(f"Falso Positivo (FP): {fp}")
    print(f"Falso Negativo (FN): {fn}")
    cm_df = pd.DataFrame(cm, index=['Real:0', 'Real:1'], columns=['Pred:0', 'Pred:1'])
    cm_df.to_csv(f"{current_dir}/experimentos-defesa/fold_{fold}/confusion_matrix.csv")

    save_path = f"{current_dir}/experimentos-defesa/fold_{fold}"
    os.makedirs(save_path, exist_ok=True)
    model.save(os.path.join(save_path, f"lstm_defend_model_fold{fold}.keras"))

    final_fold = time.time()
    tempo_fold = final_fold - inicio_fold
    tempos_folds.append({'Fold': fold, 'Tempo (s)': tempo_fold})
    tempo_total += tempo_fold
    fold += 1

tempos_folds.append({'Fold': 'Total', 'Tempo (s)': tempo_total})
tempos_df = pd.DataFrame(tempos_folds)
tempos_df.to_csv(f"{current_dir}/experimentos-defesa/tempos_folds.csv", index=False)
