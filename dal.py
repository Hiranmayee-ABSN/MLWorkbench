import os, sqlite3, joblib
from typing import List, Dict, Any, Optional
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")
MODELS_DIR = os.environ.get("APP_MODELS_DIR", "models_storage")
os.makedirs(MODELS_DIR, exist_ok=True)

def init_storage() -> None:
    with sqlite3.connect(DB_PATH) as c:
        cur = c.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
          username TEXT PRIMARY KEY,
          password_hash TEXT NOT NULL,
          tokens INTEGER NOT NULL DEFAULT 0,
          models_count INTEGER NOT NULL DEFAULT 0,
          train_count INTEGER NOT NULL DEFAULT 0,
          predict_count INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL
        )""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS models(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          username TEXT NOT NULL,
          model_name TEXT NOT NULL,
          model_type TEXT NOT NULL,
          features TEXT NOT NULL,
          label TEXT NOT NULL,
          path TEXT NOT NULL,
          created_at TEXT NOT NULL,
          train_count INTEGER NOT NULL DEFAULT 0,
          predict_count INTEGER NOT NULL DEFAULT 0
        )""")
        c.commit()

# ===== Users =====
def create_user(username: str, password_hash: str) -> None:
    with sqlite3.connect(DB_PATH) as c:
        cur = c.cursor()
        cur.execute("INSERT INTO users(username,password_hash,tokens,created_at) VALUES(?,?,?,?)",
                    (username, password_hash, 0, datetime.utcnow().isoformat()))
        c.commit()

def get_user(username: str) -> Optional[Dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as c:
        cur = c.cursor()
        cur.execute("""SELECT username,password_hash,tokens,models_count,train_count,predict_count,created_at
                       FROM users WHERE username=?""", (username,))
        r = cur.fetchone()
        if not r: return None
        return {
            "username": r[0], "password_hash": r[1], "tokens": r[2],
            "models_count": r[3], "train_count": r[4], "predict_count": r[5],
            "created_at": r[6]
        }

def delete_user(username: str) -> None:
    with sqlite3.connect(DB_PATH) as c:
        cur = c.cursor()
        cur.execute("DELETE FROM users WHERE username=?", (username,))
        cur.execute("DELETE FROM models WHERE username=?", (username,))
        c.commit()

def add_tokens(username: str, amount: int) -> None:
    with sqlite3.connect(DB_PATH) as c:
        cur = c.cursor()
        cur.execute("UPDATE users SET tokens = tokens + ? WHERE username=?", (amount, username))
        c.commit()

def get_tokens(username: str) -> int:
    with sqlite3.connect(DB_PATH) as c:
        cur = c.cursor()
        cur.execute("SELECT tokens FROM users WHERE username=?", (username,))
        r = cur.fetchone()
        return int(r[0]) if r else 0

def deduct_tokens(username: str, amount: int) -> bool:
    with sqlite3.connect(DB_PATH) as c:
        cur = c.cursor()
        cur.execute("SELECT tokens FROM users WHERE username=?", (username,))
        r = cur.fetchone()
        if not r: return False
        t = int(r[0])
        if t < amount: return False
        cur.execute("UPDATE users SET tokens = tokens - ? WHERE username=?", (amount, username))
        c.commit()
        return True

def inc_user(username: str, field: str, delta: int = 1) -> None:
    with sqlite3.connect(DB_PATH) as c:
        cur = c.cursor()
        cur.execute(f"UPDATE users SET {field} = {field} + ? WHERE username=?", (delta, username))
        c.commit()

def list_users_simple() -> List[Dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as c:
        cur = c.cursor()
        cur.execute("""SELECT username,tokens,models_count,train_count,predict_count,created_at
                       FROM users ORDER BY username""")
        rows = cur.fetchall()
        return [
            {"username": r[0], "tokens": r[1], "models_count": r[2],
             "train_count": r[3], "predict_count": r[4], "created_at": r[5]}
            for r in rows
        ]

# ===== Models =====
def save_model(path: str, obj) -> None:
    joblib.dump(obj, path)

def load_model(path: str):
    return joblib.load(path)

def insert_model_meta(username: str, model_name: str, model_type: str,
                      features: List[str], label: str, path: str) -> Dict[str, Any]:
    created = datetime.utcnow().isoformat()
    with sqlite3.connect(DB_PATH) as c:
        cur = c.cursor()
        cur.execute("""INSERT INTO models(username,model_name,model_type,features,label,path,created_at,train_count,predict_count)
                       VALUES(?,?,?,?,?,?,?,1,0)""",
                    (username, model_name, model_type, ",".join(features), label, path, created))
        c.commit()
    inc_user(username, "models_count", 1)
    inc_user(username, "train_count", 1)
    return {"created_at": created}

def list_models(username: str) -> List[Dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as c:
        cur = c.cursor()
        cur.execute("""SELECT id,model_name,model_type,features,label,path,created_at,train_count,predict_count
                       FROM models WHERE username=? ORDER BY datetime(created_at) DESC""",
                    (username,))
        rows = cur.fetchall()
        return [{
            "id": r[0], "model_name": r[1], "model_type": r[2],
            "features": r[3].split(","), "label": r[4], "path": r[5],
            "created_at": r[6], "train_count": r[7], "predict_count": r[8]
        } for r in rows]

def get_latest_model(username: str, model_name: str) -> Optional[Dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as c:
        cur = c.cursor()
        cur.execute("""SELECT id,model_type,features,label,path
                       FROM models
                       WHERE username=? AND model_name=?
                       ORDER BY datetime(created_at) DESC LIMIT 1""",
                    (username, model_name))
        r = cur.fetchone()
        if not r: return None
        return {
            "id": r[0], "model_type": r[1],
            "features": r[2].split(","), "label": r[3], "path": r[4]
        }

def inc_model(model_id: int, field: str, delta: int = 1) -> None:
    with sqlite3.connect(DB_PATH) as c:
        cur = c.cursor()
        cur.execute(f"UPDATE models SET {field} = {field} + ? WHERE id=?", (delta, model_id))
        c.commit()
