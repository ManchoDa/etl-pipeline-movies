# 🎬 ETL Pipeline: TMDB 5000 Movie Analysis

This project implements a fully modular **ETL (Extract, Transform, Load) pipeline** using Python and Pandas.  
The goal is to process the **TMDB 5000 Movie Metadata dataset**, demonstrating key data-engineering skills such as:

- Handling large CSV files efficiently  
- Cleaning and transforming semi-structured JSON data  
- Computing business-oriented KPIs (profitability, director rankings, genre performance)  
- Designing a clean, maintainable ETL architecture  

---

# 🚀 Features

- **Automated Kaggle download** (via API token)  
- **Chunked CSV processing** for memory efficiency  
- **JSON parsing** from string-encoded fields  
- **Feature Engineering**: profitability, director extraction, genre normalization  
- **KPI generation** stored as CSV outputs  
- **Clean modular code structure** inspired by industry ETL patterns  

---

# 🛠️ Quick Setup Guide

## 1️⃣ Create and Activate Virtual Environment

```bash
python -m venv venv
```
.\venv\Scripts\activate

## 2️⃣ Install Dependencies

pip install -r requirements.txt

3️⃣ Configure Kaggle Authentication

The pipeline downloads the dataset automatically using the Kaggle API.

Go to your Kaggle profile → Account → API → Create New Token

Download kaggle.json

Place it in:
C:\Users\<your-user>\.kaggle\kaggle.json

▶️ Execution
Once the environment is active and your Kaggle token is configured:
(venv) python main.py

## Output

The script will automatically:

Download TMDB files into data/raw/

Process the movie metadata in chunks

Parse nested JSON fields (e.g., genres, crew)

Compute profitability metrics and enriched movie features

Generate final KPI outputs in data/processed/

## Project Structure
etl-pipeline-tmdb/
│
├── data/
│   ├── raw/               # Raw Kaggle downloads
│   ├── processed/         # Final KPIs and cleaned data
│
├── src/
│   ├── download.py        # Kaggle download logic
│   ├── extract.py         # Chunk-based reading
│   ├── transform.py       # JSON cleaning + feature engineering
│   ├── load.py            # CSV writing functions
│
├── main.py                # Pipeline orchestrator
├── requirements.txt
└── README.md

## KPI Outputs
1️⃣ Genre Profitability Ranking

Average profitability by genre

Sorted in descending order

2️⃣ Director Score Ranking

Average rating for each director

Filtered to avoid directors with very few movies

Top 10 output
