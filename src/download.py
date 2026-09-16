import os
import shutil
from kaggle.api.kaggle_api_extended import KaggleApi
def download_dataset(dataset_slug: str, file_names: list[str], target_dir: str):
    """Descarga archivos específicos de un dataset de Kaggle si no existen."""
    
    # Comprobación simple: si el primer archivo existe, asumimos que todo fue descargado
    files_exist = all(
        os.path.exists(os.path.join(target_dir, file_name))
        for file_name in file_names
    )

    if files_exist:
        print("Todos los archivos ya existen. Saltando descarga de Kaggle.")
        return
        
    print(f"Descargando y preparando dataset: {dataset_slug}...")
    
    os.makedirs(target_dir, exist_ok=True)
    
    # Autentica y descarga
    try:
        api = KaggleApi()
        api.authenticate()
        
        # Descarga el dataset completo al directorio target_dir y descomprime
        api.dataset_download_files(dataset_slug, path=target_dir, unzip=True)
        
        print(f"Dataset {dataset_slug} descargado y descomprimido en {target_dir}.")
            
    except Exception as e:
        print(f"Error al usar la API de Kaggle: {e}")
        print("Asegúrate de que la variable de entorno KAGGLE_API_TOKEN esté configurada.")
        raise