# src/load.py (Modificado)

import pandas as pd
import os

def save_output(df: pd.DataFrame or dict, path: str, mode: str = 'csv', append: bool = False):
    """
    Guarda el DataFrame o múltiples DataFrames (diccionario) en CSV.
    Si es un diccionario, los guarda con el nombre del path base y la clave del diccionario.
    """
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    if isinstance(df, dict):
        # Si es un diccionario (resultados de KPIs)
        for name, data_frame in df.items():
            final_path = os.path.join(os.path.dirname(path), f"{name}_{os.path.basename(path)}")
            print(f"Guardando KPI {name} en {final_path}")
            data_frame.to_csv(final_path, index=False, mode='w')
    else:
        # Si es un solo DataFrame (chunks o tabla de hechos limpia)
        if append and os.path.exists(path):
            df.to_csv(path, index=False, mode='a', header=False)
        else:
            df.to_csv(path, index=False, mode='w')