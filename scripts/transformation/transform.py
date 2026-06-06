import os
import pandas as pd
from minio import Minio
from sqlalchemy import create_engine, text

client = Minio(
    os.environ.get("MINIO_ENDPOINT", "localhost:9000"),
    access_key=os.environ["MINIO_ROOT_USER"],
    secret_key=os.environ["MINIO_ROOT_PASSWORD"],
    secure=False,
)

# 1. Read CSV from MinIO (bronze)
response = client.get_object("bronze", "health/child-mortality/raw/child-mortality.csv")
df = pd.read_csv(response)

# 2. Clean
df.columns = ["entity", "code", "year", "mortality_rate"]
df["year"] = df["year"].astype(int)
df = df.dropna(subset=["mortality_rate"])

print(f"Rows after cleaning: {len(df)}")
print(df.dtypes)
print(df.head(3))

# 3. Write to PostgreSQL staging
host = os.environ.get("POSTGRES_HOST", "localhost")
user = os.environ["POSTGRES_USER"]
password = os.environ["POSTGRES_PASSWORD"]
db = os.environ["POSTGRES_DB"]

engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:5432/{db}")

with engine.begin() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS staging"))

df.to_sql("child_mortality", engine, schema="staging", if_exists="replace", index=False)
print("Data loaded into PostgreSQL staging.child_mortality")
