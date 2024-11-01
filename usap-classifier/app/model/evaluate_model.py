import numpy as np

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from model import Model
from load_models import load_dnn_model

def evaluate_model(model, X_val, y_val):
    # accuracy
    y_pred_prob = model.predict(X_val)
    y_pred = np.argmax(y_pred_prob, axis=1)  # get highest probability
    accuracy = accuracy_score(y_val, y_pred)
    
    # predicted_slices = label_encoder.inverse_transform(np.argmax(predictions, axis=1))
    print(f"Model accuracy: {accuracy:.4f}")

    # Confusion matrix
    conf_matrix = confusion_matrix(y_val, y_pred)
    print('Confusion matrix:')
    print(conf_matrix)

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