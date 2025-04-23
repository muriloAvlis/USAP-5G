import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix

# =========================
# 1. CONFIGURAÇÕES INICIAIS
# =========================

# Caminho dos arquivos
MODEL_PATH = "/home/victor/test-victor/lstm-oran-test.keras"
VAL_CSV_PATH = "/home/victor/test-victor/datasets/fix-dataset/val_instances.csv"

# Features utilizadas no treinamento
# features = [
#     'IndLatency', 'DRB.AirIfDelayUl', 'DRB.PacketSuccessRateUlgNBUu', 'DRB.RlcDelayUl',
#     'DRB.RlcPacketDropRateDl', 'DRB.RlcSduDelayDl', 'DRB.RlcSduTransmittedVolumeDL',
#     'DRB.RlcSduTransmittedVolumeUL', 'DRB.UEThpDl', 'DRB.UEThpUl'
# ]
features = ['IndLatency', 'DRB.UEThpDl', 'DRB.UEThpUl']
# ============================
# 2. CARREGAR MODELO E DADOS
# ============================

# Carregar modelo treinado
model = tf.keras.models.load_model(MODEL_PATH)

# Carregar dados de validação
df_val = pd.read_csv(VAL_CSV_PATH)
X_test = df_val[features].values
y_test = df_val['label'].values

# Reformatar para LSTM
X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

# =======================================
# 3. FUNÇÕES PARA ATAQUES ADVERSARIAIS
# =======================================

def create_adversarial_pattern_fgsm(input_data, target_label, model, epsilon):
    input_tensor = tf.convert_to_tensor(input_data, dtype=tf.float32)
    target_tensor = tf.convert_to_tensor(target_label, dtype=tf.float32)

    with tf.GradientTape() as tape:
        tape.watch(input_tensor)
        prediction = model(input_tensor, training=False)
        loss = tf.keras.losses.binary_crossentropy(target_tensor, prediction)

    gradient = tape.gradient(loss, input_tensor)
    adversarial_example = input_tensor + epsilon * tf.sign(gradient)
    return tf.clip_by_value(adversarial_example, -1, 1)

def create_adversarial_pattern_pgd(input_data, target_label, model, epsilon, alpha=0.01, iterations=40):
    input_tensor = tf.convert_to_tensor(input_data, dtype=tf.float32)
    target_tensor = tf.convert_to_tensor(target_label, dtype=tf.float32)

    adv_example = tf.Variable(input_tensor)

    for _ in range(iterations):
        with tf.GradientTape() as tape:
            tape.watch(adv_example)
            prediction = model(adv_example, training=False)
            loss = tf.keras.losses.binary_crossentropy(target_tensor, prediction)

        gradient = tape.gradient(loss, adv_example)
        adv_example.assign_add(alpha * tf.sign(gradient))
        perturbation = tf.clip_by_value(adv_example - input_tensor, -epsilon, epsilon)
        adv_example.assign(tf.clip_by_value(input_tensor + perturbation, -1, 1))

    return adv_example

# ==========================
# 4. EXECUTAR OS ATAQUES
# ==========================

epsilons = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
attack_indices = np.where(y_test == 1)[0]  # Apenas instâncias de ataque

for attack_type in ["FGSM", "PDG"]:
    for eps in epsilons:
        print(f"\n=== Testando Ataque {attack_type} com ε = {eps} ===")

        if attack_type == "FGSM":
            X_adv = np.array([
                create_adversarial_pattern_fgsm(X_test[i:i+1], [[1.0]], model, epsilon=eps).numpy()
                for i in attack_indices
            ])
        else:
            X_adv = np.array([
                create_adversarial_pattern_pgd(X_test[i:i+1], [[1.0]], model, epsilon=eps).numpy()
                for i in attack_indices
            ])

        # Garantir formato correto para LSTM
        X_adv = X_adv.reshape((X_adv.shape[0], X_test.shape[1], 1))

        # Previsões
        y_adv_pred = model.predict(X_adv).flatten()
        y_adv_labels = (y_adv_pred > 0.5).astype(int)

        # Avaliação
        print("\nRelatório de Classificação (Amostras Adversariais):")
        print(classification_report(np.ones(len(y_adv_labels)), y_adv_labels))

        cm_adv = confusion_matrix(np.ones(len(y_adv_labels)), y_adv_labels)
        tn_adv, fp_adv, fn_adv, tp_adv = cm_adv.ravel()

        print("\nMatriz de Confusão (Amostras Adversariais):")
        print(cm_adv)
        print(f"\n🔹 Falso Positivo (FP): {fp_adv}")
        print(f"🔹 Falso Negativo (FN): {fn_adv}")
