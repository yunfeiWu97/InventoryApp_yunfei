import json
import time
import uuid
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


def generate_ulid_like() -> str:
    millis = int(time.time() * 1000)
    random_part = uuid.uuid4().hex[:16]
    return f"{millis:x}{random_part}"


def lambda_handler(event, context):
    try:
        if "body" not in event or event["body"] is None:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({"error": "Request body is required"}),
            }

        body = event["body"]
        if isinstance(body, str):
            body = json.loads(body)

        item_name = body.get("item_name")
        item_description = body.get("item_description")
        item_qty_on_hand = body.get("item_qty_on_hand")
        item_price = body.get("item_price")
        location_id = body.get("location_id")

        missing = [
            key
            for key, value in [
                ("item_name", item_name),
                ("item_description", item_description),
                ("item_qty_on_hand", item_qty_on_hand),
                ("item_price", item_price),
                ("location_id", location_id),
            ]
            if value is None
        ]
        if missing:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps(
                    {"error": f"Missing required fields: {', '.join(missing)}"}
                ),
            }

        item_id = generate_ulid_like()

        new_item = {
            "item_id": item_id,
            "location_id": int(location_id),
            "item_name": item_name,
            "item_description": item_description,
            "item_qty_on_hand": int(item_qty_on_hand),
            "item_price": Decimal(str(item_price)),
        }

        table.put_item(Item=new_item)

        response_item = decimal_to_native(new_item)

        return {
            "statusCode": 201,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                },
            "body": json.dumps(response_item),
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
