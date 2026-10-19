# AGL v0.4 — Documentation & Onboarding Kit

**Start with `ONBOARDING.html`.** It has two tabs:
1. **Architecture and theory mapping:** Explains what AGL v0.4 promises and maps its operators to exact JSON/Python files.
2. **Windows onboarding lab:** Provides tested PowerShell commands, a prediction-first explanatory test runner, valid/invalid event traces and troubleshooting.

The companion `AGL_v0.4.html` is the **Full Technical Specification**. The Python scripts and original JSON files are unchanged from the AGL v0.4 reference package; the `docs/` Markdown sources and `labs/` fixtures are companion onboarding material.

## Windows quick start (PowerShell)

After extracting the kit ZIP, change directory to the resulting `agl_v0_4_starter` folder, then:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install jsonschema
.\.venv\Scripts\python.exe validate_agl.py abstract_valid_spec.json
.\.venv\Scripts\python.exe lab2_explained.py --guided
.\.venv\Scripts\python.exe -m unittest -v test_validator.py
.\.venv\Scripts\python.exe validate_agl.py abstract_valid_spec.json --trace labs\trace_pass.json
.\.venv\Scripts\python.exe validate_agl.py abstract_valid_spec.json --trace labs\trace_fail_replay.json
.\.venv\Scripts\python.exe validate_agl.py labs\spec_fail_scope.json
```

The first validation, test suite, and passing trace should succeed; the two negative fixtures should fail **intentionally**, with process exit code 1.

**AGL is proposed language, not an Anthropic feature. This ZIP is a checker, not a Claude orchestration runtime.** Passing the checker does not prove independent evidence, actual authorization, atomic state or execution safety.

**Lab 2 learning update:** Run `python lab2_explained.py --case 10` for a detailed diagnostic, or `python lab2_explained.py --guided` to predict outcomes before each test. The theory remains AGL v0.4; this update changes documentation and strengthens two test assertions, not the reference validator semantics.