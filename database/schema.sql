CREATE DATABASE IF NOT EXISTS waste_classifier;
USE waste_classifier;

CREATE TABLE IF NOT EXISTS prediction_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    predicted_class VARCHAR(100) NOT NULL,
    confidence DECIMAL(5,2) NOT NULL,
    image_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_prediction_history_created_at
ON prediction_history (created_at DESC);
