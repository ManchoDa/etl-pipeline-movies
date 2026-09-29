# src/storage.py
"""
Funciones simples para leer y escribir CSVs en un almacenamiento
compatible con S3 (SeaweedFS en local, AWS S3 en producción).

Los objetos en S3 son inmutables (no existe "append"), así que los datos
por chunks se guardan como varios archivos part-0000.csv, part-0001.csv...
dentro de un mismo prefijo, y se leen todos juntos con get_df_parts.
"""
import io

import boto3
import pandas as pd

from src import config


def get_client():
    return boto3.client(
        "s3",
        endpoint_url=config.S3_ENDPOINT_URL,
        aws_access_key_id=config.S3_ACCESS_KEY,
        aws_secret_access_key=config.S3_SECRET_KEY,
        region_name=config.S3_REGION,
    )


def ensure_bucket(bucket: str = config.S3_BUCKET) -> None:
    """Crea el bucket. Si ya existe (ejecuciones/reintentos previos), no hace nada."""
    client = get_client()
    try:
        client.create_bucket(Bucket=bucket)
    except (client.exceptions.BucketAlreadyOwnedByYou, client.exceptions.BucketAlreadyExists):
        pass


def put_df(df: pd.DataFrame, key: str, bucket: str = config.S3_BUCKET) -> None:
    """Guarda un DataFrame como CSV en s3://bucket/key."""
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    get_client().put_object(Bucket=bucket, Key=key, Body=buffer.getvalue())


def get_df(key: str, bucket: str = config.S3_BUCKET) -> pd.DataFrame:
    """Lee un CSV de s3://bucket/key como DataFrame."""
    obj = get_client().get_object(Bucket=bucket, Key=key)
    return pd.read_csv(obj["Body"])


def list_keys(prefix: str, bucket: str = config.S3_BUCKET) -> list[str]:
    """Todas las claves bajo un prefijo."""
    response = get_client().list_objects_v2(Bucket=bucket, Prefix=prefix)
    return [obj["Key"] for obj in response.get("Contents", [])]


def get_df_parts(prefix: str, bucket: str = config.S3_BUCKET) -> pd.DataFrame:
    """Lee y concatena todos los part-*.csv bajo un prefijo."""
    keys = list_keys(prefix, bucket)
    return pd.concat([get_df(k, bucket) for k in keys], ignore_index=True)