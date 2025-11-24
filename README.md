🎬 ETL Pipeline – Flight Data Processing (Python + Pandas)

This project implements a modular ETL pipeline to process flight performance data using Python, Pandas, and chunk-based processing.
The goal is to demonstrate key data-engineering skills such as handling large files, cleaning and transforming raw data, enriching datasets, and computing KPIs.

🚀 Main Features

Chunk-based loading for efficient memory usage

Data cleaning (null handling, type fixes, filtering)

Dataset enrichment using auxiliary lookup tables

KPI computation (delays, flight counts, airport performance)

Modular ETL architecture (extract / transform / load)

Clear repository structure suitable for real-world pipelines

🧩 Project Structure
etl-pipeline-flights/
│
├── data/
│   ├── raw/               # Raw datasets (input)
│   ├── processed/         # Cleaned outputs and KPIs
│
├── src/
│   ├── extract.py         # Chunk reader for large CSVs
│   ├── transform.py       # Cleaning + enrichment + KPIs
│   ├── load.py            # Save final outputs
│
├── main.py                # Pipeline orchestrator
├── requirements.txt
└── README.md

🛠️ Technologies Used

Python 3.10+

Pandas

OS / Pathlib

Chunking techniques for large datasets

📦 Input Data

The project uses public flight datasets containing:

Column	Description
FL_DATE	Flight date
AIRLINE	Carrier code
ORIGIN_AIRPORT	Departure airport
DESTINATION_AIRPORT	Arrival airport
DEPARTURE_DELAY	Delay in minutes
ARRIVAL_DELAY	Delay in minutes
CANCELLED	Cancellation flag

You may add more lookup tables such as airlines or airports for enrichment.

▶️ How to Run the Pipeline
1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate     # Windows
source venv/bin/activate  # macOS/Linux

2. Install dependencies
pip install -r requirements.txt

3. Run the pipeline
python main.py

📝 Output Files

The pipeline generates:

cleaned_flights.csv — Clean and enriched flight dataset

airport_kpis.csv — Airport performance (mean delays, number of flights)

airline_kpis.csv — Airline performance metrics

💡 Skills Demonstrated

✔ Handling large datasets with chunking
✔ Data cleaning and preprocessing
✔ KPI design & computation
✔ Modular code design
✔ Data enrichment (merging with lookup tables)
✔ Reproducible project structure