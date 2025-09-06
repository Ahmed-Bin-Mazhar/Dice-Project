# run_all.py
import subprocess
import time
import sys
import os

# Paths to your apps
FASTAPI_FILE ="Dice-Project\\utils\\kbc-ingestion.py"
STREAMLIT_FILE ="Dice-Project\\app.py"

def run_fastapi():
    """Run FastAPI app with uvicorn"""
    print("[INFO] Starting FastAPI...")

    # Change working directory to the folder containing your FastAPI file
    fastapi_dir = os.path.dirname(FASTAPI_FILE)
    fastapi_module = os.path.splitext(os.path.basename(FASTAPI_FILE))[0]  # filename without .py

    subprocess.Popen(
        [sys.executable, "-m", "uvicorn", f"{fastapi_module}:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=fastapi_dir  # set working directory
    )
    print("[INFO] FastAPI running on http://localhost:8000")

def run_streamlit():
    """Run Streamlit app"""
    print("[INFO] Starting Streamlit...")
    subprocess.Popen(["streamlit", "run", STREAMLIT_FILE])
    print("[INFO] Streamlit running")

if __name__ == "__main__":
    run_fastapi()
    time.sleep(6)  # wait a few seconds to ensure FastAPI is up
    run_streamlit()