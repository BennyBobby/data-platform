from minio import Minio
import os

client = Minio(
    "localhost:9000", access_key="minioadmin", secret_key="minioadmin", secure=False
)

BUCKET = "bronze"
FILE_PATH = os.path.join(os.path.dirname(__file__), "child-mortality.csv")
DEST = "health/child-mortality/raw/child-mortality.csv"

if not client.bucket_exists(BUCKET):
    client.make_bucket(BUCKET)
    print(f"Bucket '{BUCKET}' created")
else:
    print(f"Bucket '{BUCKET}' already exists")

print(f"Uploading...")
client.fput_object(
    BUCKET,
    DEST,
    FILE_PATH,
)
print(f"File uploaded: {BUCKET}/{DEST}")
