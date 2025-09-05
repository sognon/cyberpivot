#!/usr/bin/env python3
import subprocess as sp, os
from pathlib import Path
from textwrap import dedent

HERE = Path.cwd()

MAIN_PY = dedent("""
import os, importlib, streamlit as st
st.set_page_config(page_title="CyberPivot™", page_icon="🛡️", layout="wide")
try:
    from cloud_bootstrap import run_bootstrap
    st.caption(run_bootstrap())
except Exception as e:
    st.warning(f"Bootstrap non exécuté: {e}")
mod = importlib.import_module("main.app_cyberpivot")
if hasattr(mod, "main") and callable(mod.main):
    mod.main()
""").strip()

CLOUD_BOOTSTRAP_PY = dedent("""
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
""").strip()

def run(cmd):
    print(">", " ".join(cmd))
    sp.run(cmd, check=True)

if __name__ == "__main__":
    # 1) Écrire main.py + cloud_bootstrap.py
    (HERE/"main.py").write_text(MAIN_PY, encoding="utf-8")
    (HERE/"cloud_bootstrap.py").write_text(CLOUD_BOOTSTRAP_PY, encoding="utf-8")

    # 2) Déps min
    req = HERE/"requirements.txt"
    if not req.exists():
        req.write_text("streamlit\nrequests\n", encoding="utf-8")
    else:
        txt = req.read_text(encoding="utf-8")
        add = []
        if "streamlit" not in txt: add.append("streamlit")
        if "requests" not in txt: add.append("requests")
        if add: req.write_text(txt.rstrip()+"\n"+"\n".join(add)+"\n", encoding="utf-8")

    # 3) Git init + branche main
    if not (HERE/".git").exists():
        run(["git","init"])
    run(["git","checkout","-B","main"])

    # 4) Config remote
    remotes = sp.check_output(["git","remote"], text=True).split()
    if "origin" in remotes:
        run(["git","remote","set-url","origin","git@github.com:sognon/cyberpivot.git"])
    else:
        run(["git","remote","add","origin","git@github.com:sognon/cyberpivot.git"])

    # 5) Commit + push
    run(["git","add","-A"])
    try:
        run(["git","commit","-m","Deploy: entrypoint (app_cyberpivot) + cloud bootstrap"])
    except sp.CalledProcessError:
        print("• Rien à committer (ok)")
    run(["git","push","--force","--set-upstream","origin","main"])

    print("\n✅ Poussé sur sognon/cyberpivot (branche main).")
    print("➡️ Sur Streamlit Cloud, configure:")
    print("   • Repository: sognon/cyberpivot")
    print("   • Branch: main")
    print("   • Main file path: main.py")
    print("\n🌐 App publique: https://cyberpivot.streamlit.app/")


