# src/extract.py

import pandas as pd

# Columnas clave para la tabla principal de películas
MOVIES_COLS = [
    "id", "budget", "genres", "keywords", "release_date", 
    "revenue", "runtime", "vote_average", "vote_count"
]

# Columnas clave para la tabla de créditos
CREDITS_COLS = [
    "movie_id", "cast", "crew"
]

# Definición de tipos para optimizar
MOVIES_TYPES = {
    'id': 'int32', 
    'budget': 'int64',
    'revenue': 'int64',
    'runtime': 'float32',
    'vote_average': 'float32',
    'vote_count': 'int32'
}


def extract_chunks(path: str, chunksize: int = 1000) -> list[pd.DataFrame]:
    """Lee el archivo de películas en chunks, optimizado para archivos más pequeños."""
    try:
        chunks = pd.read_csv(
            path, 
            chunksize=chunksize, 
            dtype=MOVIES_TYPES,
            usecols=MOVIES_COLS
        )
        return list(chunks)

    except Exception as e:
        print(f"ERROR al extraer {path}: {e}")
        return []

def extract_dim(path: str) -> pd.DataFrame:
    """Lee archivos de dimensión (créditos) y renombra la columna de ID."""
    try:
        df = pd.read_csv(path, usecols=CREDITS_COLS)
        # Renombrar para que coincida con el ID de la tabla de hechos
        df.rename(columns={'movie_id': 'id'}, inplace=True) 
        return df
    except Exception as e:
        print(f"ERROR al extraer archivo de esquema: {e}")
        return pd.DataFrame()