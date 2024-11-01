import numpy as np

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from model import Model
from load_models import load_dnn_model, load_label_encoder

def evaluate_model(model, X_val, y_val):
    # accuracy
    y_pred_prob = model.predict(X_val)
    y_pred = np.argmax(y_pred_prob, axis=1)  # get highest probability
    accuracy = accuracy_score(y_val, y_pred)
    
    # General accuracy
    print(f"Model accuracy: {accuracy:.4f}")

    # Confusion matrix
    conf_matrix = confusion_matrix(y_val, y_pred)
    print('Confusion matrix:')
    print(conf_matrix)

    # Accuracy by class
    accuracies = {}
    for i in range(conf_matrix.shape[0]):  # Loop by classes
        TP = conf_matrix[i, i]  # True positives
        TN = conf_matrix.sum() - conf_matrix[i].sum() - conf_matrix[:, i].sum() + TP  # True Negatives Negativos
        total_instances = conf_matrix[i].sum() + (conf_matrix.sum() - conf_matrix[i].sum())  # Total of instances
        class_accuracy = (TP + TN) / total_instances if total_instances > 0 else 0
        accuracies[i] = class_accuracy

    # Exibir resultados
    label_encoder = load_label_encoder()
    for class_label, accuracy in accuracies.items():
        slice_id = label_encoder.inverse_transform([class_label])
        print(f'Accuracy for class {slice_id[0]}: {accuracy * 100:.2f}%')

    # F1 score, recall and precision
    report = classification_report(
        y_val, y_pred, target_names=["1", "2", "3", "128"])
    print("Classification report:")
    print(report)

if __name__ == "__main__":
    features = Model()
    X_val = features.X_val
    y_val = features.y_val

    model = load_dnn_model()

    evaluate_model(model, X_val, y_val)