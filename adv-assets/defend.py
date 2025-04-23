import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import SMOTE
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import matplotlib.pyplot as plt

# === 1. CARREGAR DADOS ===
df = pd.read_csv('/home/victor/test-victor/datasets/fix-dataset/dataset_sem_colunas.csv')
features = ['IndLatency', 'DRB.AirIfDelayUl', 'DRB.PacketSuccessRateUlgNBUu', 'DRB.RlcDelayUl',
            'DRB.RlcPacketDropRateDl', 'DRB.RlcSduDelayDl', 'DRB.RlcSduTransmittedVolumeDL',
            'DRB.RlcSduTransmittedVolumeUL', 'DRB.UEThpDl', 'DRB.UEThpUl']
X = df[features].values
y = df['label'].values

# === 2. SPLIT / NORMALIZAÇÃO / SMOTE ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

smote = SMOTE(sampling_strategy=0.2, random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

# === 3. AUMENTAR CLASSE 1 (ataques legítimos) ===
def augment_syn_attack(data, noise=0.01):
    return data + noise * np.random.randn(*data.shape)

X_train_aug = np.vstack([X_train_resampled, augment_syn_attack(X_train_resampled[y_train_resampled == 1])])
y_train_aug = np.hstack([y_train_resampled, np.ones(len(X_train_resampled[y_train_resampled == 1]))])

# === 4. REFORMATAR ===
X_train_aug = X_train_aug.reshape((X_train_aug.shape[0], X_train_aug.shape[1], 1))
X_test_lstm = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

# === 5. MODELO INICIAL ===
def build_model():
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(X_train_aug.shape[1], 1)),
        Dropout(0.3),
        LSTM(32),
        Dropout(0.3),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer=Adam(0.001), loss='binary_crossentropy', metrics=['accuracy'])
    return model

model = build_model()

# === 6. DEFESA ADVERSARIAL ===
def create_adversarial_pattern(input_data, target_label, model, epsilon, method="fgsm", alpha=0.01, iters=40):
    input_tensor = tf.convert_to_tensor(input_data, dtype=tf.float32)
    target_tensor = tf.convert_to_tensor(target_label, dtype=tf.float32)

    if method == "fgsm":
        with tf.GradientTape() as tape:
            tape.watch(input_tensor)
            prediction = model(input_tensor, training=False)
            loss = tf.keras.losses.binary_crossentropy(target_tensor, prediction)
        gradient = tape.gradient(loss, input_tensor)
        adversarial = input_tensor + epsilon * tf.sign(gradient)
        return tf.clip_by_value(adversarial, -1, 1)

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

# === 7. TREINAMENTO DO MODELO BASE ===
class_weights = compute_class_weight('balanced', classes=np.unique(y_train_aug), y=y_train_aug)
class_weights_dict = {0: class_weights[0], 1: class_weights[1]}

model.fit(X_train_aug, y_train_aug,
          epochs=10,
          batch_size=32,
          validation_data=(X_test_lstm, y_test),
          class_weight=class_weights_dict)

# === 8. GERAR AMOSTRAS ADVERSÁRIAS ===
X_test_attack = X_test_lstm[y_test == 1]
y_attack = np.ones(len(X_test_attack))

X_fgsm = np.vstack([
    create_adversarial_pattern(X_test_attack[i:i+1], [[1.]], model, epsilon=0.3, method="fgsm").numpy()
    for i in range(len(X_test_attack))
])

X_pgd = np.vstack([
    create_adversarial_pattern(X_test_attack[i:i+1], [[1.]], model, epsilon=0.3, method="pgd").numpy()
    for i in range(len(X_test_attack))
])

# === 9. TREINAR COM DEFESA ===
X_defended = np.vstack([X_train_aug, X_fgsm, X_pgd])
y_defended = np.hstack([y_train_aug, np.ones(len(X_fgsm) + len(X_pgd))])

model_defended = build_model()
model_defended.fit(X_defended, y_defended,
                   epochs=10,
                   batch_size=32,
                   validation_data=(X_test_lstm, y_test),
                   class_weight=class_weights_dict)

# === 10. AVALIAÇÃO FINAL ===
def evaluate(model, X, y, title=""):
    y_pred = model.predict(X).flatten()
    y_labels = (y_pred > 0.5).astype(int)
    print(f"\n🔍 {title}")
    print(classification_report(y, y_labels))
    return roc_auc_score(y, y_pred)

print("\n=== AVALIAÇÃO ORIGINAL ===")
evaluate(model, X_test_lstm, y_test, title="Modelo Original")

print("\n=== AVALIAÇÃO DEFENDIDO ===")
evaluate(model_defended, X_test_lstm, y_test, title="Modelo Defendido")

# === 11. SALVAR MODELO DEFENDIDO ===
model_defended.save("/home/victor/test-victor/lstm-defended-final.keras")
