import os
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix

# ============================
# 1. CONFIGURAÇÕES E FUNÇÕES
# ============================

BASE_PATH = "/home/victor/test-victor/experimentos"
RESULTS_PATH = "/home/victor/test-victor/experimentos/resultados"
features = ['IndLatency', 'DRB.UEThpDl', 'DRB.UEThpUl']
epsilons = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

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

# ============================
# 2. AVALIAR CADA FOLD
# ============================

n_folds = 5

for fold in range(1, n_folds + 1):
    print(f"\n==============================")
    print(f"🔁 Avaliando Fold {fold}")
    print(f"==============================")

    model_path = os.path.join(BASE_PATH, f"fold_{fold}", f"lstm_model_fold{fold}.keras")
    val_path = os.path.join(BASE_PATH, f"fold_{fold}", f"test_data.csv")

    if not os.path.exists(model_path) or not os.path.exists(val_path):
        print(f"⚠️ Modelo ou dados não encontrados para o fold {fold}. Pulando...")
        continue

    # Carregar modelo e dados
    model = tf.keras.models.load_model(model_path)
    df_val = pd.read_csv(val_path)
    X_test = df_val[features].values
    y_test = df_val['label'].values

    # Reformatar para LSTM
    X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

    attack_indices = np.where(y_test == 1)[0]

    for attack_type in ["FGSM", "PGD"]:
        for eps in epsilons:
            print(f"\n🧪 Fold {fold} | Ataque {attack_type} | ε = {eps}")

            if attack_type == "FGSM":
                X_adv_attacks = np.array([
                    create_adversarial_pattern_fgsm(X_test[i:i+1], [[1.0]], model, epsilon=eps).numpy()
                    for i in attack_indices
                ])
            else:
                X_adv_attacks = np.array([
                    create_adversarial_pattern_pgd(X_test[i:i+1], [[1.0]], model, epsilon=eps).numpy()
                    for i in attack_indices
                ])

            # Substituir apenas os exemplos da classe 1
            X_adv_full = np.copy(X_test)
            for idx, adv in zip(attack_indices, X_adv_attacks):
                X_adv_full[idx] = adv.reshape((X_test.shape[1], 1))

            # Previsões com adversarial misturado ao conjunto completo
            y_adv_pred = model.predict(X_adv_full).flatten()
            y_adv_labels = (y_adv_pred > 0.5).astype(int)

            # Avaliação contra y_test original
            print("\n📊 Relatório de Classificação (Conjunto Completo com Ataque na Classe 1):")
            print(classification_report(y_test, y_adv_labels, digits=4))

            cm_adv = confusion_matrix(y_test, y_adv_labels)
            tn_adv, fp_adv, fn_adv, tp_adv = cm_adv.ravel()

            print("\n🧮 Matriz de Confusão:")
            print(cm_adv)
            print(f"🔹 Falso Positivo (FP): {fp_adv}")
            print(f"🔹 Falso Negativo (FN): {fn_adv}")
            report = classification_report(y_test, y_adv_labels, output_dict=True, digits=4)
            cm_adv = confusion_matrix(y_test, y_adv_labels)
            tn_adv, fp_adv, fn_adv, tp_adv = cm_adv.ravel()
            
            # Salvar relatório como CSV
            report_df = pd.DataFrame(report).transpose()
            report_df["fold"] = fold
            report_df["attack"] = attack_type
            report_df["epsilon"] = eps
            
            # Salvar matriz de confusão e FP/FN também
            cm_df = pd.DataFrame(cm_adv, columns=["Pred_0", "Pred_1"], index=["Actual_0", "Actual_1"])
            metrics_df = pd.DataFrame([{
                "fold": fold,
                "attack": attack_type,
                "epsilon": eps,
                "FP": fp_adv,
                "FN": fn_adv,
                "TP": tp_adv,
                "TN": tn_adv
            }])
            
            # Criar diretório se não existir
            os.makedirs(RESULTS_PATH, exist_ok=True)
            
            # Nomes dos arquivos
            report_filename = f"{RESULTS_PATH}/classification_report_fold{fold}_{attack_type}_eps{eps}.csv"
            conf_matrix_filename = f"{RESULTS_PATH}/confusion_matrix_fold{fold}_{attack_type}_eps{eps}.csv"
            metrics_filename = f"{RESULTS_PATH}/metrics_summary_fold{fold}_{attack_type}_eps{eps}.csv"
            
            # Salvar CSVs
            report_df.to_csv(report_filename, index=True)
            cm_df.to_csv(conf_matrix_filename)
            metrics_df.to_csv(metrics_filename, index=False)
