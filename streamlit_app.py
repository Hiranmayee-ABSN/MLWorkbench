import streamlit as st
import pandas as pd
import requests


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://127.0.0.1:8000"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="MLWorkbench — Interactive Machine Learning Training & Prediction Platform",
    page_icon="🤖",
    layout="wide",
)


# ============================================================
# SESSION STATE
# ============================================================

if "token" not in st.session_state:
    st.session_state.token = None

if "username" not in st.session_state:
    st.session_state.username = None

if "dataset" not in st.session_state:
    st.session_state.dataset = None

if "trained" not in st.session_state:
    st.session_state.trained = False

if "trained_model" not in st.session_state:
    st.session_state.trained_model = None

if "features" not in st.session_state:
    st.session_state.features = []

if "label" not in st.session_state:
    st.session_state.label = None

if "metrics" not in st.session_state:
    st.session_state.metrics = {}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def auth_headers():

    return {
        "Authorization": (
            f"Bearer {st.session_state.token}"
        )
    }


def login(username, password):

    try:

        response = requests.post(
            f"{API_URL}/login",
            json={
                "username": username,
                "password": password,
            },
            timeout=10,
        )

        if response.status_code == 200:

            data = response.json()

            st.session_state.token = data[
                "access_token"
            ]

            st.session_state.username = username

            return True, "Login successful"

        return False, response.json().get(
            "detail",
            "Login failed",
        )

    except requests.exceptions.ConnectionError:

        return False, (
            "Cannot connect to FastAPI. "
            "Make sure uvicorn is running."
        )

    except Exception as e:

        return False, str(e)


def add_tokens(amount):

    try:

        response = requests.post(
            f"{API_URL}/add_tokens",
            headers=auth_headers(),
            json={
                "username": st.session_state.username,

                # This is only a demo field required
                # by the original repository.
                "credit_card":
                    "1111-2222-3333-4444",

                "amount": amount,
            },
            timeout=10,
        )

        if response.status_code == 200:

            return True, response.json()

        return False, response.json().get(
            "detail",
            "Could not add tokens",
        )

    except Exception as e:

        return False, str(e)


def get_tokens():

    try:

        response = requests.get(
            f"{API_URL}/tokens/"
            f"{st.session_state.username}",
            headers=auth_headers(),
            timeout=10,
        )

        if response.status_code == 200:

            return response.json()[
                "tokens"
            ]

        return None

    except Exception:

        return None


def train_model(
    uploaded_file,
    model_name,
    features,
    label,
):

    try:

        uploaded_file.seek(0)

        files = {
            "file": (
                uploaded_file.name,
                uploaded_file,
                "text/csv",
            )
        }

        data = {
            "model_name": model_name,

            "features":
                ",".join(features),

            "label": label,
        }

        response = requests.post(
            f"{API_URL}/train",
            headers=auth_headers(),
            files=files,
            data=data,
            timeout=120,
        )

        if response.status_code == 200:

            return True, response.json()

        try:
            detail = response.json().get(
                "detail",
                "Training failed",
            )
        except Exception:
            detail = response.text

        return False, detail

    except requests.exceptions.ConnectionError:

        return False, (
            "Cannot connect to FastAPI."
        )

    except Exception as e:

        return False, str(e)


def make_prediction(
    model_name,
    values,
):

    try:

        response = requests.post(
            f"{API_URL}/predict/{model_name}",
            headers=auth_headers(),
            json=values,
            timeout=30,
        )

        if response.status_code == 200:

            return True, response.json()

        try:
            detail = response.json().get(
                "detail",
                "Prediction failed",
            )
        except Exception:
            detail = response.text

        return False, detail

    except Exception as e:

        return False, str(e)


def get_models():

    try:

        response = requests.get(
            f"{API_URL}/models",
            headers=auth_headers(),
            timeout=10,
        )

        if response.status_code == 200:

            return response.json().get(
                "models",
                []
            )

        return []

    except Exception:

        return []


# ============================================================
# HEADER
# ============================================================

