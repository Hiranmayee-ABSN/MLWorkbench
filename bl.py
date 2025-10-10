import io, os, time, hashlib, logging
from typing import Dict, Any, List
import pandas as pd

from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score, f1_score

from models import MODEL_REGISTRY
from dal import (
    create_user, get_user, delete_user, add_tokens, get_tokens, deduct_tokens,
    insert_model_meta, save_model, load_model, list_models, get_latest_model,
    inc_user, inc_model, MODELS_DIR
)

# ===== Logs =====
logging.basicConfig(
    filename="server.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ===== Hash  =====
_SALT = "basic_salt"
def hash_password(pw: str) -> str:
    return hashlib.sha256(f"{_SALT}:{pw}".encode("utf-8")).hexdigest()

# ===== Users =====
def bl_signup(username: str, password: str) -> None:
    if get_user(username):
        raise ValueError("User exists")
    create_user(username, hash_password(password))
    logging.info(f"User {username} registered")

def bl_login(username: str, password: str) -> bool:
    u = get_user(username)
    return bool(u and u["password_hash"] == hash_password(password))

def bl_delete_user(username: str, password: str) -> None:
    u = get_user(username)
    if not u or u["password_hash"] != hash_password(password):
        raise ValueError("Bad credentials")
    delete_user(username)
    logging.info(f"User {username} deleted")

def bl_add_tokens(username: str, amount: int) -> int:
    add_tokens(username, amount)
    logging.info(f"User {username} added {amount} tokens")
    return get_tokens(username)

def bl_get_tokens(username: str) -> int:
    return get_tokens(username)

def require_tokens(username: str, amount: int) -> None:
    if not deduct_tokens(username, amount):
        raise ValueError("Not enough tokens")

# ===== Data =====
def df_from_upload(bytes_data: bytes) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(bytes_data))

# ===== Train =====
def train_model(username: str, df: pd.DataFrame,
                model_name: str, features: List[str], label: str,
                model_params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    if model_name not in MODEL_REGISTRY:
        raise ValueError("Unknown model")
    info = MODEL_REGISTRY[model_name]
    Model = info["ctor"]
    model_type = info["type"]

    missing = [c for c in features + [label] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    X = df[features].apply(pd.to_numeric, errors="coerce")
    y = pd.to_numeric(df[label], errors="coerce") if model_type == "regression" else df[label]

    tmp = pd.concat([X, y], axis=1).dropna()
    X, y = tmp[features], tmp[label]

    model = Model(**(model_params or {}))
    model.fit(X, y)

    metrics: Dict[str, float] = {}
    if model_type == "regression":
        yhat = model.predict(X)
        metrics["MAE"] = float(mean_absolute_error(y, yhat))
        metrics["R2"] = float(r2_score(y, yhat))
    else:
        yhat = model.predict(X)
        metrics["ACC"] = float(accuracy_score(y, yhat))
        metrics["F1"]  = float(f1_score(y, yhat, average="weighted"))

    fname = f"{username}_{model_name}_{int(time.time())}.pkl"
    fpath = os.path.join(MODELS_DIR, fname)
    save_model(fpath, model)
    meta = insert_model_meta(username, model_name, model_type, features, label, fpath)

    logging.info(f"User {username} trained {model_name} ({model_type}) feats={features} label={label}")
    return {
        "status": "model trained",
        "model_name": model_name,
        "features": features,
        "label": label,
        "metrics": metrics,
        "created_at": meta["created_at"]
    }

# ===== Predict =====
def predict_latest(username: str, model_name: str, payload: Dict[str, Any]) -> float | int:
    meta = get_latest_model(username, model_name)
    if not meta:
        raise ValueError("Model not found")
    model = load_model(meta["path"])
    feats = meta["features"]
    X = pd.DataFrame([{f: payload.get(f, None) for f in feats}], columns=feats).apply(pd.to_numeric, errors="coerce")
    if X.isna().any().any():
        raise ValueError("Missing or non-numeric features")
    pred = model.predict(X)
    inc_user(username, "predict_count", 1)
    inc_model(meta["id"], "predict_count", 1)
    logging.info(f"User {username} predict via {model_name}")
    val = pred[0] if hasattr(pred, "__len__") else pred
    try:
        return float(val)
    except Exception:
        return int(val)

def list_user_models(username: str) -> List[Dict[str, Any]]:
    return list_models(username)
