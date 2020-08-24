import json
import os

import boto3

from nested import util

SESSION = boto3.session.Session()
TABLE = os.environ.get("TABLE")


def do(event, _context):
    key = event["pathParameters"].get("key")
    table = SESSION.resource("dynamodb").Table(TABLE)
    response = table.get_item(Key={"Key": key})

    return {
        "statusCode": 200,
        "body": json.dumps({"item": response.get("Item"), "util": util.run()}),
    }