st.title("MLWorkbench — Interactive Machine Learning Training & Prediction Platform")

st.write(
    "Upload a dataset, select an ML model, "
    "train it and test predictions in real time."
)


# ============================================================
# SIDEBAR - LOGIN
# ============================================================

with st.sidebar:

    st.header("🔐 Authentication")

    if st.session_state.token:

        st.success(
            f"Logged in as "
            f"`{st.session_state.username}`"
        )

        tokens = get_tokens()

        if tokens is not None:

            st.metric(
                "Available Tokens",
                tokens,
            )

        if st.button(
            "Logout",
            use_container_width=True,
        ):

            st.session_state.token = None
            st.session_state.username = None
            st.session_state.trained = False

            st.rerun()

    else:

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password",
        )

        if st.button(
            "Login",
            use_container_width=True,
        ):

            success, message = login(
                username,
                password,
            )

            if success:

                st.success(message)
                st.rerun()

            else:

                st.error(message)

        st.info(
            "Use the account you created "
            "through the FastAPI API."
        )


# ============================================================
# REQUIRE LOGIN
# ============================================================

if not st.session_state.token:

    st.warning(
        "Please login from the sidebar "
        "before using the ML playground."
    )

    st.stop()


# ============================================================
# ADD TOKENS
# ============================================================

with st.expander(
    "💳 Demo Token Management"
):

    st.write(
        "The original project uses a demo "
        "credit/token mechanism."
    )

    token_amount = st.number_input(
        "Tokens to add",
        min_value=1,
        max_value=1000,
        value=20,
        step=1,
    )

    if st.button(
        "Add Demo Tokens"
    ):

        success, result = add_tokens(
            token_amount
        )

        if success:

            st.success(
                f"Tokens added. "
                f"Balance: "
                f"{result['tokens']}"
            )

            st.rerun()

        else:

            st.error(result)


# ============================================================
# STEP 1 - UPLOAD DATASET
# ============================================================

st.header("1️⃣ Upload Dataset")

uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"],
)


if uploaded_file is None:

    st.info(
        "Upload a CSV file to begin."
    )

    st.stop()


# ============================================================
# READ DATASET
# ============================================================

try:

    df = pd.read_csv(
        uploaded_file
    )

except Exception as e:

    st.error(
        f"Could not read CSV: {e}"
    )

    st.stop()


st.session_state.dataset = df


# ============================================================
# DATASET INFORMATION
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Rows",
        len(df),
    )

with col2:

    st.metric(
        "Columns",
        len(df.columns),
    )

with col3:

    st.metric(
        "Missing Values",
        int(df.isna().sum().sum()),
    )

with col4:

    st.metric(
        "Numeric Columns",
        len(
            df.select_dtypes(
                include="number"
            ).columns
        ),
    )


# ============================================================
# DATA PREVIEW
# ============================================================

with st.expander(
    "📊 Preview Dataset",
    expanded=True,
):

    st.dataframe(
        df.head(20),
        use_container_width=True,
    )


# ============================================================
# MISSING VALUES
# ============================================================

missing = df.isna().sum()

missing = missing[
    missing > 0
]

if len(missing) > 0:

    with st.expander(
        "⚠️ Missing Values"
    ):

        st.dataframe(
            missing.rename(
                "Missing Values"
            )
        )


# ============================================================
# STEP 2 - MODEL CONFIGURATION
# ============================================================

st.header(
    "2️⃣ Configure Machine Learning Model"
)


# Current repository supports these models.
available_models = [
    "linear",
    "random_forest",
    "svr",
]

# Add XGBoost only if installed
try:

    import xgboost

    available_models.append(
        "xgboost"
    )

except ImportError:

    pass


model_name = st.selectbox(
    "Select Model",
    available_models,
    format_func=lambda x: {
        "linear":
            "Linear Regression",

        "random_forest":
            "Random Forest",

        "svr":
            "Support Vector Regression",

        "xgboost":
            "XGBoost",
    }.get(x, x),
)


