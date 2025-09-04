import pandas as pd, yaml, os

def excel_to_yaml(excel_path, yaml_path):
    df = pd.read_excel(excel_path)
    required = ["domain", "id", "question"]
    if not all(col in df.columns for col in required):
        raise ValueError(f"Excel doit contenir les colonnes: {', '.join(required)}")
    rows = []
    for _, r in df.iterrows():
        rows.append({
            "domain": str(r["domain"]),
            "id": str(r["id"]),
            "question": str(r["question"])
        })
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(rows, f, allow_unicode=True)

def load_yaml(yaml_path):
    with open(yaml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

