import json
import os

import boto3

SESSION = boto3.session.Session()
TABLE = os.environ.get("TABLE")


def do(event, _context):
    key = event["pathParameters"].get("key")
    attrs = json.loads(event["body"])
    table = SESSION.resource("dynamodb").Table(TABLE)
    item = {"Key": key, **attrs}
    table.put_item(Item=item, ReturnValues="NONE")

    return {"statusCode": 200, "body": json.dumps({"item": item})}