# ============================================================
# FEATURE / TARGET SELECTION
# ============================================================

columns = df.columns.tolist()


label = st.selectbox(
    "Select Target / Label",
    columns,
)


feature_options = [
    col
    for col in columns
    if col != label
]


features = st.multiselect(
    "Select Input Features",
    feature_options,
    default=feature_options,
)


# ============================================================
# VALIDATION
# ============================================================

if not features:

    st.warning(
        "Select at least one feature."
    )

    st.stop()


# ============================================================
# FEATURE PREVIEW
# ============================================================

st.write(
    "**Selected Features:**",
    ", ".join(features),
)

st.write(
    "**Target:**",
    label,
)

st.write(
    "**Model:**",
    model_name,
)


# ============================================================
# TRAIN MODEL
# ============================================================

if st.button(
    "🚀 Train Model",
    type="primary",
    use_container_width=True,
):

    with st.spinner(
        "Training model..."
    ):

        success, result = train_model(
            uploaded_file,
            model_name,
            features,
            label,
        )

    if success:

        st.session_state.trained = True

        st.session_state.trained_model = (
            model_name
        )

        st.session_state.features = (
            features
        )

        st.session_state.label = (
            label
        )

        st.session_state.metrics = (
            result.get(
                "metrics",
                {}
            )
        )

        st.success(
            "Model trained successfully!"
        )

    else:

        st.error(
            f"Training failed: {result}"
        )


# ============================================================
# MODEL PERFORMANCE
# ============================================================

if st.session_state.trained:

    st.header(
        "3️⃣ Model Performance"
    )

    metrics = (
        st.session_state.metrics
    )

    if metrics:

        metric_columns = st.columns(
            len(metrics)
        )

        for col, (name, value) in zip(
            metric_columns,
            metrics.items(),
        ):

            with col:

                st.metric(
                    name,
                    round(
                        float(value),
                        4,
                    ),
                )

    st.caption(
        "Note: these metrics are calculated "
        "on the training data by the original "
        "backend. They are not a proper "
        "hold-out/test-set evaluation."
    )


# ============================================================
# STEP 4 - LIVE PREDICTION
# ============================================================

if st.session_state.trained:

    st.header(
        "4️⃣ Test Your Model"
    )

    st.write(
        "Enter values for the selected "
        "features and get a prediction "
        "from the trained model."
    )

    prediction_values = {}

    input_columns = st.columns(
        min(
            3,
            len(
                st.session_state.features
            ),
        )
    )

    for index, feature in enumerate(
        st.session_state.features
    ):

        with input_columns[
            index % len(input_columns)
        ]:

            # Convert numeric columns
            # into number inputs.
            numeric_series = pd.to_numeric(
                df[feature],
                errors="coerce",
            )

            if numeric_series.notna().any():

                median_value = float(
                    numeric_series.median()
                )

                prediction_values[
                    feature
                ] = st.number_input(
                    feature,
                    value=median_value,
                )

            else:

                st.error(
                    f"Feature '{feature}' "
                    "must contain numeric "
                    "values for the current "
                    "backend."
                )

    st.write("")

    if st.button(
        "🔮 Predict",
        type="primary",
        use_container_width=True,
    ):

        with st.spinner(
            "Generating prediction..."
        ):

            success, result = make_prediction(
                st.session_state.trained_model,
                prediction_values,
            )

        if success:

            prediction = result[
                "prediction"
            ]

            st.success(
                "Prediction generated!"
            )

            st.metric(
                "Predicted Value",
                prediction,
            )

        else:

            st.error(
                f"Prediction failed: "
                f"{result}"
            )


# ============================================================
# STEP 5 - TRAINED MODEL HISTORY
# ============================================================

st.header(
    "5️⃣ Your Trained Models"
)

models = get_models()

if models:

    model_df = pd.DataFrame(
        models
    )

    st.dataframe(
        model_df,
        use_container_width=True,
    )

else:

    st.info(
        "No trained models yet."
    )
