import os
import shutil
from kaggle.api.kaggle_api_extended import KaggleApi
KAGGLE_TOKEN="KGAT_b2988ea483c3b7b10a9296470ed8ab3f"
def download_dataset(dataset_slug: str, file_names: list[str], target_dir: str):
    """Descarga archivos específicos de un dataset de Kaggle si no existen."""
    
    # Comprobación simple: si el primer archivo existe, asumimos que todo fue descargado
    if os.path.exists(os.path.join(target_dir, file_names[0])):
        print(f"✅ Archivos clave ya existen. Saltando descarga de Kaggle.")
        return
        
    print(f"⏳ Descargando y preparando dataset: {dataset_slug}...")
    
    os.makedirs(target_dir, exist_ok=True)
    
    # Autentica y descarga
    try:
        os.environ['KAGGLE_API_TOKEN'] = KAGGLE_TOKEN
        api = KaggleApi()
        api.authenticate()
        
        # Descarga el dataset completo al directorio target_dir y descomprime
        api.dataset_download_files(dataset_slug, path=target_dir, unzip=True)
        
        print(f"🎉 Dataset {dataset_slug} descargado y descomprimido en {target_dir}.")
            
    except Exception as e:
        print(f"❌ Error al usar la API de Kaggle: {e}")
        print("Asegúrate de que la variable de entorno KAGGLE_API_TOKEN esté configurada.")