import json
import os
import shutil
from test.util.server import ServerThread

import flask

from localfunk import sam

app = flask.Flask("test_gen_code")


def test_build():
    if os.path.exists(".aws-sam"):
        shutil.rmtree(".aws-sam")

    sam.build("127.0.0.1:5000", template_path="test/fixtures/template.yml")

    assert os.path.exists(".aws-sam")
    assert os.path.exists(".aws-sam/build/FunctionOne")
    assert os.path.exists(".aws-sam/build/FunctionTwo")
    assert os.path.exists(".aws-sam/build/FunctionOne/requirements.txt")
    assert os.path.exists(".aws-sam/build/FunctionTwo/requirements.txt")
    assert os.path.exists(".aws-sam/build/FunctionOne/handler1.py")
    assert os.path.exists(".aws-sam/build/FunctionTwo/handler2.py")

    if os.path.exists(".aws-sam"):
        shutil.rmtree(".aws-sam")


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

    response = generated_code.test_code({"event": "test"}, {"context": "test"})

    server.shutdown()

    assert json.loads(response) == {
        "event": {"event": "test"},
        "context": {"context": "test"},
        "env": dict(os.environ.items()),
        "code_uri": "app",
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

    response = generated_code_fail.test_code({"event": "test"}, {"context": "test"})

    server.shutdown()

    assert json.loads(response) == {"error": "[Errno 61] Connection refused"}

    if os.path.exists(path):
        os.remove(path)


def test_get_functions():
    assert sam.get_functions(template_path="test/fixtures/template.yml") == [
        {
            "name": "FunctionOne",
            "code_uri": "app1",
            "file": "handler1",
            "function": "handle",
        },
        {
            "name": "FunctionTwo",
            "code_uri": "app2",
            "file": "handler2",
            "function": "do",
        },
    ]


def func(name):
    return {
        "name": name,
        "code_uri": "app",
        "file": name,
        "function": name,
    }


@app.route("/", methods=["POST"])
def hello():
    return json.dumps(flask.request.json)
