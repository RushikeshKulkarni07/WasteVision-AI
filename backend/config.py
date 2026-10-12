import os
from dotenv import load_dotenv

load_dotenv()


def _as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, os.getenv("DATASET_PATH", "Garbage classification"))
MODEL_DIR = os.path.join(BASE_DIR, "model")
MODEL_PATH = os.path.join(
    MODEL_DIR,
    os.path.basename(os.getenv("MODEL_PATH", "waste_classifier_model.h5")),
)
LABELS_PATH = os.path.join(MODEL_DIR, "labels.json")
UPLOAD_DIR = os.path.join(BASE_DIR, os.getenv("UPLOAD_FOLDER", "uploads"))
if os.getenv("VERCEL") == "1":
    UPLOAD_DIR = "/tmp/uploads"
DATABASE_PATH = os.path.join(BASE_DIR, "database", "prediction_history.db")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "waste-classifier-secret")
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "waste_classifier")
    if os.getenv("USE_SQLITE") is not None:
        USE_SQLITE = _as_bool(os.getenv("USE_SQLITE"))
    else:
        USE_SQLITE = os.getenv("VERCEL") == "1" or not os.getenv("MYSQL_HOST")
    BASE_DIR = BASE_DIR
    DATASET_DIR = DATASET_DIR
    MODEL_DIR = MODEL_DIR
    MODEL_PATH = MODEL_PATH
    LABELS_PATH = LABELS_PATH
    UPLOAD_DIR = UPLOAD_DIR
    DATABASE_PATH = DATABASE_PATH
