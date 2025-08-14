# catalog.py — Excel -> YAML (cache par hash), lien avec l’audit
from pathlib import Path
import pandas as pd
import standards
import storage

CACHE_DIR = standards.CACHE_DIR

def cache_catalog_from_excel(audit_id: int, df: pd.DataFrame, title: str = "Custom Catalog", version: str = "") -> Path:
    """
    - Calcule un hash stable du questionnaire Excel
    - Génère un YAML (si pas déjà en cache)
    - Met à jour l’audit (yaml_path + catalog_hash)
    - Retourne le chemin du YAML
    """
    h = standards.hash_dataframe(df)
    yaml_path = CACHE_DIR / f"{h}.yaml"
    if not yaml_path.exists():
        catalog = standards.df_to_yaml(df, title=title, version=version)
        standards.save_yaml_catalog(catalog, yaml_path)
    storage.update_audit_catalog(audit_id, str(yaml_path), h)
    return yaml_path

def load_catalog_for_audit(audit: dict) -> pd.DataFrame:
    """
    - Si l’audit pointe vers un YAML caché (yaml_path), on le charge
    - Sinon on charge la norme de l’audit (audit['standard'])
    - Retourne un DataFrame aplati prêt pour l’app
    """
    ypath = (audit or {}).get("yaml_path")
    if ypath and Path(ypath).exists():
        std = standards.load_standard(ypath)
        return standards.flatten_to_dataframe(std)
    std = standards.load_standard(audit["standard"])
    return standards.flatten_to_dataframe(std)

