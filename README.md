
# Final Project - MLWorkbench — Interactive Machine Learning Training & Prediction Platform

## Project Overview

A complete Machine Learning application built with **FastAPI** and **Streamlit**.

The project provides a web-based ML playground where users can:

- Upload CSV datasets
- Preview uploaded datasets
- View dataset statistics
- Detect missing values
- Select input features
- Select a target/label column
- Select a Machine Learning algorithm
- Train ML models through a FastAPI backend
- Save trained models using Joblib
- View model performance metrics
- Enter new input values
- Generate real-time predictions
- View previously trained models
- Authenticate using JWT
- Control API usage through a token system

The application separates the **ML backend/API** from the **Streamlit frontend**.

---

# Project Architecture

```text
                         USER
                           │
                           ▼
                ┌─────────────────────┐
                │ Streamlit Dashboard │
                │  ML Model Playground│
                └──────────┬──────────┘
                           │
                    HTTP REST API
                           │
                           ▼
                ┌─────────────────────┐
                │       FastAPI       │
                │       Backend       │
                └──────────┬──────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
          JWT Auth      ML Training   Prediction
              │            │            │
              ▼            ▼            ▼
           SQLite       Scikit-learn   Saved Models
                                      (.pkl / Joblib)
````

---

# Project Structure

```text
FinalProject_FastAPI/
│
├── main.py
│       # FastAPI backend and REST API endpoints
│
├── streamlit_app.py
│       # Interactive ML dashboard / frontend
│
├── bl.py
│       # Business logic
│       # Training, prediction, tokens and ML operations
│
├── dal.py
│       # Data access layer
│       # SQLite database and model metadata
│
├── models.py
│       # Pydantic schemas
│       # JWT helpers and ML model registry
│
├── app.db
│       # SQLite database
│
├── train_sample.csv
│       # Example training dataset
│
├── models_storage/
│       # Saved trained ML models
│
├── server.log
│       # Application logs
│
├── requirements.txt
│       # Python dependencies
│
├── FastAPI_ML_Postman_Collection.json
│       # Postman API testing collection
│
└── README.md
```

---

# Installation and Setup

## 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd FinalProject_FastAPI
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv .venv
```

Activate it using PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or using Command Prompt:

```cmd
.venv\Scripts\activate
```

---

## 3. Install dependencies

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install project dependencies:

```bash
pip install -r requirements.txt
```

If required, install the main dependencies manually:

```bash
pip install fastapi
pip install uvicorn
pip install pandas
pip install scikit-learn
pip install joblib
pip install streamlit
pip install requests
pip install pyjwt
pip install pydantic
pip install python-multipart
pip install bcrypt
```

Optional XGBoost support:

```bash
pip install xgboost
```

---

# Running the Application

The application consists of two parts:

1. FastAPI backend
2. Streamlit frontend

Both must be running simultaneously.

---

## 1. Start FastAPI

Open the first terminal:

```bash
uvicorn main:app --reload --port 8000
```

The API will run at:

```text
http://localhost:8000
```

---

## 2. Open Swagger UI

FastAPI automatically provides interactive API documentation.

Open:

```text
http://localhost:8000/docs
```

Swagger can be used to test authentication, tokens, model training and prediction APIs.

---

## 3. Start Streamlit

Open a second terminal.

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run:

```bash
streamlit run streamlit_app.py
```

The Streamlit application will normally be available at:

```text
http://localhost:8501
```

---

# ML Model Playground

The Streamlit dashboard provides the main user interface for the Machine Learning workflow.

The complete workflow is:

```text
Upload CSV
     ↓
Preview Dataset
     ↓
Select Target
     ↓
Select Features
     ↓
Select ML Model
     ↓
Train Model
     ↓
View Performance Metrics
     ↓
Enter Test Values
     ↓
Generate Prediction
     ↓
View Prediction
```

---

# Dataset Upload

Users can upload a CSV file directly through the Streamlit dashboard.

The dashboard displays:

* Number of rows
* Number of columns
* Number of missing values
* Number of numeric columns
* Dataset preview
* Missing-value information

Example:

```text
Dataset: train_sample.csv

Rows:             6
Columns:          4
Missing Values:   0
Numeric Columns:  4
```

---

# Feature and Target Selection

After uploading a dataset, the user selects:

### Target / Label

The column that the ML model needs to predict.

### Input Features

The columns used by the model to make the prediction.

For example:

```text
Dataset:

age
salary
rooms
price
```

Configuration:

```text
Features:
age
salary
rooms

Target:
price
```

The model therefore learns:

```text
age + salary + rooms
          ↓
       ML Model
          ↓
        price
```

---

# Supported Machine Learning Models

The application supports several Machine Learning algorithms through the backend.

Currently available in the dashboard:

```text
Linear Regression
Random Forest
Support Vector Regression (SVR)
XGBoost (if installed)
```

