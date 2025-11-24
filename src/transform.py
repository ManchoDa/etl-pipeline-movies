# src/transform.py

import pandas as pd
import numpy as np
import ast # Necesario para convertir strings de JSON en estructuras de Python

def get_first_value(json_str, key_name='name'):
    """
    Función auxiliar para extraer el primer valor 'name' de una lista de JSONs.
    Se usa para géneros, palabras clave, director, etc.
    """
    try:
        # ast.literal_eval convierte la string que parece JSON en una lista/dict de Python
        list_of_dicts = ast.literal_eval(json_str)
        if list_of_dicts:
            return list_of_dicts[0][key_name]
    except:
        pass
    return np.nan # Devuelve NaN si falla la conversión o no hay datos

def get_director(crew_json):
    """
    Función auxiliar para extraer el nombre del director de la lista de 'crew'.
    """
    try:
        list_of_dicts = ast.literal_eval(crew_json)
        for crew_member in list_of_dicts:
            if crew_member.get('job') == 'Director':
                return crew_member.get('name')
    except:
        pass
    return np.nan

def transform_chunk(df: pd.DataFrame, credits_df: pd.DataFrame) -> pd.DataFrame:
    """Realiza la limpieza y Feature Engineering de un chunk de datos de películas."""
    
    df_clean = df.copy()
    
    # 1. ENRIQUECIMIENTO (JOIN)
    # Unir la tabla de películas con la tabla de créditos por ID
    df_clean = df_clean.merge(credits_df, on='id', how='left')
    
    # 2. LIMPIEZA DE DATOS SEMIESTRUCTURADOS (JSON)
    # Extraer el primer género y la primera palabra clave
    df_clean['main_genre'] = df_clean['genres'].apply(get_first_value)
    df_clean['main_keyword'] = df_clean['keywords'].apply(get_first_value)
    
    # Extraer el nombre del director
    df_clean['director'] = df_clean['crew'].apply(get_director)

    # 3. FEATURE ENGINEERING Y CONVERSIÓN DE TIPOS
    
    # Calcular Rentabilidad: Revenue - Budget (manejo de nulos)
    # Se rellenan nulos con 0 antes de la operación para evitar NaN en el resultado
    df_clean['profit'] = df_clean['revenue'].fillna(0) - df_clean['budget'].fillna(0)
    
    # Extraer el año de lanzamiento
    df_clean['release_year'] = pd.to_datetime(df_clean['release_date'], errors='coerce').dt.year
    
    # 4. FILTRADO: Eliminar películas sin datos esenciales o sin rentabilidad
    # Nos quedamos con películas que tienen un género y una fecha
    df_clean.dropna(subset=['main_genre', 'release_year'], inplace=True)
    
    # 5. SELECCIÓN FINAL: Seleccionar solo las columnas procesadas para la carga
    return df_clean[[
        'id', 'release_year', 'main_genre', 'director', 
        'vote_average', 'vote_count', 'profit'
    ]]

def calculate_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula las métricas clave agregadas por Género y Director."""
    
    # KPI 1: Géneros más rentables (promedio de rentabilidad)
    genre_kpis = df.groupby('main_genre').agg(
        AVG_PROFIT=('profit', 'mean'),
        TOTAL_MOVIES=('id', 'count')
    ).reset_index()
    
    genre_kpis['PROFIT_RANK'] = genre_kpis['AVG_PROFIT'].rank(method='min', ascending=False)
    
    # KPI 2: Directores más votados (promedio ponderado de votos)
    # Usamos una fórmula simple: Directores con al menos 100 votos
    director_kpis = df.groupby('director').agg(
        AVG_VOTE=('vote_average', 'mean'),
        TOTAL_VOTES=('vote_count', 'sum'),
        MOVIES_COUNT=('id', 'count')
    ).reset_index()
    
    director_kpis = director_kpis[director_kpis['TOTAL_VOTES'] >= 100]
    director_kpis.sort_values(by='AVG_VOTE', ascending=False, inplace=True)

    # Combinamos ambos KPIs en un diccionario para cargarlos por separado
    return {
        'genre_ranking': genre_kpis.sort_values(by='PROFIT_RANK'),
        'director_ranking': director_kpis.head(10) # Top 10 directores
    }