import boto3
import json

BUCKET = "datacanvas-ai-mudasser-2026"
KEY = "outputs/latest.json"

s3 = boto3.client("s3")


def lambda_handler(event, context):

    try:
        response = s3.get_object(
            Bucket=BUCKET,
            Key=KEY
        )

        data = json.loads(
            response["Body"].read().decode("utf-8")
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "GET,OPTIONS"
            },
            "body": json.dumps(data)
        }

    except Exception as e:

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": str(e)
            })
        }