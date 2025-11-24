# 🎬 ETL Pipeline: TMDB Movie Metadata (Python + Pandas)

This project implements a modular **ETL pipeline** (Extract, Transform, Load) to process the **TMDB Movie Metadata dataset**, using Python and Pandas.  
The goal is to demonstrate key data-engineering skills including:

- Chunk-based processing for large CSV files  
- Cleaning and transforming semi-structured fields (JSON-like strings)  
- Feature engineering (profitability, genre expansion, director extraction)  
- KPI generation for movie-related insights  
- A clean, maintainable ETL architecture  

---

# 🚀 Features

- **Automated download** from Kaggle using API token  
- **Chunked reading** of large datasets  
- **Parsing JSON-like columns** (`genres`, `keywords`, `production_companies`, etc.)  
- **Extraction of key fields** such as director, top genres, popularity metrics  
- **KPI computation** (profitability, genre ranking, director ranking)  
- **Modular ETL structure** following best practices  

---

# 🧩 Project Structure

etl-pipeline-movies/
│
├── data/
│ ├── raw/ # Raw Kaggle downloads
│ ├── processed/ # Cleaned data + KPI outputs
│
├── src/
│ ├── download.py # Kaggle file downloader
│ ├── extract.py # Chunk-based CSV loader
│ ├── transform.py # Cleaning + JSON parsing + feature engineering
│ ├── load.py # Save processed datasets
│
├── main.py # Pipeline orchestrator
├── requirements.txt
└── README.md

yaml
Copiar código

---

# 🛠️ Technologies Used

- Python 3.10+  
- Pandas  
- JSON parsing  
- Chunk processing  
- OS / Pathlib  

---

# 📦 Dataset: TMDB Movie Metadata

The dataset contains over 10,000 movies and multiple semi-structured fields.

### Key Columns:

| Column | Description |
|--------|-------------|
| `id` | Movie ID |
| `title` | Movie title |
| `release_date` | Release date |
| `genres` | List of genres (JSON string) |
| `keywords` | Movie tags (JSON string) |
| `original_language` | Language code |
| `budget` | Movie budget |
| `revenue` | Movie revenue |
| `vote_average` | TMDB rating |
| `vote_count` | Number of votes |
| `credits` | Cast and crew (JSON string) |

---

# 🧠 Skills Demonstrated

### ✔ JSON Parsing & Normalization
- `genres` → expanded into multiple rows or extracted main genre  
- `keywords` → flattened  
- `credits` → director extracted from crew list  
 

### ✔ KPI Computation
Two main ranking outputs:

| File | Description |
|------|-------------|
| `genre_ranking_tmdb_movie_kpis.csv` | Avg profitability by genre |
| `director_ranking_tmdb_movie_kpis.csv` | Top directors by vote average |

---

# 🛠️ Setup Instructions

## 1️⃣ Create the virtual environment

```bash
python -m venv venv
```
source venv/bin/activate
2️⃣ Install requirements
bash

pip install -r requirements.txt
3️⃣ Configure Kaggle authentication

Go to your Kaggle profile → Account

Click Create API Token

Save the generated kaggle.json here:

C:\\Users\\<your-user>\\.kaggle\\kaggle.json
▶️ Running the pipeline
Once everything is ready:

bash
python main.py
The pipeline will:

Download the dataset into data/raw/

Process data chunk by chunk

Parse JSON-like fields

Compute KPIs

Save outputs into data/processed/

📄 Output Files
cleaned_movies.csv — cleaned and enriched dataset

genre_ranking_tmdb_movie_kpis.csv — genre profitability ranking

director_ranking_tmdb_movie_kpis.csv — top directors based on ratings