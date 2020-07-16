import importlib
import json
import os
import sys
from types import ModuleType

from cfn_tools import load_yaml
from flask import Flask, request

IGNORE_VARS = ["PATH", "LD_LIBRARY_PATH"]

app = Flask(__name__)
TEMPLATE_PATH = None


def start(port, template):
    global TEMPLATE_PATH  # pylint: disable=global-statement
    TEMPLATE_PATH = template
    app.run(port=port)


@app.route("/", methods=["POST"])
def local_function_api():
    return local_function(request.json)


def local_function(payload):
    set_up(payload)
    response = invoke(payload)
    tear_down(payload)
    return json.dumps(response)


def invoke(payload):
    if payload["code_uri"] == "__INLINE":
        function = load_inline(payload)
    else:
        function = load_code(payload)

    return function(payload["event"], None)


def load_code(payload):
    module = importlib.import_module(payload["file"])
    importlib.reload(module)
    return getattr(module, payload["function"])


def load_inline(payload):
    global TEMPLATE_PATH  # pylint: disable=global-statement
    template = load_yaml(open(TEMPLATE_PATH, "r").read())
    code = template["Resources"][payload["name"]]["Properties"]["InlineCode"]
    module = ModuleType("localfunk_index")
    exec(code, module.__dict__)  # pylint: disable=exec-used
    return getattr(module, payload["function"])


def set_up(payload):
    set_env(payload.get("env"))
    if payload["code_uri"] != "__INLINE":
        sys.path.append(payload["code_uri"])


def tear_down(payload):
    unset_env(payload["env"])
    if payload["code_uri"] != "__INLINE":
        sys.path.remove(payload["code_uri"])


def set_env(env):
    for key, value in env.items():
        if key not in IGNORE_VARS:
            os.environ[key] = value


def unset_env(env):
    for key in env.keys():
        if key not in IGNORE_VARS:
            os.environ.pop(key)