The backend also contains support for classification models such as Logistic Regression.

The available algorithms depend on the model registry and installed dependencies.

---

# Model Training

After selecting the dataset, features, target and model, the user clicks:

```text
Train Model
```

The Streamlit frontend sends the dataset and configuration to:

```text
POST /train
```

The FastAPI backend then:

```text
CSV Dataset
     ↓
Pandas DataFrame
     ↓
Feature Selection
     ↓
Target Selection
     ↓
ML Model
     ↓
Model Training
     ↓
Performance Metrics
     ↓
Save Model
```

The trained model is saved using Joblib.

---

# Model Performance

After training, the dashboard displays the metrics returned by the ML backend.

For regression models, metrics can include:

```text
MAE
R²
```

Example:

```text
MAE       1.3433

R²        0.9624
```

### Important

The current backend calculates these metrics using the training dataset.

Therefore, these values should **not be interpreted as production-level model accuracy or generalization performance**.

A future improvement is to introduce:

```text
Train/Test Split
        ↓
Train Model
        ↓
Test Model
        ↓
Calculate Metrics
```

instead of evaluating the model on the same data used for training.

---

# Real-Time Prediction

After a model has been trained, the dashboard automatically provides a prediction interface.

For example, if the model uses:

```text
age
salary
rooms
```

the dashboard dynamically creates input fields:

```text
Age       [ 35 ]

Salary    [ 70000 ]

Rooms     [ 3 ]
```

When the user clicks:

```text
Predict
```

the Streamlit frontend sends the input values to:

```text
POST /predict/{model_name}
```

For example:

```text
POST /predict/linear
```

The FastAPI backend:

```text
Input Values
     ↓
Load Saved Model
     ↓
model.predict()
     ↓
Prediction
     ↓
Return Result
     ↓
Streamlit Dashboard
```

Example:

```text
Predicted Value

82.45
```

This is a real prediction generated by the trained ML model.

---

# Example Dataset

The repository contains:

```text
train_sample.csv
```

Example structure:

```text
age,salary,rooms,price

30,50000,2,200000
40,80000,3,350000
50,100000,4,450000
22,42000,1,150000
36,72000,3,300000
28,52000,2,220000
```

For this dataset:

```text
Features:
age
salary
rooms

Target:
price
```

The model learns to estimate:

```text
price
```

from:

```text
age + salary + rooms
```

---

# Authentication

The application uses JWT-based authentication.

## Signup

```text
POST /signup
```

Example:

```json
{
    "username": "testuser",
    "password": "1234"
}
```

---

## Login

```text
POST /login
```

Example:

```json
{
    "username": "testuser",
    "password": "1234"
}
```

Successful login returns:

```json
{
    "access_token": "JWT_TOKEN",
    "token_type": "bearer"
}
```

The JWT is required for protected API endpoints.

---

# Token-Based Usage Control

The project includes a token/credit system to demonstrate API usage control.

| Action      | Tokens Required |
| ----------- | --------------: |
| Train Model |               1 |
| Predict     |               5 |
| Add Tokens  |               0 |
| List Models |               0 |

The token balance can be viewed using:

```text
GET /tokens/{username}
```

Tokens can be added using:

```text
POST /add_tokens
```

Example:

```json
{
    "username": "testuser",
    "credit_card": "1111-2222-3333-4444",
    "amount": 20
}
```

### Note

The credit-card field is only part of the original demonstration token system.

It does **not** process real payments.

---

# API Endpoints

| Method | Endpoint                | Description                   |
| ------ | ----------------------- | ----------------------------- |
| POST   | `/signup`               | Register a new user           |
| POST   | `/login`                | Authenticate and receive JWT  |
| POST   | `/add_tokens`           | Add demonstration tokens      |
| GET    | `/tokens/{username}`    | Get token balance             |
| POST   | `/train`                | Upload CSV and train ML model |
| GET    | `/models`               | List user's trained models    |
| POST   | `/predict/{model_name}` | Generate prediction           |
| DELETE | `/remove_user`          | Delete the authenticated user |
| GET    | `/health`               | Check API status              |

---

# API Workflow

The complete API workflow is:

```text
1. Signup
      ↓
2. Login
      ↓
3. Receive JWT
      ↓
4. Authorize API
      ↓
5. Add demonstration tokens
      ↓
6. Upload CSV
      ↓
7. Train model
      ↓
8. View trained models
      ↓
9. Send prediction input
      ↓
10. Receive prediction
```

---

# Example API Training Request

The `/train` endpoint accepts:

```text
multipart/form-data
```

Parameters:

```text
model_name: random_forest

features: age,salary,rooms

label: price

file: train_sample.csv
```

The backend trains the selected model and stores it.

---

# Example Prediction Request

After training a model:

```text
POST /predict/random_forest
```

Example request:

```json
{
    "age": 35,
    "salary": 70000,
    "rooms": 3
}
```

