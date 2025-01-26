import pandas as pd

def load_dataset(source: str) -> pd.core.frame.DataFrame:
    pd_vectors = pd.read_json(source)
    return pd_vectors.drop(columns=["text"], errors="ignore").fillna("")