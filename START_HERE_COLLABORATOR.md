# The B-AI DataLab v0.17.0 — Collaborator Run Package

This folder is prepared so a collaborator can run the **exact v0.17.0 research-prototype baseline locally**.

## What you need

- Windows 10/11, macOS, or Linux
- Python **3.11 or 3.12** (3.12 recommended)
- Internet access the first time only, so Python can install the required packages

Python can be downloaded from: https://www.python.org/downloads/

## Fastest way to run

### macOS

1. Unzip this folder.
2. Double-click **`RUN_BAI_DATALAB_MAC.command`**.
3. If macOS blocks it the first time, right-click the file → **Open** → **Open**.
4. The first run creates a local Python environment and installs dependencies. This can take a few minutes.
5. The app should open in the default browser at `http://localhost:8501`.

### Windows

1. Unzip this folder.
2. Double-click **`RUN_BAI_DATALAB_WINDOWS.bat`**.
3. The first run creates a local Python environment and installs dependencies. This can take a few minutes.
4. The app should open in the default browser at `http://localhost:8501`.

### Linux

From a terminal in this folder:

```bash
chmod +x RUN_BAI_DATALAB_LINUX.sh
./RUN_BAI_DATALAB_LINUX.sh
```

## Important: no AI key is required

The default mode is **Deterministic only**. The complete student environment runs locally without an OpenAI, Gemini, Groq, Anthropic, or Mistral API key.

The optional AI modes can be selected from the sidebar and require the collaborator's own provider API key. Do not share API keys in email or commit them to source control.

## Student modules in this version

- Model Doctor
- Model Court
- Leakage Detective
- Break the Model
- Uncertainty Lab
- Human vs AI Statistician

## Instructor Mode

Instructor Mode is optional. To enable it locally:

1. Open `the-bai-datalab-streamlit/.streamlit/`.
2. Copy `secrets.example.toml` and rename the copy to `secrets.toml`.
3. Replace the placeholder password with a long local password.
4. Restart the app.

Do not share or commit the resulting `secrets.toml` file.

## Stop the app

Close the terminal/command window, or press **Ctrl+C** in it.

## Start it again later

Run the same `RUN_BAI_DATALAB_...` file. Dependencies will not be reinstalled unless the local `.venv` folder has been deleted.

## If the first run fails

Check:

```text
python --version
```

or on macOS/Linux:

```text
python3 --version
```

It should report Python 3.11 or 3.12. If Python is installed but the script still cannot locate it, open a terminal in this folder and run the manual commands below.

## Manual installation (fallback)

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r the-bai-datalab-streamlit/requirements.txt
python -m pip install -e ./the-bai-datalab-core
cd the-bai-datalab-streamlit
python -m streamlit run app.py
```

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\the-bai-datalab-streamlit\requirements.txt
python -m pip install -e .\the-bai-datalab-core
cd .\the-bai-datalab-streamlit
python -m streamlit run app.py
```

## Version / research status

This is **The B-AI DataLab v0.17.0**, the frozen research-prototype baseline used for the current scholarly work. It is an implemented proof of concept and does not itself constitute evidence of educational effectiveness.
