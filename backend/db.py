import os
import sqlite3

import mysql.connector
from mysql.connector import Error

from backend.config import Config


def create_database_if_not_exists():
    if Config.USE_SQLITE:
        os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
        return

    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
        )
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DATABASE}")
        cursor.close()
        connection.close()
    except Error as exc:
        print(f"MySQL database creation failed: {exc}")
        raise


def connect_db():
    if Config.USE_SQLITE:
        os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
        connection = sqlite3.connect(Config.DATABASE_PATH)
        connection.row_factory = sqlite3.Row
        return connection

    create_database_if_not_exists()
    connection = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE,
        autocommit=True,
    )
    return connection


def init_db():
    try:
        connection = connect_db()
        if Config.USE_SQLITE:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS prediction_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT NOT NULL,
                    predicted_class TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    image_path TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_prediction_history_created_at ON prediction_history (created_at DESC)"
            )
            connection.commit()
        else:
            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS prediction_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    file_name VARCHAR(255) NOT NULL,
                    predicted_class VARCHAR(100) NOT NULL,
                    confidence DECIMAL(5,2) NOT NULL,
                    image_path VARCHAR(500),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_prediction_history_created_at ON prediction_history (created_at DESC)"
            )
            cursor.close()
        connection.close()
    except Exception as exc:
        print(f"Database init skipped: {exc}")


def save_prediction(file_name, predicted_class, confidence, image_path=None):
    try:
        connection = connect_db()
        if Config.USE_SQLITE:
            connection.execute(
                """
                INSERT INTO prediction_history (file_name, predicted_class, confidence, image_path)
                VALUES (?, ?, ?, ?)
                """,
                (file_name, predicted_class, float(confidence), image_path),
            )
            connection.commit()
        else:
            cursor = connection.cursor()
            query = """
                INSERT INTO prediction_history (file_name, predicted_class, confidence, image_path)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (file_name, predicted_class, confidence, image_path))
            cursor.close()
        connection.close()
    except Exception as exc:
        print(f"Database save skipped: {exc}")


def get_recent_predictions(limit=10):
    try:
        connection = connect_db()
        if Config.USE_SQLITE:
            rows = connection.execute(
                """
                SELECT file_name, predicted_class AS class_name, confidence, created_at
                FROM prediction_history
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [dict(row) for row in rows]

        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT file_name, predicted_class AS class_name, confidence, created_at
            FROM prediction_history
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (limit,),
        )
        records = cursor.fetchall()
        cursor.close()
        connection.close()
        return records
    except Error as exc:
        print(f"Unable to fetch prediction history: {exc}")
        return []
    except sqlite3.Error as exc:
        print(f"Unable to fetch SQLite prediction history: {exc}")
        return []
