# WasteVision AI

This project is the renamed version of the previous `Waste-Classifier` repository and is prepared for deployment on Vercel. It uses a CNN-based waste classification model, a Flask backend, and a lightweight web interface for uploading images and viewing recent predictions.

## New GitHub repo name

The project is now set up for a repo such as:

```text
https://github.com/RushikeshKulkarni07/WasteVision-AI
```

You can rename the repository in GitHub to match your preferred naming convention after the first push.

## Project structure

- `app.py` – Flask app entry point
- `backend/` – model and database logic
- `database/schema.sql` – SQL schema for MySQL setups
- `static/` – frontend styling and JavaScript
- `templates/` – HTML templates
- `model/` – saved model and labels
- `uploads/` – temporary upload folder
- `Garbage classification/` – training dataset

## Features

- Upload an image of waste
- Predict cardboard, glass, metal, paper, plastic, and trash
- Show confidence scores
- Stores recent predictions in a local SQLite database by default
- Works on Vercel with serverless-friendly SQLite fallback

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. Configure environment

```bash
copy .env.example .env
```

Then update `.env` for your local setup. For Vercel deployment, leave `USE_SQLITE=true` unless you attach your own MySQL database.

## 3. Run locally

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## 4. Deploy on Vercel

1. Push this project to GitHub.
2. Import the repo into Vercel.
3. Set the project root to the repository root.
4. Keep Python as the runtime and let Vercel install `requirements.txt` automatically.
5. Add `VERCEL=1` as an environment variable if needed.
6. Deploy the project.

## 5. Notes

- The app uses SQLite by default for Vercel compatibility.
- If you want MySQL in local development, set `USE_SQLITE=false` and provide your SQL credentials.
- The saved model file is expected in `model/waste_classifier_model.h5`.
- If the model is missing, run `python train_model.py` once.

## Git commands

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/RushikeshKulkarni07/WasteVision-AI.git
git push -u origin main
```
