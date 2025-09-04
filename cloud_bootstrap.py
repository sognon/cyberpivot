# cloud_bootstrap.py
import os
import shutil
import tarfile
import zipfile
from pathlib import Path
from typing import Iterable, Optional

import streamlit as st
import requests

@st.cache_resource(show_spinner=True)
def run_bootstrap() -> str:
    """
    Portage Cloud du bootstrap : exécute 1 seule fois côté serveur Streamlit Cloud.
    ➜ Convertit les étapes usuelles d'un .sh :
       - mkdir -p -> Path(...).mkdir(parents=True, exist_ok=True)
       - wget/curl -> download_file()
       - unzip/tar -> extract_zip()/extract_tar()
       - export VAR=... -> lire st.secrets["VAR"] ou os.environ["VAR"]
       - chmod -> inutile sauf cas spécifiques (Streamlit exécute en user-space)
    ⚠️ apt-get/sudo : à déclarer dans packages.txt (une ligne par paquet), pas ici.
    """

    # ========= 1) Répertoires requis =========
    ensure_dirs([
        "data",
        "models",
        "artifacts",
        # ajoute ici d'autres dossiers créés par bootstrap2.sh
    ])

    # ========= 2) Variables d'env / secrets =========
    # Exemple : API keys envoyées via Settings → Secrets
    # API_KEY = env("API_KEY")
    # ENDPOINT = env("ENDPOINT_URL", default="https://api.example.com")

    # ========= 3) Téléchargements nécessaires =========
    # ➜ Remplace tes 'wget/curl' ici :
    # download_file("https://exemple.com/model.bin", "models/model.bin")
    # download_file("https://exemple.com/archive.zip", "artifacts/archive.zip")

    # ========= 4) Extractions =========
    # if Path("artifacts/archive.zip").exists() and not Path("artifacts/unpacked").exists():
    #     extract_zip("artifacts/archive.zip", "artifacts/unpacked")

    # if Path("artifacts/model.tar.gz").exists() and not Path("models/weights").exists():
    #     extract_tar("artifacts/model.tar.gz", "models")

    # ========= 5) Pré-initialisations (ex: DB sqlite, fichiers vides, etc.) =========
    # touch("data/.init_ok")

    return "bootstrap cloud: OK ✅"

# ------------------- Helpers -------------------

def env(key: str, default: Optional[str] = None) -> str:
    """Lis une variable d'env depuis os.environ ou st.secrets."""
    if key in os.environ and os.environ[key]:
        return os.environ[key]
    try:
        return st.secrets[key]
    except Exception:
        if default is not None:
            return default
        raise RuntimeError(f"Secret/var `{key}` manquant. Ajoute-le dans Settings → Secrets.")

def ensure_dirs(paths: Iterable[str]) -> None:
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)

def touch(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).touch(exist_ok=True)

def download_file(url: str, dst: str, timeout: int = 60) -> None:
    dst_path = Path(dst)
    if dst_path.exists() and dst_path.stat().st_size > 0:
        return
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, stream=True, timeout=timeout)
    r.raise_for_status()
    with open(dst_path, "wb") as f:
        shutil.copyfileobj(r.raw, f)

def extract_zip(src_zip: str, dst_dir: str) -> None:
    with zipfile.ZipFile(src_zip, "r") as zf:
        zf.extractall(dst_dir)

def extract_tar(src_tar: str, dst_dir: str) -> None:
    mode = "r:gz" if src_tar.endswith(".gz") else "r:"
    with tarfile.open(src_tar, mode) as tf:
        tf.extractall(dst_dir)

