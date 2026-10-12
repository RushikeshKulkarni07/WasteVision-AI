from backend.model_handler import WasteClassifier


if __name__ == '__main__':
    classifier = WasteClassifier()
    classifier.train_model()
    print('Training completed successfully.')
