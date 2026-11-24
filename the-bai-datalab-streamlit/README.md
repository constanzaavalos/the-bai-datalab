# The B-AI DataLab Streamlit v0.11.1

v0.11 adds protected Instructor Mode.

## What changes

- Dynamic navigation uses `st.Page` + `st.navigation`.
- Students see Home, Model Doctor, and Instructor sign in.
- The Instructor Dashboard is **not present in navigation** until authentication succeeds.
- The Instructor page also performs a server-side session check before loading analytics.
- Instructor credentials are read from `.streamlit/secrets.toml`.
- Logout removes instructor access from the current Streamlit session.
- SQLite learning analytics remain unchanged.

## Configure instructor credentials

Copy:

```bash
cp .streamlit/secrets.example.toml .streamlit/secrets.toml
```

Then edit:

```toml
[instructor]
username = "instructor"
password = "USE_A_LONG_UNIQUE_PASSWORD"
```

`.streamlit/secrets.toml` is ignored by Git.

## Run

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e ../the-bai-datalab-core
python -m streamlit run app.py
```

## Security note

This shared-secret login is appropriate for the local/research prototype.
For institutional deployment, replace it with university SSO/OIDC or another
identity provider.


## v0.11.1 student-workspace changes

- Adds **Start new submission** to clear the active analysis and file uploader.
- Clears the previous student code before a new submission to reduce accidental attribution.
- Keeps completed/incomplete historical attempts in SQLite for Instructor Mode.
- Removes Reasoning History from the student-facing Model Doctor page.
- Removes duplicate hint rendering when the evaluator returns the same hint already displayed.
- A new SQLite session is created only when the next bundle is analysed.

## v0.12.1

Model Doctor is now fast-first. Deterministic feedback is the default and requires no API call. AI can be used on demand or automatically after unresolved reasoning. The core rule library also includes advanced model families, multilevel models, nonlinear models, validation/tuning, regularisation, pipelines, imputation and leakage checks.


## v0.12.1 patch
- Replaced non-emoji navigation icons with Streamlit-compatible emoji icons.
