import pandas as pd
from src.extract import extract_chunks, extract_dim
from src.transform import transform_chunk, calculate_kpis
from src.load import save_output
from src.download import download_dataset 
import os
import shutil

# --- Configuración del Dataset de Kaggle (TMDB) ---
KAGGLE_SLUG = "tmdb/tmdb-movie-metadata" 
RAW_DATA_DIR = "data/raw/"
MOVIES_FILE = "tmdb_5000_movies.csv"     # El archivo principal
CREDITS_FILE = "tmdb_5000_credits.csv"  # Archivo de dimensión (actores/directores)


def main():
    
    # 0. DESCARGA DE DATOS (Si no existen)
    download_dataset(KAGGLE_SLUG, [MOVIES_FILE, CREDITS_FILE], RAW_DATA_DIR) 

    print("--- 1. EXTRACCIÓN DE DATOS ---")
    
    # 1.1 Extracción de dimensiones (Créditos)
    credits_path = os.path.join(RAW_DATA_DIR, CREDITS_FILE)
    credits_df = extract_dim(credits_path)
    
    # 1.2 Extracción de hechos (Películas) en chunks (mantenemos chunking por buena práctica)
    movies_path = os.path.join(RAW_DATA_DIR, MOVIES_FILE)
    movies_chunks = extract_chunks(movies_path)
    
    if not movies_chunks:
        print("La extracción falló. Abortando pipeline.")
        return

    # Limpiar archivo previo
    processed_path = "data/processed/processed_movies_data.csv"
    if os.path.exists(processed_path):
        os.remove(processed_path)
    
    print("\n--- 2. TRANSFORMACIÓN DE DATOS (CHUNK A CHUNK) ---")

    for i, chunk in enumerate(movies_chunks):
        print(f"Procesando Chunk {i+1}...")
        
        # 2.1 Transformación (Limpieza y Feature Engineering)
        cleaned_chunk = transform_chunk(chunk, credits_df)
        
        # 2.2 Carga del chunk limpio (en modo append)
        save_output(cleaned_chunk, processed_path, append=(i > 0))

    print("\n--- 3. CÁLCULO DE KPIS Y CARGA FINAL ---")
    
    # 3.1 Carga del dataset limpio completo
    final_cleaned_df = pd.read_csv(processed_path)
    
    # 3.2 Cálculo de métricas
    kpis_df = calculate_kpis(final_cleaned_df)

    # 3.3 Carga de los KPIs
    save_output(kpis_df, "data/processed/tmdb_movie_kpis.csv")
    
    print(f"Resultado final (tmdb_movie_kpis.csv) guardado en data/processed/")
    print(f"Tabla de hechos limpia (processed_movies_data.csv) guardada en data/processed/")


if __name__ == "__main__":
    main()