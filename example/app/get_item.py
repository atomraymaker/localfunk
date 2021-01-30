import json
import os

import boto3

from nested import util

SESSION = boto3.session.Session()
TABLE = os.environ.get("TABLE")


def do(event, context):
    print(event)
    key = event["pathParameters"].get("key")
    table = SESSION.resource("dynamodb").Table(TABLE)
    print(os.environ.get("AWS_DEFAULT_REGION"))
    response = table.get_item(Key={"Key": key})

    print(context.aws_request_id)

    return {
        "statusCode": 200,
        "body": json.dumps({"item": response.get("Item"), "util": util.run()}),
    }
