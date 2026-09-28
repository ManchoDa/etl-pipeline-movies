# dags/movie_etl_pipeline.py
"""
ETL pipeline for TMDB movie metadata.

Flujo: download -> extract (a staging) -> transform (a processed) -> calculate_kpis
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta

from airflow.sdk import dag, task
from airflow.exceptions import AirflowFailException
from airflow.models import Variable

logger = logging.getLogger(__name__)

# --- Configuración centralizada ---
RAW_DIR = "data/raw/"
STAGING_DIR = "data/staging/"
PROCESSED_DIR = "data/processed/"

DATASET_SLUG = "tmdb/tmdb-movie-metadata"
MOVIES_FILE = "tmdb_5000_movies.csv"
CREDITS_FILE = "tmdb_5000_credits.csv"

STAGING_MOVIES_PATH = os.path.join(STAGING_DIR, "movies_staged.csv")
STAGING_CREDITS_PATH = os.path.join(STAGING_DIR, "credits_staged.csv")
PROCESSED_MOVIES_PATH = os.path.join(PROCESSED_DIR, "processed_movies_data.csv")
KPI_OUTPUT_PATH = os.path.join(PROCESSED_DIR, "tmdb_movie_kpis.csv")

default_args = {
    "owner": "danie",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    dag_id="movie_etl_pipeline",
    description="ETL pipeline for TMDB movie metadata: download, extract, transform, and compute KPIs.",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["movies", "etl", "pandas"],
)
def movie_etl_pipeline():
    """
    Pipeline TMDB: descarga el dataset de Kaggle, extrae los CSV raw a una
    capa de staging (tipos/columnas optimizados), transforma y enriquece
    los datos por chunks, y calcula KPIs de negocio (rentabilidad por
    género, ranking de directores).
    """

    @task
    def download_data() -> None:
        """Descarga los CSV de Kaggle si no existen ya en RAW_DIR."""
        from src.download import download_dataset

        download_dataset(DATASET_SLUG, [MOVIES_FILE, CREDITS_FILE], RAW_DIR)

    @task
    def extract_data() -> dict:
        """
        Lee los CSV raw (con los dtypes/columnas ya optimizados definidos
        en src/extract.py) y materializa el resultado en la capa de
        staging, para que transform_data no tenga que releer el raw.
        """
        from src.extract import extract_chunks, extract_dim
        from src.load import save_output

        movies_path = os.path.join(RAW_DIR, MOVIES_FILE)
        credits_path = os.path.join(RAW_DIR, CREDITS_FILE)

        for path in (movies_path, credits_path):
            if not os.path.exists(path):
                raise AirflowFailException(f"Required raw file missing: {path}")

        credits_df = extract_dim(credits_path)
        if credits_df.empty:
            raise AirflowFailException("Credits extraction returned an empty DataFrame.")

        movies_chunks = extract_chunks(movies_path)
        if not movies_chunks:
            raise AirflowFailException("Movies extraction returned no chunks.")

        # Persistimos el resultado de la extracción en staging
        save_output(credits_df, STAGING_CREDITS_PATH)

        if os.path.exists(STAGING_MOVIES_PATH):
            os.remove(STAGING_MOVIES_PATH)
        for i, chunk in enumerate(movies_chunks):
            save_output(chunk, STAGING_MOVIES_PATH, append=(i > 0))

        logger.info(
            "Extract completed: %s movie chunks, %s credit rows -> staged in %s",
            len(movies_chunks), len(credits_df), STAGING_DIR,
        )

        return {"credits_path": STAGING_CREDITS_PATH, "movies_path": STAGING_MOVIES_PATH}

    @task
    def transform_data(staged_paths: dict) -> str:
        """
        Lee de staging (no del raw), limpia y enriquece los datos por
        chunks, y guarda el resultado consolidado en PROCESSED_MOVIES_PATH.
        Devuelve solo la ruta del CSV procesado (no el DataFrame) para
        mantener el XCom liviano.
        """
        import pandas as pd

        from src.load import save_output
        from src.transform import transform_chunk

        credits_df = pd.read_csv(staged_paths["credits_path"])

        if os.path.exists(PROCESSED_MOVIES_PATH):
            os.remove(PROCESSED_MOVIES_PATH)

        chunk_iter = pd.read_csv(staged_paths["movies_path"], chunksize=1000)
        total_rows = 0
        for i, chunk in enumerate(chunk_iter):
            cleaned_chunk = transform_chunk(chunk, credits_df)
            total_rows += len(cleaned_chunk)
            save_output(cleaned_chunk, PROCESSED_MOVIES_PATH, append=(i > 0))

        if total_rows == 0:
            raise AirflowFailException(
                "Transform produced zero rows — check upstream filters "
                "(main_genre/release_year) in transform_chunk."
            )

        logger.info(
            "Transform completed: %s rows written to %s",
            total_rows, PROCESSED_MOVIES_PATH,
        )

        return PROCESSED_MOVIES_PATH

    @task
    def calculate_kpis(processed_path: str) -> None:
        """Lee el dataset procesado y calcula/guarda los KPIs de negocio."""
        import pandas as pd

        from src.load import save_output
        from src.transform import calculate_kpis as compute_kpis

        df = pd.read_csv(processed_path)
        if df.empty:
            raise AirflowFailException(f"No data found at {processed_path}")

        kpis = compute_kpis(df)
        save_output(kpis, KPI_OUTPUT_PATH)
        logger.info("KPIs saved with base path %s", KPI_OUTPUT_PATH)

    # --- Orquestación ---
    downloaded = download_data()
    staged = extract_data()
    processed = transform_data(staged)
    calculate_kpis(processed)

    downloaded >> staged


movie_etl_pipeline()