The API returns the model prediction.

---

# Trained Model Management

Each trained model is stored in the model storage directory.

Example:

```text
models_storage/
│
├── testuser_linear_XXXXXXXX.pkl
├── testuser_random_forest_XXXXXXXX.pkl
└── ...
```

Model metadata is stored in SQLite.

The dashboard displays information such as:

```text
Model Name
Model Type
Features
Target
Created At
Training Count
Prediction Count
```

Example:

```text
random_forest
regression
age, salary, rooms
price
```

---

# Streamlit Dashboard

The Streamlit application provides the following sections:

```text
1. Upload Dataset
2. Configure Machine Learning Model
3. Model Performance
4. Test Your Model
5. Your Trained Models
```

The dashboard allows users to perform the complete ML workflow without manually interacting with every API endpoint.

---

# Database

The application uses SQLite for persistent storage.

The database stores information such as:

* Users
* Password authentication information
* Token balances
* Trained model metadata
* Training counts
* Prediction counts

The database file is:

```text
app.db
```

---

# Database Path

The database path should be generated relative to the project directory so that FastAPI and Streamlit use the same database.

Recommended configuration in `dal.py`:

```python
import os

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DB_PATH = os.path.join(
    BASE_DIR,
    "app.db"
)
```

This prevents FastAPI and Streamlit from accidentally creating separate databases when launched from different working directories.

---

# Logging

Important application events are written to:

```text
server.log
```

Example:

```text
2026-09-01 18:04:02 - INFO - User testuser trained model linear
```

Logs can be used for debugging and monitoring application activity.

---

# Postman Testing

The project includes:

```text
FastAPI_ML_Postman_Collection.json
```

Import this collection into Postman to test the API.

The collection can be used to test:

```text
Signup
 ↓
Login
 ↓
Add Tokens
 ↓
Train Model
 ↓
List Models
 ↓
Predict
 ↓
Remove User
```

The training request requires:

```text
train_sample.csv
```

---

# Troubleshooting

| Problem                          | Cause                         | Solution                                        |
| -------------------------------- | ----------------------------- | ----------------------------------------------- |
| `404` on `/`                     | Root route not defined        | Normal behavior                                 |
| `401 Unauthorized`               | Invalid/missing JWT           | Login again and authorize                       |
| `402 Payment Required`           | Not enough tokens             | Add demonstration tokens                        |
| `Training failed`                | Invalid features/target       | Check CSV column names                          |
| `Invalid CSV`                    | File cannot be parsed         | Check CSV format                                |
| Streamlit cannot connect         | FastAPI is not running        | Start `uvicorn main:app --reload --port 8000`   |
| Streamlit starts on another port | Port 8501 is already occupied | Use the displayed Streamlit URL                 |
| No trained models appear         | Wrong database path           | Ensure `DB_PATH` is shared                      |
| Prediction fails                 | Model/input mismatch          | Use the same feature names used during training |
| XGBoost unavailable              | Package not installed         | Run `pip install xgboost`                       |

---

# Technologies Used

## Backend

* FastAPI
* Uvicorn
* Python

## Machine Learning

* Scikit-learn
* Pandas
* Joblib
* XGBoost (optional)

## Frontend

* Streamlit

## Database

* SQLite

## Authentication

* JWT / PyJWT
* HTTP Bearer Authentication
* bcrypt

## API Testing

* Swagger / OpenAPI
* Postman

---

# Key Features

### Machine Learning

* CSV-based model training
* Multiple ML algorithms
* Model persistence
* Real-time inference
* Performance metrics

### Web Application

* Interactive Streamlit dashboard
* Dataset preview
* Feature selection
* Target selection
* Model selection
* Prediction interface
* Trained model history

### Backend

* REST API
* JWT authentication
* Token-based usage control
* SQLite persistence
* Logging
* Model management

---

# Future Improvements

The following improvements can be added to make the project more robust:

1. Train/test dataset splitting
2. Cross-validation
3. RMSE metric
4. Confusion matrix for classification
5. Actual vs predicted visualization
6. Feature importance visualization
7. Automatic regression/classification detection
8. Categorical feature encoding
9. Missing-value preprocessing
10. Model comparison
11. Prediction history
12. Dataset preprocessing pipeline
13. Model download
14. Improved authentication UI
15. Deployment using Docker
16. Semantic/TTL knowledge layer

---

# Project Demonstration

The recommended demonstration flow is:

```text
Open Streamlit
      ↓
Login
      ↓
Upload CSV
      ↓
Preview Dataset
      ↓
Select Features
      ↓
Select Target
      ↓
Select ML Algorithm
      ↓
Train Model
      ↓
View MAE / R²
      ↓
Enter New Data
      ↓
Click Predict
      ↓
Display Prediction
      ↓
View Saved Model
```

This demonstrates the complete path from **raw dataset to trained Machine Learning model to real-time prediction**.
