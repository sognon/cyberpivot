# standards.py — gestion des normes (YAML), génération depuis Excel, et utilitaires
from typing import Dict, Any, List
from pathlib import Path
import hashlib
import yaml
import pandas as pd

# Dossiers : standards/ pour les normes, standards/cache/ pour les YAML générés
STANDARDS_DIR = Path("standards")
CACHE_DIR = STANDARDS_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def list_standards() -> List[str]:
    """
    Retourne les normes disponibles en fichiers YAML dans standards/.
    Exemple: ["iso42001", "iso27001"]
    """
    if not STANDARDS_DIR.exists():
        return []
    return sorted([p.stem for p in STANDARDS_DIR.glob("*.yaml") if p.name != "cache.yaml"])

def load_standard(name_or_path: str) -> Dict[str, Any]:
    """
    Charge une norme depuis son nom (ex: 'iso42001') ou un chemin YAML.
    """
    p = Path(name_or_path)
    yaml_path = p if p.exists() else (STANDARDS_DIR / f"{name_or_path}.yaml")
    with open(yaml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def flatten_to_dataframe(std: Dict[str, Any]) -> pd.DataFrame:
    """
    Aplati la structure YAML en DataFrame avec les colonnes attendues par l’app.
    Colonnes : Domaine, ID, Item, Question, Objectif, Preuve attendue, Référence, Critère, Recommandation
    """
    rows = []
    for d in std.get("domains", []):
        dname = d.get("name", "")
        for c in d.get("controls", []):
            rows.append({
                "Domaine": dname,
                "ID": c.get("id", ""),
                "Item": c.get("item", ""),
                "Question": c.get("question", ""),
                "Objectif": c.get("objective", ""),
                "Preuve attendue": c.get("evidence", ""),
                "Référence": c.get("reference", ""),
                "Critère": c.get("criterion", ""),
                "Recommandation": c.get("recommendation", ""),
            })
    return pd.DataFrame(rows)

def df_to_yaml(df: pd.DataFrame, title: str = "Custom Catalog", version: str = "") -> Dict[str, Any]:
    """
    Convertit un DataFrame (Excel importé) vers la structure YAML standardisée.
    """
    required = ["Domaine","ID","Item","Question","Objectif","Preuve attendue","Référence","Critère","Recommandation"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Colonne manquante dans le questionnaire: {col}")

    domains = []
    for dname, block in df.groupby("Domaine"):
        controls = []
        for _, r in block.iterrows():
            controls.append({
                "id": str(r["ID"]) if pd.notna(r["ID"]) else "",
                "item": _norm(r["Item"]),
                "question": _norm(r["Question"]),
                "objective": _norm(r["Objectif"]),
                "evidence": _norm(r["Preuve attendue"]),
                "reference": _norm(r["Référence"]),
                "criterion": _norm(r["Critère"]),
                "recommendation": _norm(r["Recommandation"]),
            })
        domains.append({"name": str(dname), "controls": controls})

    return {
        "title": title,
        "version": str(version) if version else "",
        "domains": domains,
    }

def save_yaml_catalog(catalog: Dict[str, Any], out_path: Path) -> Path:
    """
    Sauvegarde un catalogue YAML sur disque.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(catalog, f, allow_unicode=True, sort_keys=False)
    return out_path

def hash_dataframe(df: pd.DataFrame) -> str:
    """
    Hash stable d’un questionnaire (pour le cache). On trie colonnes/rows et remplit les NaN.
    """
    norm = df.copy()
    norm = norm.reindex(sorted(norm.columns), axis=1).fillna("")
    norm = norm.sort_values(by=list(norm.columns)).reset_index(drop=True)
    b = norm.to_csv(index=False).encode("utf-8")
    return hashlib.sha256(b).hexdigest()

def _norm(x) -> str:
    return "" if x is None else str(x).strip()

