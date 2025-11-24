import json
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Inventory")


def decimal_to_native(value):
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
        path_params = event.get("pathParameters") or {}
        item_id = path_params.get("id")

        if not item_id:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({"error": "Missing item id in path"}),
            }

        query_result = table.query(
            KeyConditionExpression=Key("item_id").eq(item_id)
        )
        items = query_result.get("Items", [])

        if not items:
            return {
                "statusCode": 404,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({"error": "Item not found"}),
            }

        item = items[0]
        location_id = item["location_id"]

        table.delete_item(
            Key={
                "item_id": item_id,
                "location_id": location_id,
            }
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(
                {"message": "Item deleted successfully", "item": decimal_to_native(item)}
            ),
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
