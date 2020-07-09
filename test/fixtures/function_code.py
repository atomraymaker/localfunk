import os


def run(event, _context):
    return {"var_value": os.environ[event["var_name"]]}
