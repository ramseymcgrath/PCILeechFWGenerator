import subprocess
import sys


def test_cli_fallback_returns_success():
    # Run a short inline Python process that imports the module and checks
    # fallback behaviour via get_device_config returning None
    cmd = [
        sys.executable,
        "-c",
        (
            "import src.device_clone.device_config as dc, json;"
            "m=dc.get_device_config('this_profile_should_not_exist');"
            "print(json.dumps({'result': m is None}))"
        ),
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0

    # Some modules log warnings to stdout which can prefix the JSON output.
    # Find the first JSON object in stdout and validate its contents.
    out = proc.stdout.strip()
    import json

    idx = out.find("{")
    assert idx != -1, f"no JSON object found in output: {out!r}"
    payload = json.loads(out[idx:])
    assert payload == {"result": True}
