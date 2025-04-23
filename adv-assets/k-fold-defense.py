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

# AUGMENTAÇÃO SINTÉTICA BASEADA EM RUÍDO GAUSSIANO
def augment_syn_attack(data, noise=0.01):
    return data + noise * np.random.randn(*data.shape)

# FGSM
def create_adversarial_pattern_fgsm(input_data, target_label, model, epsilon):
    input_tensor = tf.convert_to_tensor(input_data, dtype=tf.float32)
    target_tensor = tf.convert_to_tensor(target_label, dtype=tf.float32)
    target_tensor = tf.reshape(target_tensor, (-1, 1))

    with tf.GradientTape() as tape:
        tape.watch(input_tensor)
        prediction = model(input_tensor, training=False)
        loss = tf.keras.losses.binary_crossentropy(target_tensor, prediction)

    gradient = tape.gradient(loss, input_tensor)
    adversarial_example = input_tensor + epsilon * tf.sign(gradient)
    return tf.clip_by_value(adversarial_example, -1, 1)

# PGD
def create_adversarial_pattern_pgd(input_data, target_label, model, epsilon, alpha=0.01, num_iter=10):
    x_adv = tf.identity(input_data)
    target_tensor = tf.convert_to_tensor(target_label, dtype=tf.float32)
    target_tensor = tf.reshape(target_tensor, (-1, 1))

    for _ in range(num_iter):
        with tf.GradientTape() as tape:
            tape.watch(x_adv)
            prediction = model(x_adv, training=False)
            loss = tf.keras.losses.binary_crossentropy(target_tensor, prediction)

        gradient = tape.gradient(loss, x_adv)
        signed_grad = tf.sign(gradient)
        x_adv = x_adv + alpha * signed_grad
        x_adv = tf.clip_by_value(x_adv, input_data - epsilon, input_data + epsilon)
        x_adv = tf.clip_by_value(x_adv, -1, 1)

    return x_adv

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
df = pd.read_csv('/home/victor/test-victor/datasets/fix-dataset/dataset_sem_colunas.csv')

features = ['IndLatency', 'DRB.UEThpDl', 'DRB.UEThpUl']
X = df[features].values
y = df['label'].values

# K-FOLD SETUP
n_splits = 5
skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

fold = 1
for train_index, test_index in skf.split(X, y):
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

    for epoch in range(20):
        print(f"Época {epoch + 1} de 20")

        for epsilon in epsilon_values:
            print(f"  Gerando exemplos adversariais (FGSM + PGD) com epsilon = {epsilon}")

            X_adv_fgsm = np.array([
                create_adversarial_pattern_fgsm(X_train_augmented[i:i+1], [y_train_augmented[i]], model, epsilon).numpy().squeeze()
                for i in range(len(X_train_augmented))
            ])
            X_adv_pgd = np.array([
                create_adversarial_pattern_pgd(X_train_augmented[i:i+1], [y_train_augmented[i]], model, epsilon).numpy().squeeze()
                for i in range(len(X_train_augmented))
            ])

            X_adv_combined = np.vstack([X_adv_fgsm, X_adv_pgd])[..., np.newaxis]
            y_adv_combined = np.hstack([y_train_augmented, y_train_augmented])

            X_train_combined = np.vstack([X_train_augmented_lstm, X_adv_combined])
            y_train_combined = np.hstack([y_train_augmented, y_adv_combined])

            model.fit(
                X_train_combined, y_train_combined,
                epochs=1, batch_size=32,
                validation_data=(X_test_lstm, y_test),
                class_weight=class_weights_dict,
                verbose=1
            )

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

    save_path = f"/home/victor/test-victor/experimentos-defesa/fold_{fold}"
    os.makedirs(save_path, exist_ok=True)
    model.save(os.path.join(save_path, f"lstm_defend_model_fold{fold}.keras"))

    fold += 1
