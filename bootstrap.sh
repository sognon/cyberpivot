#!/usr/bin/env bash
set -euo pipefail

# --- Aller dans le dossier du script
cd "$(dirname "$0")"

echo "== CyberPivot bootstrap =="
echo "Dossier: $(pwd)"

# --- Activer le venv s'il existe
if [ -f ".venv/bin/activate" ]; then
  echo "Activation du venv .venv ..."
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
  pip install matplotlib numpy
  pip install passlib[bcrypt]
else
  echo "⚠️ Aucun venv .venv détecté (ok mais tu dois avoir streamlit installé globalement)."
fi

# --- Initialisation DB (auth + storage)
echo "== Initialisation des bases =="

set +e
python - <<'PY'
import sys, traceback

def log(msg: str):
    print(msg, flush=True)

ok = True
try:
    import bootstrap
    log("• bootstrap.py détecté → bootstrap.init_app_db()")
    res = bootstrap.init_app_db()
    ok = bool(res)
except Exception as e:
    log(f"! Import bootstrap échoué: {e}")
    log("→ Fallback: init direct via auth/storage")
    try:
        import auth, storage

        if hasattr(auth, 'init_auth_db'):
            auth.init_auth_db()
            log("  - auth.init_auth_db() OK")
        else:
            log("  - auth.init_auth_db() introuvable (ignoré)")

        if hasattr(storage, 'init_db'):
            storage.init_db()
            log("  - storage.init_db() OK")
        else:
            log("  - storage.init_db() introuvable (ignoré)")

    except Exception as e4:
        ok = False
        log(f"!! Import auth/storage échoué: {e4}")
        traceback.print_exc()

if ok:
    log("✅ Initialisation terminée SANS erreur.")
    sys.exit(0)
else:
    log("⚠️ Initialisation terminée AVEC erreurs.")
    sys.exit(1)
PY
rc=$?
set -e

if [ $rc -eq 0 ]; then
  echo "== ✅ bootstrap OK"
else
  echo "== ⚠️ bootstrap en erreur (code $rc)"
fi

# --- Lancer Streamlit
echo "== Lancement de l'app Streamlit =="
exec streamlit run app_cyberpivot.py


