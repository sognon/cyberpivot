# validators.py — chargement Excel/CSV & normalisation

import pandas as pd

REQUIRED_COLS = ["Domain", "QID", "Item", "Question"]

def load_norme_excel(file) -> pd.DataFrame:
    name = getattr(file, "name", "").lower()
    if name.endswith(".csv"):
        df = pd.read_csv(file, encoding="utf-8")
    else:
        df = pd.read_excel(file)

    cols = list(df.columns)
    alias = {c.lower().strip(): c for c in cols}
    def pick(key):
        for k in alias:
            if k == key.lower(): return alias[k]
        return None

    out = pd.DataFrame()
    for c in REQUIRED_COLS:
        src = pick(c) or c
        out[c] = df[src] if src in df.columns else ""

    out["Level"] = df[pick("Level")] if pick("Level") in df.columns else "No"
    out["Comment"] = df[pick("Comment")] if pick("Comment") in df.columns else ""

    for c in ["Domain","QID","Item","Question","Level","Comment"]:
        out[c] = out[c].astype("string").fillna("").map(lambda v: str(v) if v is not None else "")

    # garder les lignes où au moins un identifiant est renseigné
    mask = (out["Domain"].str.strip()!="") | (out["QID"].str.strip()!="") | (out["Item"].str.strip()!="")
    out = out[mask].reset_index(drop=True)
    return out


