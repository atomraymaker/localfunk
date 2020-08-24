import os

from cfn_tools import dump_yaml, load_yaml


def cleanup(template):
    if os.path.exists(template):
        os.remove(template)


def build(url, template_path, save_path):
    template_yaml = parse(template_path)
    functions = get_functions(template_yaml)
    update_template(template_yaml, functions, url)
    save_template(template_yaml, save_path)


def update_template(template_yaml, functions, url):
    for name, details in template_yaml["Resources"].items():
        if details["Type"] == "AWS::Serverless::Function":
            props = template_yaml["Resources"][name]["Properties"]
            if "CodeUri" in props:
                del props["CodeUri"]
            props["Handler"] = "index.handler"
            props["InlineCode"] = gen_code(functions[name], url)


def save_template(template_yaml, save_path):
    file = open(save_path, "w+")
    file.write(dump_yaml(template_yaml))
    file.close()


def gen_code(func, proxy):
    return f"""
import http.client
import json
import os

conn = http.client.HTTPConnection("{proxy}")
headers = {{"Content-type": "application/json"}}


def handler(event, context):
    data = {{
        "event": event, 
        "env": dict(os.environ.items()),
        "name": "{func['name']}",
        "code_uri": "{func['code_uri']}",
        "file": "{func['file']}",
        "function": "{func['function']}" 
    }}

    try:
        conn.request("POST", "/", json.dumps(data), headers)
        response = conn.getresponse()
        return json.loads(response.read().decode())
    except Exception as e:
        return {{ "error": str(e) }}
    """


def get_functions(template_yaml):
    functions = {}
    for name, details in template_yaml["Resources"].items():
        if details["Type"] == "AWS::Serverless::Function":
            props = details["Properties"]
            file, function = props["Handler"].rsplit(".", 1)

            if "CodeUri" in props:
                code_uri = props["CodeUri"]
            else:
                code_uri = "__INLINE"

            functions[name] = {
                "name": name,
                "code_uri": code_uri,
                "file": file,
                "function": function,
            }

    return functions


def parse(template_path):
    text = open(template_path, "r").read()
    return load_yaml(text)
