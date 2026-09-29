import pandas as pd

from src.extract import extract_chunks, extract_dim


def test_extract_chunks_reads_only_expected_columns(tmp_path):
    csv_path = tmp_path / "movies.csv"
    df = pd.DataFrame({
        "id": [1, 2], "budget": [100, 200], "genres": ["[]", "[]"],
        "keywords": ["[]", "[]"], "release_date": ["2020-01-01", "2021-01-01"],
        "revenue": [10, 20], "runtime": [90.0, 100.0], "vote_average": [7.0, 8.0],
        "vote_count": [10, 20], "title": ["A", "B"],  # columna extra que debe ignorarse
    })
    df.to_csv(csv_path, index=False)

    chunks = extract_chunks(str(csv_path), chunksize=1)
    assert len(chunks) == 2
    assert "title" not in chunks[0].columns
    assert "id" in chunks[0].columns


def test_extract_chunks_missing_file_returns_empty_list():
    assert extract_chunks("/ruta/que/no/existe.csv") == []


def test_extract_dim_renames_movie_id_to_id(tmp_path):
    csv_path = tmp_path / "credits.csv"
    pd.DataFrame({"movie_id": [1, 2], "cast": ["[]", "[]"], "crew": ["[]", "[]"]}).to_csv(csv_path, index=False)

    result = extract_dim(str(csv_path))
    assert "id" in result.columns
    assert "movie_id" not in result.columns


def test_extract_dim_missing_file_returns_empty_dataframe():
    result = extract_dim("/ruta/que/no/existe.csv")
    assert result.empty
