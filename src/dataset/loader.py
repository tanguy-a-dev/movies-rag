import pandas as pd

from src.settings import settings


def load_movies():
    if not settings.dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found at {settings.dataset_path}")

    return pd.read_csv(settings.dataset_path)
