import json
import os
from test.util.server import ServerThread

import flask

from localfunk import sam

app = flask.Flask("test_gen_code")


def test_build():
    path = ".localfunk.yaml"

    if os.path.exists(path):
        os.remove(path)

    sam.build("127.0.0.1:5000", "test/fixtures/template.yml", path)

    assert os.path.exists(path)

    if os.path.exists(path):
        os.remove(path)


def test_gen_code():
    server = ServerThread(app)
    server.start()

    path = "generated_code.py"
    if os.path.exists(path):
        os.remove(path)

    code = sam.gen_code(func("test_code"), "127.0.0.1:5000")
    file = open(path, "w+")
    file.write(code)
    file.close()

    import generated_code  # pylint: disable=import-error, import-outside-toplevel

    response = generated_code.handler({"event": "test"}, Context())

    server.shutdown()

    assert response == {
        "event": {"event": "test"},
        "env": dict(os.environ.items()),
        "name": "Function",
        "code_uri": "app",
        "file": "test_code",
        "function": "test_code",
        "context": {},
    }

    if os.path.exists(path):
        os.remove(path)


def test_gen_code_failure():
    server = ServerThread(app)
    server.start()

    path = "generated_code_fail.py"
    if os.path.exists(path):
        os.remove(path)

    code = sam.gen_code(func("test_code"), "127.0.0.1:5002")  # incorrect port
    file = open(path, "w+")
    file.write(code)
    file.close()

    import generated_code_fail  # pylint: disable=import-error, import-outside-toplevel

    response = generated_code_fail.handler({"event": "test"}, Context())

    server.shutdown()

    assert response == {"error": "[Errno 61] Connection refused"}

    if os.path.exists(path):
        os.remove(path)


def test_get_functions():
    template_yaml = sam.parse(template_path="test/fixtures/template.yml")
    assert sam.get_functions(template_yaml=template_yaml) == {
        "FunctionOne": {
            "name": "FunctionOne",
            "code_uri": "app1",
            "file": "handler1",
            "function": "handle",
        },
        "FunctionTwo": {
            "name": "FunctionTwo",
            "code_uri": "__INLINE",
            "file": "index",
            "function": "handler",
        },
    }


def func(name):
    return {
        "name": "Function",
        "code_uri": "app",
        "file": name,
        "function": name,
    }


class Context:
    pass


@app.route("/", methods=["POST"])
def hello():
    return json.dumps(flask.request.json)
