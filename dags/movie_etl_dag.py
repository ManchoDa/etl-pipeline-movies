# dags/movie_etl_pipeline.py
"""
ETL pipeline for TMDB movie metadata.

Flujo: download -> extract (a staging) -> transform (a processed) -> calculate_kpis
"""
from __future__ import annotations

import logging
import os
import tempfile
from datetime import datetime, timedelta

from airflow.sdk import dag, task
from airflow.exceptions import AirflowFailException

logger = logging.getLogger(__name__)


default_args = {
    "owner": "danie",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
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
        from src import config, storage
        from src.download import download_dataset

        storage.ensure_bucket()

        with tempfile.TemporaryDirectory() as tmp_dir:
            download_dataset(
                config.DATASET_SLUG,
                [config.MOVIES_FILE, config.CREDITS_FILE],
                tmp_dir,
            )
            for name in (config.MOVIES_FILE, config.CREDITS_FILE):
                local_path = os.path.join(tmp_dir, name)
                storage.get_client().upload_file(
                    local_path, config.S3_BUCKET, f"{config.RAW_PREFIX}{name}"
                )
 
        logger.info("Raw subido a s3://%s/%s", config.S3_BUCKET, config.RAW_PREFIX)

    @task
    def extract_data() -> dict:
        """Lee el raw (columnas/tipos definidos en src/extract.py) y lo deja en staging/."""
        import tempfile
 
        from src import config, storage
        from src.extract import extract_chunks, extract_dim
 
        with tempfile.TemporaryDirectory() as tmp_dir:
            movies_local = os.path.join(tmp_dir, config.MOVIES_FILE)
            credits_local = os.path.join(tmp_dir, config.CREDITS_FILE)
            storage.get_client().download_file(
                config.S3_BUCKET, f"{config.RAW_PREFIX}{config.MOVIES_FILE}", movies_local
            )
            storage.get_client().download_file(
                config.S3_BUCKET, f"{config.RAW_PREFIX}{config.CREDITS_FILE}", credits_local
            )
 
            credits_df = extract_dim(credits_local)
            movies_chunks = extract_chunks(movies_local)
 
        if credits_df.empty or not movies_chunks:
            raise AirflowFailException("Extract no produjo datos válidos.")
 
        credits_key = f"{config.STAGING_PREFIX}credits/credits.csv"
        movies_prefix = f"{config.STAGING_PREFIX}movies/"
 
        storage.put_df(credits_df, credits_key)
        for i, chunk in enumerate(movies_chunks):
            storage.put_df(chunk, f"{movies_prefix}part-{i:04d}.csv")
 
        logger.info("Extract OK: %s chunks, %s filas de créditos", len(movies_chunks), len(credits_df))
        return {"credits_key": credits_key, "movies_prefix": movies_prefix}

    @task
    def transform_data(staged_paths: dict) -> str:
        """Lee staging/, limpia y enriquece chunk a chunk, y escribe en processed/."""
        from src import config, storage
        from src.transform import transform_chunk
 
        credits_df = storage.get_df(staged_paths["credits_key"])
        movie_keys = storage.list_keys(staged_paths["movies_prefix"])
 
        processed_prefix = f"{config.PROCESSED_PREFIX}movies/"
        total_rows = 0
        for i, key in enumerate(movie_keys):
            cleaned = transform_chunk(storage.get_df(key), credits_df)
            total_rows += len(cleaned)
            storage.put_df(cleaned, f"{processed_prefix}part-{i:04d}.csv")
 
        if total_rows == 0:
            raise AirflowFailException("Transform produjo 0 filas.")
 
        logger.info("Transform OK: %s filas en %s chunks", total_rows, len(movie_keys))
        return processed_prefix

    @task
    def calculate_kpis(processed_prefix: str) -> None:
        """Calcula los KPIs a partir de processed/ y los guarda en processed/kpis/."""
        from src import config, storage
        from src.transform import calculate_kpis as compute_kpis
 
        df = storage.get_df_parts(processed_prefix)
 
        for name, frame in compute_kpis(df).items():
            storage.put_df(frame, f"{config.PROCESSED_PREFIX}kpis/{name}.csv")
 
        logger.info("KPIs guardados en s3://%s/%skpis/", config.S3_BUCKET, config.PROCESSED_PREFIX)
 
    downloaded = download_data()
    staged = extract_data()
    processed = transform_data(staged)
    calculate_kpis(processed)
 
    downloaded >> staged
 
 
movie_etl_pipeline()
 