from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any
import json, logging

from models import (
    SignupRequest, LoginRequest, DeleteUserRequest, AddTokensRequest,
    TrainResponse, PredictResponse, parse_features, create_jwt, decode_jwt
)
from dal import init_storage, list_users_simple
from bl import (
    bl_signup, bl_login, bl_delete_user, bl_add_tokens, bl_get_tokens, require_tokens,
    df_from_upload, train_model, predict_latest, list_user_models
)

import pandas as pd
import streamlit as st


# ===== Logs =====
logging.basicConfig(filename="server.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# ===== Lifespan=====
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_storage()
    logging.info("App started")
    yield

app = FastAPI(title="Complete ML API", lifespan=lifespan)

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Auth dependency=====
bearer_scheme = HTTPBearer(auto_error=True)


def get_current_username(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    token = credentials.credentials
    try:
        payload = decode_jwt(token)
        return str(payload["sub"])
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid/expired token")

# ===== Health =====
@app.get("/health")
def health():
    return {"ok": True}

# ===== Users =====
@app.post("/signup")
def signup(req: SignupRequest):
    try:
        bl_signup(req.username, req.password)
        return {"status": "ok"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login")
def login(req: LoginRequest):
    if not bl_login(req.username, req.password):
        raise HTTPException(status_code=401, detail="Bad credentials")
    token = create_jwt(req.username)
    logging.info(f"User {req.username} logged in")
    return {"access_token": token, "token_type": "bearer"}

@app.delete("/remove_user")
def remove_user(req: DeleteUserRequest, current_user: str = Depends(get_current_username)):
    if req.username != current_user:
        raise HTTPException(status_code=403, detail="Can delete only your own user")
    try:
        bl_delete_user(req.username, req.password)
        return {"status": "deleted"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/tokens/{username}")
def tokens(username: str, current_user: str = Depends(get_current_username)):
    if username != current_user:
        raise HTTPException(status_code=403, detail="Can view only your own tokens")
    return {"tokens": bl_get_tokens(username)}

@app.post("/add_tokens")
def add_tokens(req: AddTokensRequest, current_user: str = Depends(get_current_username)):
    if req.username != current_user:
        raise HTTPException(status_code=403, detail="Can add tokens only to yourself")
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    tokens = bl_add_tokens(req.username, req.amount)
    return {"status": "tokens added", "tokens": tokens}

# ===== ML =====
@app.post("/train", response_model=TrainResponse)
async def train(
    model_name: str = Form(...),
    features: str = Form(...),
    label: str = Form(...),
    file: UploadFile = File(...),
    model_params: Optional[str] = Form(None),
    current_user: str = Depends(get_current_username)
):
    # 1 token
    try:
        require_tokens(current_user, 1)
    except ValueError as e:
        raise HTTPException(status_code=402, detail=str(e))

    content = await file.read()
    try:
        df = df_from_upload(content)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV")

    feats = parse_features(features)
    params: Dict[str, Any] = {}
    if model_params:
        try:
            params = json.loads(model_params)
        except Exception:
            params = {}

    try:
        res = train_model(current_user, df, model_name, feats, label, params)
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/models")
def models(current_user: str = Depends(get_current_username)):
    # 1 token
    try:
        require_tokens(current_user, 1)
    except ValueError as e:
        raise HTTPException(status_code=402, detail=str(e))
    return {"models": list_user_models(current_user)}

@app.post("/predict/{model_name}", response_model=PredictResponse)
def predict(model_name: str, body: Dict[str, Any], current_user: str = Depends(get_current_username)):
    # 5 tokens
    try:
        require_tokens(current_user, 5)
    except ValueError as e:
        raise HTTPException(status_code=402, detail=str(e))
    try:
        pred = predict_latest(current_user, model_name, body)
        return {"prediction": pred}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ===== Streamlit Dashboard=====
#  (להריץ בעוד חלון streamlit run main.py)
if __name__ == "__main__":

    init_storage()
    st.set_page_config(page_title="Users & Tokens", layout="wide")
    st.title("Users & Tokens Dashboard (Simple)")
    st.caption("קריאה ישירה ל-SQLite – ללא שרת API")
    rows = list_users_simple()
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No users yet. Use /signup then /add_tokens via the API.")
