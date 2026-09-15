from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator


default_args = {
    "owner": "danie",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="movie_etl_pipeline",
    description="ETL pipeline for TMDB movie metadata",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["movies", "etl", "pandas"],
) as dag:

    def download_data():
        from src.download import download_dataset

        download_dataset(
            "tmdb/tmdb-movie-metadata",
            [
                "tmdb_5000_movies.csv",
                "tmdb_5000_credits.csv",
            ],
            "data/raw/",
        )

    def extract_data():
        from src.extract import extract_chunks, extract_dim

        credits_path = "data/raw/tmdb_5000_credits.csv"
        movies_path = "data/raw/tmdb_5000_movies.csv"

        credits_df = extract_dim(credits_path)
        movies_chunks = extract_chunks(movies_path)

        if not movies_chunks:
            raise ValueError("Movie extraction failed.")

        # Guardamos temporalmente los datos para la siguiente task.
        # Más adelante sustituiremos esto por un almacenamiento mejor.
        import pickle

        with open("/tmp/credits_df.pkl", "wb") as f:
            pickle.dump(credits_df, f)

        with open("/tmp/movies_chunks.pkl", "wb") as f:
            pickle.dump(movies_chunks, f)

    def transform_data():
        import os
        import pickle

        from src.transform import transform_chunk
        from src.load import save_output

        with open("/tmp/credits_df.pkl", "rb") as f:
            credits_df = pickle.load(f)

        with open("/tmp/movies_chunks.pkl", "rb") as f:
            movies_chunks = pickle.load(f)

        processed_path = "data/processed/processed_movies_data.csv"

        if os.path.exists(processed_path):
            os.remove(processed_path)

        for i, chunk in enumerate(movies_chunks):
            cleaned_chunk = transform_chunk(chunk, credits_df)

            save_output(
                cleaned_chunk,
                processed_path,
                append=(i > 0),
            )

    def calculate_kpis():
        import pandas as pd

        from src.transform import calculate_kpis
        from src.load import save_output

        processed_path = "data/processed/processed_movies_data.csv"

        df = pd.read_csv(processed_path)

        kpis_df = calculate_kpis(df)

        save_output(
            kpis_df,
            "data/processed/tmdb_movie_kpis.csv",
        )

    download_task = PythonOperator(
        task_id="download_data",
        python_callable=download_data,
    )

    extract_task = PythonOperator(
        task_id="extract_data",
        python_callable=extract_data,
    )

    transform_task = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data,
    )

    kpi_task = PythonOperator(
        task_id="calculate_kpis",
        python_callable=calculate_kpis,
    )

    download_task >> extract_task >> transform_task >> kpi_task