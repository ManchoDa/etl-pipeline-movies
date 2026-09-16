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
        import os
        import sys

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
        import os
        from src.extract import extract_chunks, extract_dim

        credits_path = "data/raw/tmdb_5000_credits.csv"
        movies_path = "data/raw/tmdb_5000_movies.csv"


        if not os.path.exists(credits_path):
            raise FileNotFoundError(
                f"Credits file not found: {credits_path}"
            )

        if not os.path.exists(movies_path):
            raise FileNotFoundError(
                f"Movies file not found: {movies_path}"
            )

        credits_df = extract_dim(credits_path)
        movies_chunks = extract_chunks(movies_path)
        
        if credits_df.empty:
            raise ValueError("Credits extraction failed.")

        if not movies_chunks:
            raise ValueError("Movie extraction failed.")

        print(
            f"Extraction successful: "
            f"{len(movies_chunks)} movie chunks, "
            f"{len(credits_df)} credit records."
        )

    def transform_data():
        import os
        from src.extract import extract_chunks, extract_dim
        from src.transform import transform_chunk
        from src.load import save_output

        credits_path = "data/raw/tmdb_5000_credits.csv"
        movies_path = "data/raw/tmdb_5000_movies.csv"

        credits_df = extract_dim(credits_path)
        movies_chunks = extract_chunks(movies_path)

        if credits_df.empty:
            raise ValueError("Credits extraction failed.")

        if not movies_chunks:
            raise ValueError("Movie extraction failed.")

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
        print(
        f"Transformation completed: "
        f"{len(movies_chunks)} chunks processed."
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