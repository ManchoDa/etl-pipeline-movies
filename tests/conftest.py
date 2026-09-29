import pandas as pd
import pytest


@pytest.fixture
def credits_df():
    return pd.DataFrame({
        "id": [1, 2, 3],
        "cast": ["[]", "[]", "[]"],
        "crew": [
            '[{"job": "Director", "name": "Christopher Nolan"}, {"job": "Producer", "name": "X"}]',
            '[{"job": "Writer", "name": "Y"}]',   # sin director
            "no es json valido",                  # dato corrupto real
        ],
    })


@pytest.fixture
def movies_df():
    return pd.DataFrame({
        "id": [1, 2, 3, 4],
        "budget": [1000, 500, 0, 200],
        "genres": [
            '[{"id": 28, "name": "Action"}]',
            '[{"id": 35, "name": "Comedy"}]',
            "[]",              # sin género -> se filtra
            "no es json",      # corrupto -> se filtra
        ],
        "keywords": ['[{"name": "hero"}]', "[]", "[]", "[]"],
        "release_date": ["2010-07-16", "2015-03-01", "2020-01-01", None],
        "revenue": [5000, 100, 0, 0],
        "runtime": [148.0, 90.0, 100.0, 100.0],
        "vote_average": [8.8, 6.0, 5.0, 5.0],
        "vote_count": [500, 50, 10, 10],
    })
