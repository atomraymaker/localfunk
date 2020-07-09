import os
import shutil

from cfn_tools import dump_yaml, load_yaml


def build(url, template_path="template.yml"):
    if os.path.exists(".aws-sam"):
        shutil.rmtree(".aws-sam")
    os.makedirs(".aws-sam")
    os.makedirs(".aws-sam/build")

    template_yaml = parse(template_path)

    for func in get_functions(template_yaml):
        build_function(func, url)

    update_template(template_yaml)
    save_template(template_yaml)


def update_template(template_yaml):
    for name, details in template_yaml["Resources"].items():
        if details["Type"] == "AWS::Serverless::Function":
            template_yaml["Resources"][name]["Properties"]["CodeUri"] = name


def save_template(template_yaml):
    file = open(".aws-sam/build/template.yaml", "w+")
    file.write(dump_yaml(template_yaml))
    file.close()


def build_function(func, proxy):
    path = f".aws-sam/build/{func['name']}"

    # function directory
    os.makedirs(path)

    # requirements.txt
    open(f"{path}/requirements.txt", "w+")

    # function file
    file = open(f"{path}/{func['file']}.py", "w+")
    code = gen_code(func, proxy)
    file.write(code)
    file.close()


def gen_code(func, proxy):
    return f"""
import http.client
import json
import os

conn = http.client.HTTPConnection("{proxy}")
headers = {{"Content-type": "application/json"}}


def {func['function']}(event, context):
    data = {{
        "event": event, 
        "env": dict(os.environ.items()),
        "code_uri": "{func['code_uri']}"
    }}

    try:
        conn.request("POST", "/", json.dumps(data), headers)
        response = conn.getresponse()
        return json.loads(response.read().decode())
    except Exception as e:
        return json.dumps({{
            "error": str(e)
        }})
    """


def get_functions(template_yaml):
    functions = []
    for name, details in template_yaml["Resources"].items():
        if details["Type"] == "AWS::Serverless::Function":
            props = details["Properties"]
            handler = props["Handler"].split(".")
            functions.append(
                {
                    "name": name,
                    "code_uri": props["CodeUri"],
                    "file": handler[0],
                    "function": handler[1],
                }
            )

    return functions


def parse(template_path):
    text = open(template_path, "r").read()
    return load_yaml(text)
