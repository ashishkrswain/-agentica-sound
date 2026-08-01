@echo off
setlocal
echo ===================================================
echo     Agentica Sound - Local AI Music Studio (Suno AI)
echo ===================================================
echo.
cd /d "%~dp0"

set PYTHON_CMD=C:\Users\ashis\AppData\Local\Programs\Python\Python310\python.exe
if not exist "%PYTHON_CMD%" (
    set PYTHON_CMD=python
)

echo Starting backend server on http://127.0.0.1:8000 ...
echo GPU Hardware: NVIDIA GeForce GTX 1650 (CUDA 12.8)
echo.

"%PYTHON_CMD%" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
pause
