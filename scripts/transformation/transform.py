import os
import pandas as pd
from io import BytesIO
from minio import Minio

client = Minio(
    os.environ.get("MINIO_ENDPOINT", "localhost:9000"),
    access_key=os.environ["MINIO_ROOT_USER"],
    secret_key=os.environ["MINIO_ROOT_PASSWORD"],
    secure=False,
)

response = client.get_object("bronze", "health/child-mortality/raw/child-mortality.csv")
df = pd.read_csv(response)

df.columns = ["entity", "code", "year", "mortality_rate"]
df["year"] = df["year"].astype(int)
df = df.dropna(subset=["mortality_rate"])

print(len(df))
print(df.dtypes)
print(df.head(3))

if not client.bucket_exists("silver"):
    client.make_bucket("silver")

buffer = BytesIO()
df.to_parquet(buffer, index=False)
buffer.seek(0)

client.put_object(
    "silver",
    "health/child-mortality/child-mortality.parquet",
    buffer,
    length=buffer.getbuffer().nbytes,
    content_type="application/octet-stream",
)

print("Parquet file uploaded in silver bucket")
