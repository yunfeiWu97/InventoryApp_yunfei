import json
from decimal import Decimal

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Inventory")


def decimal_to_native(value):
    """Convert DynamoDB Decimals to int/float so json.dumps works."""
    if isinstance(value, list):
        return [decimal_to_native(v) for v in value]
    if isinstance(value, dict):
        return {k: decimal_to_native(v) for k, v in value.items()}
    if isinstance(value, Decimal):
        if value % 1 == 0:
            return int(value)
        return float(value)
    return value


def lambda_handler(event, context):
    try:
        response = table.scan()
        items = response.get("Items", [])

        items = decimal_to_native(items)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(items),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"error": str(e)}),
        }
