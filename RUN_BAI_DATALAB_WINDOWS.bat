@echo off
setlocal
cd /d "%~dp0"

echo The B-AI DataLab v0.17.0

set "PYEXE="
py -3.12 -c "import sys" >nul 2>&1 && set "PYEXE=py -3.12"
if not defined PYEXE py -3.11 -c "import sys" >nul 2>&1 && set "PYEXE=py -3.11"
if not defined PYEXE python -c "import sys; raise SystemExit(0 if (3,11) ^<= sys.version_info[:2] ^< (3,13) else 1)" >nul 2>&1 && set "PYEXE=python"

if not defined PYEXE (
  echo.
  echo Python 3.11 or 3.12 is required.
  echo Install Python 3.12 from https://www.python.org/downloads/
  echo During installation, tick "Add python.exe to PATH".
  echo Then run this file again.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo.
  echo First-time setup: creating a local environment...
  %PYEXE% -m venv .venv || goto :error
  .venv\Scripts\python.exe -m pip install --upgrade pip || goto :error
  .venv\Scripts\python.exe -m pip install -r the-bai-datalab-streamlit\requirements.txt || goto :error
  .venv\Scripts\python.exe -m pip install -e .\the-bai-datalab-core || goto :error
)

echo.
echo Starting The B-AI DataLab. Your browser should open automatically.
cd the-bai-datalab-streamlit
..\.venv\Scripts\python.exe -m streamlit run app.py
exit /b 0

:error
echo.
echo Setup failed. Please take a screenshot of this window and send it to the project owner.
pause
exit /b 1
