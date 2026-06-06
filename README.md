# Data Platform - Child Mortality Analysis

A local data platform built with a medallion architecture (Bronze / Silver / Gold), orchestrated with Airflow and visualized with Metabase.

## Stack

| Layer | Tool |
|---|---|
| Data Lake (raw) | MinIO |
| Ingestion | Python + Minio SDK |
| Transformation | Pandas + SQLAlchemy |
| Data Warehouse | PostgreSQL |
| Modeling | dbt |
| Orchestration | Apache Airflow |
| Visualization | Metabase |
| Infrastructure | Docker Compose |

## Architecture

```
CSV (Our World in Data)
    ↓ ingest_bronze       [scripts/ingestion/ingest_child_mortality.py]
MinIO bronze/health/child-mortality/raw/   (raw CSV)
    ↓ transform_silver    [scripts/transformation/transform.py]
PostgreSQL staging.child_mortality         (cleaned data)
    ↓ dbt_gold            [dbt/child_mortality/models/gold/]
PostgreSQL gold.mortality_by_country       (avg mortality by country)
PostgreSQL gold.evolution_by_decade        (global trend by decade)
PostgreSQL gold.top_countries_improvement  (top 10 most improved countries)
    ↓
Metabase dashboard
```

The full pipeline is orchestrated by the Airflow DAG `child_mortality_pipeline` ([dags/child_mortality_pipeline.py](dags/child_mortality_pipeline.py)), which runs four stages in sequence: `ingest_bronze >> transform_silver >> dbt_gold >> dbt_test`.

## Dataset

[Child Mortality — Our World in Data](https://ourworldindata.org/child-mortality)

- 16,835 rows
- Columns: `entity`, `code`, `year`, `mortality_rate`
- Metric: Under-five mortality rate (deaths per 1,000 live births)

## Getting Started

### Prerequisites

- Docker Desktop
- Python 3.11+
- [uv](https://github.com/astral-sh/uv)

### Setup

1. Clone the repo and create your `.env` from the example:

```bash
cp .env.example .env
# Fill in your credentials
```

2. Start all services:

```bash
docker compose up --build -d
```

3. Access the services:

| Service | URL |
|---|---|
| MinIO | http://localhost:9001 |
| Airflow | http://localhost:8080 |
| Metabase | http://localhost:3000 |

4. Trigger the pipeline in Airflow (`child_mortality_pipeline`) or run scripts locally:

```bash
set -a && source .env && set +a
uv run scripts/ingestion/ingest_child_mortality.py
uv run scripts/transformation/transform.py
cd dbt/child_mortality && dbt run --profiles-dir ../
```

> `set -a` exports all variables from `.env` to child processes without needing the `export` keyword in the file.

## Project Structure

```
data-platform/
├── Dockerfile                              # Custom Airflow image (Python 3.11 + deps)
├── docker-compose.yml                      # MinIO, PostgreSQL, Airflow, Metabase
├── requirements.txt                        # Python deps for Airflow container
├── pyproject.toml                          # Python deps for local development (uv)
├── .env.example                            # Credentials template
│
├── dags/
│   └── child_mortality_pipeline.py         # Airflow DAG: bronze >> silver >> gold
│
├── scripts/
│   ├── ingestion/
│   │   ├── ingest_child_mortality.py       # Upload raw CSV to MinIO (bronze)
│   │   └── child-mortality.csv             # Source dataset (Our World in Data)
│   └── transformation/
│       └── transform.py                    # Clean data, load to PostgreSQL (staging)
│
└── dbt/
    ├── profiles.yml                        # dbt PostgreSQL connection
    └── child_mortality/
        ├── dbt_project.yml                 # dbt project config
        └── models/
            ├── staging/
            │   └── sources.yml             # Source definition + data quality tests
            └── gold/
                ├── schema.yml              # dbt tests (not_null, unique)
                ├── mortality_by_country.sql
                ├── evolution_by_decade.sql
                └── top_countries_improvement.sql
```
