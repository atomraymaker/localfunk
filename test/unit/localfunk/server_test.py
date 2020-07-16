import json

from localfunk import server


def test_run_code():
    var_value = "test_run_code"
    payload = {
        "env": {"env_var": var_value},
        "event": {"var_name": "env_var"},
        "context": {},
        "name": "Function",
        "code_uri": "test/fixtures",
        "file": "function_code",
        "function": "run",
    }

    assert json.loads(server.local_function(payload)) == {"var_value": var_value}
