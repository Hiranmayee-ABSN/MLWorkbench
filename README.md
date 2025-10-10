# Final Project - FastAPI Machine Learning Server

Author: Dvir Cabessa  
Date: 2025-10-10  
Environment: Python 3.10+

---

## Project Overview
A complete FastAPI-based Machine Learning API that supports:
- Uploading CSV datasets
- Training and saving ML models (Linear Regression, Random Forest, Logistic Regression, SVR; optional XGBoost)
- Performing predictions using trained models
- JWT-based authentication
- Token-based usage control
- Streamlit dashboard for monitoring users and tokens

---

## Project Structure
```
FinalProject_FastAPI/
│
├── main.py                             # FastAPI app + optional Streamlit dashboard
├── bl.py                               # Business logic (training, prediction, tokens)
├── dal.py                              # Data access (SQLite + joblib model persistence)
├── models.py                           # Pydantic schemas, JWT helpers, model registry
├── app.db                              # SQLite database (auto-created)
├── train_sample.csv                    # Example dataset
├── server.log                          # Server logs
├── FastAPI_ML_Postman_Collection.json  # Postman test collection
└── README.md                           # This file
```

Note on database path: in `dal.py` the variable `DB_PATH` defines where `app.db` is created. Use an absolute path or compute it from `__file__` so both FastAPI and Streamlit point to the same database, for example:
```python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")
```

---

## Installation and Setup

### 1) Create virtual environment and install dependencies
```bash
python -m venv .venv
. .venv/Scripts/activate   # Windows PowerShell
pip install --upgrade pip
pip install -r requirements.txt
```

If you do not have `requirements.txt`, use:
```txt
xgboost
streamlit
fastapi
pandas
scikit-learn
joblib
pyjwt
pydantic
python-multipart
uvicorn
bcrypt
contextvars
```

### 2) Run the API server
```bash
uvicorn main:app --reload --port 8000
```
Swagger UI: http://localhost:8000/docs

### 3) Optional: Run the Streamlit dashboard
```bash
streamlit run main.py
```

---

## Authentication and Tokens
- `POST /login` returns a JWT `access_token`.
- Protected routes require HTTP Bearer token.
- In Swagger:
  1. Call `POST /login` with JSON credentials.
  2. Copy the `access_token` from the response.
  3. Click **Authorize** and paste only the token (Swagger adds `Bearer` automatically).
  4. Use the protected routes.

Token policy:

| Action | Tokens Required |
|--------|------------------|
| Train Model (`/train`) | 1 |
| Get Models List (`/models`) | 1 |
| Predict (`/predict/{model_name}`) | 5 |
| Add Tokens (`/add_tokens`) | 0 |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/signup` | Register a new user |
| POST | `/login` | Authenticate and receive JWT |
| POST | `/add_tokens` | Add tokens to user balance |
| GET | `/tokens/{username}` | Get token balance |
| POST | `/train` | Train a model using CSV |
| GET | `/models` | List user models |
| POST | `/predict/{model_name}` | Predict using a trained model |
| DELETE | `/remove_user` | Delete a user (requires own JWT) |
| GET | `/health` | Health check |

Note: `/` and `/favicon.ico` are not defined and will return 404 by design.

---

## Example Swagger Flow

1. `POST /signup`
```json
{"username": "dvir", "password": "1234"}
```
2. `POST /login` → copy `access_token`
```json
{"username": "dvir", "password": "1234"}
```
3. Click **Authorize** and paste the token.  
4. `POST /add_tokens`
```json
{"username": "dvir", "credit_card": "1111-2222-3333-4444", "amount": 20}
```
5. `POST /train` (multipart/form-data)  
   - model_name: linear  
   - features: age,salary,rooms  
   - label: price  
   - file: train_sample.csv  
   - model_params: {} (optional)  
6. `GET /models`
7. `POST /predict/linear`
```json
{"age": 35, "salary": 70000, "rooms": 3}
```
8. `DELETE /remove_user`
```json
{"username": "dvir", "password": "1234"}
```

---

## Testing with Postman
Import `FastAPI_ML_Postman_Collection.json`. The collection includes the full flow:
Signup → Login → Add Tokens → Train → Models → Predict → Remove User.  
Attach `train_sample.csv` to the training request or store it in the same folder.

---

## Logging
All significant actions are written to `server.log`, e.g.:
```
2025-10-10 14:05:33 - INFO - User dvir trained model linear
2025-10-10 14:10:12 - WARNING - User dvir attempted prediction without enough tokens
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| 404 on `/` or `/favicon.ico` | Root route not defined | Normal behavior |
| 401 Unauthorized | Missing or invalid JWT | Login again and re-authorize |
| 402 Payment Required | Not enough tokens | Use `/add_tokens` |
| Training error | CSV headers mismatch | Ensure `features` and `label` exist in the CSV |
| Streamlit shows no users | Streamlit and API use different DB paths | Unify `DB_PATH` in `dal.py` |

---

## Technologies
- Backend: FastAPI, SQLite, joblib
- Machine Learning: scikit-learn, pandas (optional XGBoost)
- Monitoring UI: Streamlit
- Auth: JWT (PyJWT)

---

## Author
Dvir Cabessa  
Bar-Ilan University – Technology Management  
Ecom College – AI Development Program  
Email: dvicabi@gmail.com
