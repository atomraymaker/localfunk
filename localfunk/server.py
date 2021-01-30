import json
import os
import subprocess
from pathlib import Path

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
    payload = request.json
    print(payload["function"])
    command = [
        "sam",
        "local",
        "invoke",
        "-e",
        "-",
        payload["name"],
    ]
    env = {k: v for (k, v) in payload["env"].items() if k not in IGNORE_VARS}

    run = subprocess.run(
        command,
        input=json.dumps(payload["event"]).encode(),
        env={**os.environ, **env},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    print(run.stderr)
    print(run.stdout)
    print(run.returncode)

    return run.stdout.decode('utf-8')
