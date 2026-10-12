from backend.model_handler import WasteClassifier


if __name__ == "__main__":
    classifier = WasteClassifier()
    model = classifier.train_model()
    print("Model trained successfully.")
    print("Saved model:", model)
