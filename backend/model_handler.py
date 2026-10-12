import json
import os

import numpy as np

from backend.config import Config

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import tensorflow as tf
    from tensorflow.keras import layers, models
    from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img
    from tensorflow.keras.models import load_model
except ImportError:
    tf = None
    layers = None
    models = None
    ImageDataGenerator = None
    img_to_array = None
    load_img = None
    load_model = None


class WasteClassifier:
    def __init__(self, img_size=128):
        self.img_size = img_size
        self.model = None
        self.class_names = []

    def _ensure_tensorflow_available(self):
        if Image is None:
            raise ImportError(
                "Pillow is required for image loading. Install it with: "
                "python -m pip install pillow"
            )

        if tf is None or models is None or layers is None or ImageDataGenerator is None or load_img is None or img_to_array is None or load_model is None:
            raise ImportError(
                "TensorFlow is not available. Please install the project requirements with: "
                "python -m pip install -r requirements.txt"
            )

    def _build_model(self, num_classes):
        self._ensure_tensorflow_available()

        model = models.Sequential([
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=(self.img_size, self.img_size, 3)),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Flatten(),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.4),
            layers.Dense(num_classes, activation='softmax')
        ])

        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        return model

    def _load_labels(self):
        if os.path.exists(Config.LABELS_PATH):
            with open(Config.LABELS_PATH, 'r', encoding='utf-8') as file:
                return json.load(file)

        if os.path.isdir(Config.DATASET_DIR):
            class_names = sorted(
                [entry.name for entry in os.scandir(Config.DATASET_DIR) if entry.is_dir()]
            )
            return class_names

        return []

    def _save_labels(self):
        if not self.class_names:
            return
        os.makedirs(Config.MODEL_DIR, exist_ok=True)
        with open(Config.LABELS_PATH, 'w', encoding='utf-8') as file:
            json.dump(self.class_names, file)

    def train_model(self):
        self._ensure_tensorflow_available()

        if not os.path.isdir(Config.DATASET_DIR):
            raise FileNotFoundError(f"Dataset folder not found: {Config.DATASET_DIR}")

        train_datagen = ImageDataGenerator(
            rescale=1.0 / 255.0,
            validation_split=0.2,
            horizontal_flip=True,
            zoom_range=0.2,
        )

        train_data = train_datagen.flow_from_directory(
            Config.DATASET_DIR,
            target_size=(self.img_size, self.img_size),
            batch_size=32,
            class_mode='categorical',
            subset='training',
            seed=42,
        )

        val_data = train_datagen.flow_from_directory(
            Config.DATASET_DIR,
            target_size=(self.img_size, self.img_size),
            batch_size=32,
            class_mode='categorical',
            subset='validation',
            seed=42,
        )

        self.class_names = list(train_data.class_indices.keys())
        model = self._build_model(len(self.class_names))
        model.fit(train_data, validation_data=val_data, epochs=10, verbose=1)

        os.makedirs(Config.MODEL_DIR, exist_ok=True)
        model.save(Config.MODEL_PATH)
        self._save_labels()
        self.model = model
        return model

    def load_or_train(self):
        self._ensure_tensorflow_available()

        if not os.path.exists(Config.MODEL_PATH):
            return self.train_model()

        self.class_names = self._load_labels()
        if not self.class_names:
            self.class_names = sorted(
                [entry.name for entry in os.scandir(Config.DATASET_DIR) if entry.is_dir()]
            )

        self.model = load_model(Config.MODEL_PATH)
        return self.model

    def predict(self, image_path):
        self._ensure_tensorflow_available()

        if self.model is None:
            self.load_or_train()

        image = load_img(image_path, target_size=(self.img_size, self.img_size))
        image_array = img_to_array(image) / 255.0
        expanded = np.expand_dims(image_array, axis=0)
        prediction = self.model.predict(expanded, verbose=0)[0]

        predicted_index = int(np.argmax(prediction))
        predicted_class = self.class_names[predicted_index] if predicted_index < len(self.class_names) else 'unknown'
        confidence = float(np.max(prediction) * 100)

        return {
            'class_name': predicted_class,
            'confidence': round(confidence, 2),
            'index': predicted_index,
        }
