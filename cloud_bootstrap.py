import os, shutil, tarfile, zipfile
from pathlib import Path
import streamlit as st, requests

@st.cache_resource(show_spinner=True)
def run_bootstrap() -> str:
    Path("data").mkdir(parents=True, exist_ok=True)
    Path("models").mkdir(parents=True, exist_ok=True)
    # Exemple: download_file("https://exemple.com/model.bin", "models/model.bin")
    return "bootstrap cloud: OK ✅"

def download_file(url: str, dst: str, timeout: int = 60):
    dst_path = Path(dst); dst_path.parent.mkdir(parents=True, exist_ok=True)
    if dst_path.exists() and dst_path.stat().st_size > 0: return
    r = requests.get(url, stream=True, timeout=timeout); r.raise_for_status()
    with open(dst_path, "wb") as f: shutil.copyfileobj(r.raw, f)