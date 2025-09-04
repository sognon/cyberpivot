# validators.py — garde-fous pour les fichiers Excel de normes
import pandas as pd

REQUIRED_COLS = { 'Domain', 'QID', 'Item', 'Question', 'Level' }

def load_norme_excel(file_like) -> pd.DataFrame:
    try:
        df = pd.read_excel(file_like, engine='openpyxl')
    except ImportError as e:
        raise RuntimeError("Dépendance manquante : openpyxl") from e
    except Exception as e:
        raise ValueError(f'Excel illisible: {e}')
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise ValueError('Colonnes manquantes: ' + ', '.join(sorted(missing)))
    if df.empty:
        raise ValueError('Le fichier Excel est vide.')
    return df
