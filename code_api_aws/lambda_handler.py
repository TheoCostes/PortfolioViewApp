import pandas as pd
import boto3
from io import StringIO
from utils import update_prices


def lambda_handler(event, context):
    """
    Append data to an existing CSV file in an S3 bucket.

    Parameters:
    - api_data_result: DataFrame, the data retrieved from the api_data function.
    - s3_bucket: str, the name of the S3 bucket.
    - s3_key: str, the key (path) to the CSV file within the bucket.

    Returns:
    - None
    """

    s3_bucket = event['s3_bucket']
    s3_key = event['s3_key']
    # Load existing CSV file from S3
    s3 = boto3.client('s3')
    print(s3_bucket, s3_key)
    try:
        response = s3.get_object(Bucket=s3_bucket, Key=s3_key)
        existing_data = pd.read_csv(response['Body'])
    except Exception as e:
        # If the file doesn't exist, you might want to handle this case based on your requirements
        existing_data = pd.DataFrame()

    api_data_result = update_prices(existing_data)
    # Append new data to existing data
    updated_data = pd.concat([existing_data, api_data_result], ignore_index=True)

    # Convert the updated DataFrame to CSV string
    csv_buffer = StringIO()
    updated_data.to_csv(csv_buffer, index=False)

    # Upload the updated CSV to S3
    s3.put_object(Body=csv_buffer.getvalue(), Bucket=s3_bucket, Key=s3_key)

    print(f"Data appended to {s3_key} in {s3_bucket}.")

    return {"statusCode": 200, "body": "Success"}

