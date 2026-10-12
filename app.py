import os

from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

from backend.config import Config
from backend.db import get_recent_predictions, init_db, save_prediction
from backend.model_handler import WasteClassifier


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
    os.makedirs(Config.MODEL_DIR, exist_ok=True)

    classifier = WasteClassifier()
    model_ready = False

    try:
        classifier.load_or_train()
        model_ready = True
        print("Application started successfully.")
    except Exception as exc:
        print(f"Startup warning: {exc}")

    try:
        init_db()
    except Exception as exc:
        print(f"Database init warning: {exc}")

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/history')
    def get_history():
        return jsonify({
            'status': 'success',
            'history': get_recent_predictions(limit=10),
        })

    @app.route('/predict', methods=['POST'])
    def predict():
        if 'image' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No image file uploaded.'
            }), 400

        uploaded_file = request.files['image']
        if uploaded_file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'Please choose an image file.'
            }), 400

        filename = secure_filename(uploaded_file.filename)
        save_path = os.path.join(Config.UPLOAD_DIR, filename)
        uploaded_file.save(save_path)

        if not model_ready:
            return jsonify({
                'status': 'error',
                'message': 'Model is not ready. Please train the model first with python train_model.py.'
            }), 500

        try:
            result = classifier.predict(save_path)
            save_prediction(
                file_name=filename,
                predicted_class=result['class_name'],
                confidence=float(result['confidence']),
                image_path=save_path,
            )

            return jsonify({
                'status': 'success',
                'prediction': result['class_name'],
                'confidence': result['confidence'],
                'file_name': filename,
                'history': get_recent_predictions(limit=5)
            })
        except Exception as exc:
            return jsonify({
                'status': 'error',
                'message': str(exc)
            }), 500

    @app.route('/health')
    def health_check():
        return jsonify({'status': 'ok'})

    return app


app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')), debug=False)
