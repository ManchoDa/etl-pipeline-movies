import os
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL") or None
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY") or None
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY") or None
S3_REGION = os.getenv("S3_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET", "movies-lake")
RAW_PREFIX = "raw/"
STAGING_PREFIX = "staging/"
PROCESSED_PREFIX = "processed/"
DATASET_SLUG = "tmdb/tmdb-movie-metadata"
MOVIES_FILE = "tmdb_5000_movies.csv"
CREDITS_FILE = "tmdb_5000_credits.csv"
 