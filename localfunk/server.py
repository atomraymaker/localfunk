import importlib
import json
import os
import sys

from flask import Flask, request

IGNORE_VARS = ["PATH", "LD_LIBRARY_PATH"]

app = Flask(__name__)


def start(port):
    app.run(port=port)


@app.route("/", methods=["POST"])
def local_function_api():
    return local_function(request.json)


def local_function(payload):
    set_up(payload)
    response = run_code(payload)
    tear_down(payload)
    return json.dumps(response)


def run_code(payload):
    module_name, function_name = payload["env"]["_HANDLER"].split(".")
    module = importlib.import_module(module_name)
    importlib.reload(module)
    function = getattr(module, function_name)
    return function(payload["event"], None)


def set_up(payload):
    set_env(payload.get("env"))
    sys.path.append(payload["code_uri"])


def tear_down(payload):
    unset_env(payload["env"])
    sys.path.remove(payload["code_uri"])


def set_env(env):
    for key, value in env.items():
        if key not in IGNORE_VARS:
            os.environ[key] = value


def unset_env(env):
    for key in env.keys():
        if key not in IGNORE_VARS:
            os.environ.pop(key)
