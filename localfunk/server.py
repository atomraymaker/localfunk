import importlib
import json
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

from cfn_tools import load_yaml
from flask import Flask, request

IGNORE_VARS = ["PATH", "LD_LIBRARY_PATH", "LOCALFUNK_TEMPLATE"]

app = Flask(__name__)


def start(port, template):
    subprocess.run(
        ["flask", "run"],
        check=True,
        env={
            **os.environ,
            **{
                "LOCALFUNK_TEMPLATE": template,
                "FLASK_APP": Path(os.path.realpath(__file__)).with_suffix(""),
                "FLASK_ENV": "development",
                "FLASK_RUN_PORT": str(port),
            },
        },
    )


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
    return getattr(module, payload["function"])


def load_inline(payload):
    template_path = os.environ["LOCALFUNK_TEMPLATE"]  # pylint: disable=global-statement
    template = load_yaml(open(template_path, "r").read())
    code = template["Resources"][payload["name"]]["Properties"]["InlineCode"]
    module = ModuleType("localfunk_index")
    exec(code, module.__dict__)  # pylint: disable=exec-used
    return getattr(module, payload["function"])


def set_up(payload):
    clear_env()
    set_env(payload.get("env"))
    if payload["code_uri"] != "__INLINE":
        sys.path.append(payload["code_uri"])


# TODO: test if this is still needed now that flask does the reloading
def tear_down(payload):
    unset_env(payload["env"])
    if payload["code_uri"] != "__INLINE":
        sys.path.remove(payload["code_uri"])


def clear_env():
    for key in os.environ.keys():  # pylint: disable=consider-iterating-dictionary
        if key not in IGNORE_VARS:
            os.environ.pop(key)


def set_env(env):
    for key, value in env.items():
        if key not in IGNORE_VARS:
            os.environ[key] = value


def unset_env(env):
    for key in env.keys():
        if key not in IGNORE_VARS:
            os.environ.pop(key)
