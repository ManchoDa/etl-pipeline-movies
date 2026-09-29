"""
Tests de storage.py con el cliente S3 simulado (unittest.mock).

No dependen de SeaweedFS/MinIO real levantado: así pueden correr en CI
sin infraestructura, comprobando que storage.py llama a boto3 con los
parámetros correctos.
"""
from unittest.mock import MagicMock, patch

import pandas as pd

from src import storage


def test_put_df_uploads_csv_bytes_to_expected_key():
    df = pd.DataFrame({"a": [1, 2]})
    with patch("src.storage.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        storage.put_df(df, "processed/movies/part-0000.csv", bucket="movies-lake")

        mock_client.put_object.assert_called_once()
        _, kwargs = mock_client.put_object.call_args
        assert kwargs["Bucket"] == "movies-lake"
        assert kwargs["Key"] == "processed/movies/part-0000.csv"
        assert "1" in kwargs["Body"]  # el csv serializado contiene los datos


def test_get_df_reads_csv_from_s3_object():
    csv_bytes = b"a,b\n1,2\n3,4\n"
    with patch("src.storage.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_object.return_value = {"Body": pd.io.common.BytesIO(csv_bytes)}
        mock_get_client.return_value = mock_client

        df = storage.get_df("staging/credits/credits.csv")

        assert list(df.columns) == ["a", "b"]
        assert len(df) == 2


def test_list_keys_returns_only_keys_from_response():
    with patch("src.storage.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list_objects_v2.return_value = {
            "Contents": [{"Key": "raw/a.csv"}, {"Key": "raw/b.csv"}]
        }
        mock_get_client.return_value = mock_client

        keys = storage.list_keys("raw/")

        assert keys == ["raw/a.csv", "raw/b.csv"]


def test_list_keys_empty_prefix_returns_empty_list():
    with patch("src.storage.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.list_objects_v2.return_value = {}  # sin "Contents"
        mock_get_client.return_value = mock_client

        assert storage.list_keys("staging/nada/") == []


def test_ensure_bucket_ignores_already_exists_error():
    with patch("src.storage.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.exceptions.BucketAlreadyOwnedByYou = Exception
        mock_client.exceptions.BucketAlreadyExists = Exception
        mock_client.create_bucket.side_effect = mock_client.exceptions.BucketAlreadyOwnedByYou()
        mock_get_client.return_value = mock_client

        storage.ensure_bucket("movies-lake")  # no debe lanzar excepción

        mock_client.create_bucket.assert_called_once_with(Bucket="movies-lake")
