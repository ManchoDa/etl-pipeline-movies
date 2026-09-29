import numpy as np
import pandas as pd

from src.transform import calculate_kpis, get_director, get_first_value, transform_chunk


class TestGetFirstValue:
    def test_extracts_first_name(self):
        assert get_first_value('[{"id": 1, "name": "Action"}]') == "Action"

    def test_empty_list_returns_nan(self):
        assert pd.isna(get_first_value("[]"))

    def test_malformed_json_returns_nan(self):
        assert pd.isna(get_first_value("esto no es json"))

    def test_none_returns_nan(self):
        assert pd.isna(get_first_value(None))


class TestGetDirector:
    def test_finds_director_among_crew(self):
        crew = '[{"job": "Writer", "name": "A"}, {"job": "Director", "name": "B"}]'
        assert get_director(crew) == "B"

    def test_no_director_in_crew_returns_nan(self):
        assert pd.isna(get_director('[{"job": "Producer", "name": "A"}]'))

    def test_malformed_json_returns_nan(self):
        assert pd.isna(get_director("no es json"))


class TestTransformChunk:
    def test_enriches_and_filters_correctly(self, movies_df, credits_df):
        result = transform_chunk(movies_df, credits_df)
        # las filas 3 y 4 no tienen género válido -> deben quedar filtradas
        assert len(result) == 2
        assert set(result["id"]) == {1, 2}

    def test_computes_profit_as_revenue_minus_budget(self, movies_df, credits_df):
        result = transform_chunk(movies_df, credits_df)
        row = result[result["id"] == 1].iloc[0]
        assert row["profit"] == 5000 - 1000

    def test_extracts_director_via_join(self, movies_df, credits_df):
        result = transform_chunk(movies_df, credits_df)
        row = result[result["id"] == 1].iloc[0]
        assert row["director"] == "Christopher Nolan"

    def test_movie_without_director_gets_nan(self, movies_df, credits_df):
        result = transform_chunk(movies_df, credits_df)
        row = result[result["id"] == 2].iloc[0]
        assert pd.isna(row["director"])

    def test_output_has_expected_columns(self, movies_df, credits_df):
        result = transform_chunk(movies_df, credits_df)
        expected = {"id", "release_year", "main_genre", "director", "vote_average", "vote_count", "profit"}
        assert set(result.columns) == expected


class TestCalculateKpis:
    def test_returns_both_rankings(self):
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "main_genre": ["Action", "Action", "Comedy"],
            "director": ["A", "A", "B"],
            "profit": [100, 300, 50],
            "vote_average": [8.0, 7.0, 6.0],
            "vote_count": [200, 100, 5],
        })
        kpis = calculate_kpis(df)
        assert set(kpis.keys()) == {"genre_ranking", "director_ranking"}

    def test_director_ranking_excludes_low_vote_counts(self):
        # director B tiene pocos votos en total (< 100) y debe quedar fuera
        df = pd.DataFrame({
            "id": [1, 2],
            "main_genre": ["Action", "Comedy"],
            "director": ["A", "B"],
            "profit": [100, 50],
            "vote_average": [8.0, 9.0],
            "vote_count": [200, 5],
        })
        kpis = calculate_kpis(df)
        assert "A" in kpis["director_ranking"]["director"].values
        assert "B" not in kpis["director_ranking"]["director"].values

    def test_genre_ranking_sorted_by_profit_descending(self):
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "main_genre": ["Action", "Comedy", "Drama"],
            "director": ["A", "B", "C"],
            "profit": [50, 500, 100],
            "vote_average": [7, 7, 7],
            "vote_count": [100, 100, 100],
        })
        kpis = calculate_kpis(df)
        genres_in_order = kpis["genre_ranking"]["main_genre"].tolist()
        assert genres_in_order[0] == "Comedy"  # el de mayor profit
