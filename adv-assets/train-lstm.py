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
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix

# 1. CARREGAR O DATASET
df = pd.read_csv('/home/victor/test-victor/datasets/fix-dataset/dataset_sem_colunas.csv')

# # 2. SEPARAR FEATURES E LABELS
# features = ['IndLatency', 'DRB.AirIfDelayUl', 'DRB.PacketSuccessRateUlgNBUu', 'DRB.RlcDelayUl',
#             'DRB.RlcPacketDropRateDl', 'DRB.RlcSduDelayDl', 'DRB.RlcSduTransmittedVolumeDL',
#             'DRB.RlcSduTransmittedVolumeUL', 'DRB.UEThpDl', 'DRB.UEThpUl']
features = ['IndLatency', 'DRB.UEThpDl', 'DRB.UEThpUl']

X = df[features].values  # Features
y = df['label'].values   # Labels

# 3. DIVIDIR EM TREINAMENTO E TESTE
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# 4. NORMALIZAÇÃO DOS DADOS
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# 5. OVERSAMPLING COM SMOTE (para aumentar a classe 1)
smote = SMOTE(sampling_strategy=0.2, random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

# 6. DATA AUGMENTATION PARA ATAQUES DDoS
def augment_syn_attack(data, noise=0.01):
    return data + noise * np.random.randn(*data.shape)

X_train_augmented = np.vstack([X_train_resampled, augment_syn_attack(X_train_resampled[y_train_resampled == 1])])
y_train_augmented = np.hstack([y_train_resampled, np.ones(len(X_train_resampled[y_train_resampled == 1]))])

# 7. AJUSTE DE PESOS DAS CLASSES
class_weights = compute_class_weight('balanced', classes=np.unique(y_train_augmented), y=y_train_augmented)
class_weights_dict = {0: class_weights[0], 1: class_weights[1]}

# 8. REFORMATAR PARA LSTM (adicionar dimensão de tempo)
X_train_augmented = X_train_augmented.reshape((X_train_augmented.shape[0], X_train_augmented.shape[1], 1))
X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

# 9. CONSTRUIR A LSTM
model = Sequential([
    LSTM(64, return_sequences=True, input_shape=(X_train_augmented.shape[1], 1)),
    Dropout(0.3),
    LSTM(32, return_sequences=False),
    Dropout(0.3),
    Dense(1, activation='sigmoid')
])

# Salvar as instâncias de treinamento (após oversampling + augmentação)
X_train_augmented_2d = X_train_augmented.reshape((X_train_augmented.shape[0], X_train_augmented.shape[1]))
df_train = pd.DataFrame(X_train_augmented_2d, columns=features)
df_train['label'] = y_train_augmented
df_train.to_csv('/home/victor/test-victor/datasets/fix-dataset/train_instances_reduced.csv', index=False)

# Salvar as instâncias de validação (X_test e y_test)
X_test_2d = X_test.reshape((X_test.shape[0], X_test.shape[1]))
df_val = pd.DataFrame(X_test_2d, columns=features)
df_val['label'] = y_test
# mudar aqui tbm
df_val.to_csv('/home/victor/test-victor/datasets/fix-dataset/val_instances.csv', index=False)


model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])

# 10. TREINAR O MODELO
history = model.fit(X_train_augmented, y_train_augmented,
                    epochs=20, batch_size=32,
                    validation_data=(X_test, y_test),
                    class_weight=class_weights_dict)

# 11. AVALIAÇÃO DO MODELO
y_pred = model.predict(X_test)

# Garantindo que y_pred tenha o mesmo formato de y_test
y_pred = y_pred.flatten()
y_pred_labels = (y_pred > 0.5).astype(int)

print("\nRelatório de Classificação:")
print(classification_report(y_test, y_pred_labels))

#print("AUC-ROC Score:", roc_auc_score(y_test, y_pred))

# 12. MATRIZ DE CONFUSÃO E CÁLCULO DE FALSO POSITIVO / FALSO NEGATIVO
cm = confusion_matrix(y_test, y_pred_labels)
tn, fp, fn, tp = cm.ravel()

print("\nMatriz de Confusão:")
print(cm)

print(f"\n🔹 Falso Positivo (FP): {fp}")
print(f"🔹 Falso Negativo (FN): {fn}")

model.save("lstm-oran-test.keras")
