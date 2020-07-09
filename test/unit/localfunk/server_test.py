import json

from localfunk import server


def test_run_code():
    var_value = "test_run_code"
    payload = {
        "env": {"env_var": var_value, "_HANDLER": "function_code.run"},
        "event": {"var_name": "env_var"},
        "context": {},
        "code_uri": "test/fixtures",
    }

    assert json.loads(server.local_function(payload)) == {"var_value": var_value}
