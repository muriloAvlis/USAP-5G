import os
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix

# Função FGSM
def fgsm(model, X, y, epsilon):
    X_tensor = tf.convert_to_tensor(X, dtype=tf.float32)
    y_tensor = tf.convert_to_tensor(y.reshape(-1, 1), dtype=tf.float32)
    with tf.GradientTape() as tape:
        tape.watch(X_tensor)
        prediction = model(X_tensor, training=False)
        loss = tf.keras.losses.binary_crossentropy(y_tensor, prediction)
    gradient = tape.gradient(loss, X_tensor)
    adv_X = X_tensor + epsilon * tf.sign(gradient)
    return tf.clip_by_value(adv_X, -1, 1).numpy()

# Função PGD
def pgd(model, X, y, epsilon, alpha=0.01, num_iter=40):
    X_tensor = tf.convert_to_tensor(X, dtype=tf.float32)
    adv_X = tf.identity(X_tensor)
    y_tensor = tf.convert_to_tensor(y.reshape(-1, 1), dtype=tf.float32)
    for _ in range(num_iter):
        with tf.GradientTape() as tape:
            tape.watch(adv_X)
            pred = model(adv_X, training=False)
            loss = tf.keras.losses.binary_crossentropy(y_tensor, pred)
        gradient = tape.gradient(loss, adv_X)
        adv_X = adv_X + alpha * tf.sign(gradient)
        adv_X = tf.clip_by_value(adv_X, X_tensor - epsilon, X_tensor + epsilon)
        adv_X = tf.clip_by_value(adv_X, -1, 1)
    return adv_X.numpy()

# Função de Avaliação
def avaliar_modelo(model, X_adv, y_true):
    y_pred = (model.predict(X_adv).flatten() > 0.5).astype(int)
    report = classification_report(y_true, y_pred, output_dict=True)
    cm = confusion_matrix(y_true, y_pred)
    return report, cm

# Função para garantir que '1' existe no reporte
def get_recall(report, class_label):
    # Verifica se a classe '1' existe no dicionário e retorna o recall
    return report.get(str(class_label), {}).get('recall', 0.0)

# Parâmetros de Execução
folds = 5
epsilon_list = [0.1, 0.3, 0.5]
current_dir = os.getcwd()
features = ['IndLatency', 'DRB.UEThpDl', 'DRB.UEThpUl']

# Criar diretório de resultados
result_dir = os.path.join(current_dir, "comparacao_defesa")
os.makedirs(result_dir, exist_ok=True)

# Loop principal para avaliação com diferentes valores de epsilon
for epsilon in epsilon_list:
    all_results = []
    print(f"\nAvaliando para epsilon = {epsilon}")
    
    for fold in range(1, folds + 1):
        print(f"Fold {fold}")

        # Carregar modelos
        defend_model = tf.keras.models.load_model(f"{current_dir}/experimentos-defesa/fold_{fold}/lstm_defend_model_fold{fold}.keras")
        base_model = tf.keras.models.load_model(f"{current_dir}/experimentos/fold_{fold}/lstm_model_fold{fold}.keras")

        # Carregar dados de teste
        test_df = pd.read_csv(f"{current_dir}/experimentos/fold_{fold}/test_data.csv")
        X_test = test_df[features].values
        y_test = test_df["label"].values
        X_test_lstm = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

        # Criar exemplos adversariais
        X_adv_fgsm = fgsm(base_model, X_test_lstm, y_test, epsilon)
        X_adv_pgd = pgd(base_model, X_test_lstm, y_test, epsilon)

        # Avaliar os modelos em FGSM
        rep_def_fgsm, cm_def_fgsm = avaliar_modelo(defend_model, X_adv_fgsm, y_test)
        rep_base_fgsm, cm_base_fgsm = avaliar_modelo(base_model, X_adv_fgsm, y_test)

        # Avaliar os modelos em PGD
        rep_def_pgd, cm_def_pgd = avaliar_modelo(defend_model, X_adv_pgd, y_test)
        rep_base_pgd, cm_base_pgd = avaliar_modelo(base_model, X_adv_pgd, y_test)

        # Coletar resultados para salvar
        all_results.append({
            'Fold': fold,
            'Epsilon': epsilon,
            'Defendida_FGSM_Recall': get_recall(rep_def_fgsm, 1),
            'Base_FGSM_Recall': get_recall(rep_base_fgsm, 1),
            'Defendida_PGD_Recall': get_recall(rep_def_pgd, 1),
            'Base_PGD_Recall': get_recall(rep_base_pgd, 1)
        })

    # Salvar os resultados do fold
    result_df = pd.DataFrame(all_results)
    result_df.to_csv(os.path.join(result_dir, f"comparacao_epsilon_{epsilon}.csv"), index=False)

print("\nComparação concluída!")
