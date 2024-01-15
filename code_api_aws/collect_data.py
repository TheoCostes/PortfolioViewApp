import pandas as pd
import boto3
from io import StringIO
from utils_api import update_prices
import os
import secrets

os.chdir("..")

s3_bucket = "dashboard-invest"
s3_key = "portefeuille.csv"

AWS_ACCESS_KEY_ID = secrets.get_secret("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = secrets.get_secret("AWS_SECRET_ACCESS_KEY")

print(AWS_ACCESS_KEY_ID)
print(AWS_SECRET_ACCESS_KEY)
# AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)
print(s3_bucket, s3_key)
try:
    response = s3.get_object(Bucket=s3_bucket, Key=s3_key)
    print(response)
    existing_data = pd.read_csv(response['Body'])
except Exception as e:
    # If the file doesn't exist, you might want to handle this case based on your requirements
    print("ERROR :", e)
    existing_data = pd.DataFrame()

api_data_result = update_prices(existing_data)
# Append new data to existing data
updated_data = pd.concat([existing_data, api_data_result], ignore_index=True)

# Convert the updated DataFrame to CSV string
csv_buffer = StringIO()
updated_data.to_csv(csv_buffer, index=False)
print("to S3")
# Upload the updated CSV to S3
s3.put_object(Body=csv_buffer.getvalue(), Bucket=s3_bucket, Key=s3_key)

print("done")

