# Hands-on Onboarding: Install, Validate, Break, Repair

**Learning objective:** By the end of this lab, you will be able to inspect a valid AGL contract, run the static validator, reproduce a passing and failing trace audit, explain the failure reports, and safely modify a contract without accidentally crossing its governance boundaries.

This is a **reference-specification lab**. None of the commands launches Claude, schedules a loop, connects to GitHub, spends money, or changes production software.

## Before you start

**Requirements:** Windows 10/11, PowerShell, Python 3.10 or newer, and an internet connection for the first `jsonschema` installation. No Microsoft Office or Claude subscription is required for these exercises. An editor such as VS Code helps with reading JSON but is optional.

The downloadable **Onboarding Kit** contains the full v0.4 specification, the original reference validator and schema, an improved 11-test regression suite, the learning-oriented `lab2_explained.py` runner, this manual, and three lab fixtures. This is a **documentation/lab improvement within AGL v0.4**; it does not change the formal specification or the validator rules.

### Quick start: PowerShell without activation-policy issues

Run the following commands from PowerShell. The `py -3` launcher is standard on many Windows Python installations; replace it with `python` if your system lacks `py`.

```powershell
$zip = "$env:USERPROFILE\Downloads\AGL_v0.4_Onboarding_Kit.zip"
$dest = "$env:USERPROFILE\Downloads\AGL-v0.4-lab"
Expand-Archive -LiteralPath $zip -DestinationPath $dest -Force
Set-Location "$dest\agl_v0_4_starter"

py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install jsonschema
.\.venv\Scripts\python.exe validate_agl.py abstract_valid_spec.json
.\.venv\Scripts\python.exe -m unittest -v test_validator.py
```

Because these commands call the virtual environment's interpreter explicitly, you **do not need to activate** the environment or change the PowerShell execution policy.

You should see a PASS from the validator and an eleven-test summary ending in `OK`. The actual installation output from pip may vary.

**Safety:** The command `Expand-Archive -Force` writes into the specified lab folder. Use a fresh directory if you want to preserve a previous experiment.

## The starter directory

```text
agl_v0_4_starter/
├── AGL_v0.4.html                 ← full conceptual specification
├── ONBOARDING.html               ← this two-tab guide
├── README.md                     ← original reference README
├── symbols.json                  ← 41 unique formal definitions
├── schema.json                   ← Draft 2020-12 contract shape
├── abstract_valid_spec.json      ← original valid P4 contract
├── validate_agl.py               ← validator + historical trace auditor
├── test_validator.py             ← 11 regression tests (2 assertions strengthened)
├── lab2_explained.py             ← interactive explanatory Lab 2 runner
└── labs/
    ├── trace_pass.json           ← expected valid event history
    ├── trace_fail_replay.json    ← deliberate duplicate effect
    └── spec_fail_scope.json      ← deliberate scope escalation
```

The validator, schema, symbol registry, and valid contract are the original v0.4 reference artifacts. The test file has two more specific assertions, and the explanatory runner, manual, and lab fixtures are educational additions. No live orchestration capability has been added.

## Lab 1 — The valid contract

**Command:**

```powershell
.\.venv\Scripts\python.exe validate_agl.py abstract_valid_spec.json
```

**Expected output:**

```text
PASS: reference schema and semantic checks.
LIMIT: PASS does not prove execution safety, evaluator soundness, or evidence authenticity.
```

**Interpretation:** The declared data satisfies the JSON Schema and the subset of cross-field consistency rules implemented in `validate_static()`. It does not mean that the ambition is worthwhile, permissions are real, a goal was executed, or safety was proven.

### Follow the key references manually

Open `abstract_valid_spec.json` and confirm:

- `pattern` is `P4`, so all of `ambition`, `contract`, `goal`, and `loop` are required.
- `contract.id` is `contract-alpha`; both `goal.contract_ref` and `loop.contract_ref` refer to that ID.
- `goal.evaluator_ref` matches `verifier.id`.
- `goal.executor_id` is different from `verifier.runner_id`.
- The allowed actions flow downward: governance → contract → goal/loop.
- Reserved money maxima reconcile: `10` (Goal) + `20` (Loop cumulative) = `30` (Governance overall cap).

The validator checks these particular equalities and inclusions; it doesn't validate the economic reasonableness of those numbers.

## Lab 2 — Learn from the tests, not merely from `OK`

The ordinary unit-test runner is useful for maintaining code, but **`Ran 11 tests ... OK` explains almost nothing about AGL**. This lab now has a second, teaching-oriented runner that demonstrates the actual rule tested by each mutation.

### 2A. Run the educational tour

```powershell
.\.venv\Scripts\python.exe lab2_explained.py
```

Every case reports **specification section → rule → deliberate change → expected result → actual diagnostic → learning**. A deliberately invalid configuration must be rejected, so the pattern `EXPECT: FAIL / ACTUAL: FAIL / TEST: PASS` is a successful test.

**A representative output (Case 5):**

```text
CASE 05 / 11 | No authority escalation | SPEC sections 3, 6.2, 8
RULE:   Loop actions must be a subset of approved contract actions.
CHANGE: Add delete-production to loop.response.authorized_actions.
EXPECT: FAIL (must mention authorization)
ACTUAL: FAIL
DIAGNOSTIC: LOOP: response exceeds contract authorization
TEST:   PASS - expected behavior confirmed
LEARN:  The checker rejects declared Loop scope escalation.
```

Read this as a miniature experimental method: state a proposition, make a controlled intervention, predict the consequence, observe the validator, and bound the conclusion. **It does not show that a real Claude process would be unable to call a forbidden tool.**

### 2B. Choose one experiment and inspect its limits

```powershell
.\.venv\Scripts\python.exe lab2_explained.py --list
.\.venv\Scripts\python.exe lab2_explained.py --case 10
```

`--case 10` includes this crucial limitation:

```text
LIMIT: This does not prevent an API from performing the same effect twice.
```

This distinction is foundational: *static and historical evidence checking* is not the same as *runtime enforcement*.

### 2C. Predict before observing (interactive mode)

```powershell
.\.venv\Scripts\python.exe lab2_explained.py --guided
```

For each case, the runner states the rule and the mutation, then asks:

```text
PREDICT checker verdict [PASS/FAIL]:
```

Enter `PASS` or `FAIL` (or press Enter to skip). It then shows the actual result, diagnostic, interpretation, and limitation. **Prediction → observation → explanation** is the primary learning mode.

### The 11 experiments and their exact theoretical connections

| # | Controlled experiment | Expected checker verdict | Full Specification |
|---|---|---|---|
| 1 | Keep the reference contract unchanged | PASS | §§3, 7, 8 — contract and static checking |
| 2 | Delete `ambition.R.verbify` | FAIL | §4.4 — noun-to-verb transformation |
| 3 | Delete `ambition.D.discovery.surprise_detector` | FAIL | §§4.3, 10 — discovery and epistemic progress |
| 4 | Make evaluator and executor identities equal | FAIL | §§5.1, 9 — separate verifier and executor |
| 5 | Add unauthorized `delete-production` to Loop actions | FAIL | §§3, 6.2 — authority preservation |
| 6 | Reduce overall money cap below declared reservations | FAIL | §§3, 6.2 — budget consistency |
| 7 | Remove declaration of the `dedupe` guard | FAIL | §§6.2, 8 — required guard declarations |
| 8 | Set a fixed interval below the checker minimum | FAIL | §§6.3, 8 — timing policy |
| 9 | Supply observation, action, and increasing checkpoint | PASS | §6.1 — operational sequence |
| 10 | Repeat an `effect_id` in a recorded trace | FAIL | §6.2 — idempotency evidence |
| 11 | Make checkpoint version decrease from 3 to 2 | FAIL | §§6.1–6.2 — continuity evidence |

### 2D. Keep the conventional unit tests too

```powershell
.\.venv\Scripts\python.exe -m unittest -v test_validator.py
```

These remain the automated regression suite. Two assertions have been strengthened: tests 2 and 3 now demand diagnostics referring to the **specific missing field** instead of accepting any error whatsoever. The expected summary is still `Ran 11 tests ... OK`, but you should now understand the proposition behind each result.

**What this lab does not prove:** that the claimed scientific discovery methods are substantive, that declared permissions are enforced at tool-call time, that log evidence is authentic/exhaustive, or that observed checkpoints correspond to atomic durable storage. Those are separate research and runtime obligations for later versions.

## Lab 3 — Audit a legitimate recorded event sequence

```powershell
.\.venv\Scripts\python.exe validate_agl.py abstract_valid_spec.json --trace labs\trace_pass.json
```

**Expected:**

```text
PASS: reference schema and semantic checks plus supplied-trace audit.
LIMIT: PASS does not prove execution safety, evaluator soundness, or evidence authenticity.
```

The event sequence is a JSON **array**:

```json
[
  {"kind": "observation", "event_id": "event-1"},
  {"kind": "action", "event_id": "event-1", "effect_id": "effect-1",
   "name": "propose", "authorization_checked": true,
   "lease_id": "lease-1", "contract_id": "contract-alpha",
   "run_id": "run-1", "money_cost": 0.2},
  {"kind": "checkpoint", "version": 1}
]
```

The auditor sees an observed event, an authorized-by-declaration action referencing that event, and a monotonically advancing checkpoint. It does not prove that the external action took place or that a real lease existed.

**Subtle format distinction:** This implementation expects a JSON array file for `--trace`. A newline-delimited JSONL file mentioned in the abstract contract is **not** accepted by the CLI without conversion.

## Lab 4 — Reproduce replay detection

```powershell
.\.venv\Scripts\python.exe validate_agl.py abstract_valid_spec.json --trace labs\trace_fail_replay.json
$LASTEXITCODE
```

**Expected:**

```text
FAIL: TRACE[2]: repeated effect_id effect-1
1
```

This fixture repeats the same consequential effect identity. The checker reports it and exits with code `1`. The `1` is **expected** in a negative test; it means the invalid trace was rejected correctly.

**What this proves:** A duplicate `effect_id` *present in this trace* can be detected.

**What it does not prove:** Duplicate real-world effects cannot happen, or that omitted/forged log records are detected. The external service and transaction ledger would need to enforce stronger guarantees.

## Lab 5 — Reproduce a contract-authority violation

```powershell
.\.venv\Scripts\python.exe validate_agl.py labs\spec_fail_scope.json
$LASTEXITCODE
```

**Expected:**

```text
FAIL: LOOP: response exceeds contract authorization
1
```

The deliberately invalid specimen adds `delete-production` to `loop.response.authorized_actions` while `contract.authorized_actions` still permits only `read` and `propose`.

The validator correctly rejects the escalation. This is a **static scope check**, not a runtime access-control system: an actual agent's tool permissions must still be enforced by the host.

## Lab 6 — Repair the invalid contract and test your own change

Work on a **copy** of the original JSON specimen, not the baseline fixture.

```powershell
Copy-Item abstract_valid_spec.json labs\my_first_spec.json
code labs\my_first_spec.json
```

If `code` is unavailable, open the file in another editor. Modify the `ambition.H.ultimate_goal` string so that it clearly states an outcome rather than an isolated action. You can also change `ambition.R.verbify.output` to a more precise observable function; do **not** remove its fields or change `discipline_discovery.input_ref`.

Then validate:

```powershell
.\.venv\Scripts\python.exe validate_agl.py labs\my_first_spec.json
```

The result should still PASS if you changed only those required, nonempty descriptive strings. This teaches a vital limitation: **semantic quality is not validated**. The reference checker ensures a `VERBIFY` result exists and is wired to discipline discovery; it cannot judge whether you have formulated a genuinely better functional objective.

### Controlled failure: remove a required discovery component

In your copy, delete the `ambition.D.discovery.surprise_detector` key. Rerun the validator. You should see a schema failure identifying a missing required property. Restore the key and validate again.

This is the most direct demonstration of the distinction between *expressing a theoretical requirement in a schema* and *actually implementing a scientific discovery algorithm*.

## How to create P1, P2 or P3 from the P4 specimen

The current `abstract_valid_spec.json` is a complete P4 starting point. If you need another pattern, create a copy and adjust `pattern` together with the operators—not just the pattern label.

| Target | Necessary entries | Sensible edits |
|---|---|---|
| P1 | `ambition`, `contract`, `goal`, `verifier`, `governance` | Remove `loop`; adjust the governance cap to cover the goal budget |
| P2 | `ambition`, `contract`, `loop`, `verifier`, `governance` | Remove `goal`; approve a bounded discovery **charter** rather than autonomous implementation |
| P3 | `contract`, `goal`, `loop`, `verifier`, `governance` | Remove `ambition`; assume the goal and scope were already selected |
| P4 | All of the above | Preserve all operators but keep strategic review separate from iteration-level execution |

These are conceptual minimal sets enforced by the schema's conditional presence rules. The schema **may still admit extra operators** and does not execute the transitions implied by the `pattern` label.

## How to safely extend the reference implementation

A recommended contributor workflow is:

1. Modify `schema.json` if you're changing syntax or required fields.
2. Modify `validate_agl.py` if you're introducing cross-field constraints or stronger trace checks.
3. Add at least one accepting test and one rejecting test to `test_validator.py`.
4. Update `symbols.json` if you introduce formal notation; do not assign an existing symbol a second meaning.
5. Update the corresponding section of `AGL_v0.4.html` and the documentation crosswalk.
6. Rerun the validator and all eleven original tests, plus any new tests.

**Extension priorities:** Check `goal.objective` against the contract's intended result; add schema-level rule consistency for unusual pattern combinations; specify machine-readable budgets and measurements; validate evidence schemas; introduce a *separate runtime* that enforces side-effect authorization before tool calls. Each step should have explicit tests and a stated trust boundary.

## Troubleshooting

| Symptom | Likely cause | Resolution |
|---|---|---|
| `'py' is not recognized` | Python launcher missing | Use `python -m venv .venv` or install Python 3.10+ |
| `ModuleNotFoundError: jsonschema` | Dependency not installed into the interpreter in use | Run `.\.venv\Scripts\python.exe -m pip install jsonschema` from the lab root |
| `FileNotFoundError: schema.json` | Reference script moved away from adjacent schema | Keep `validate_agl.py` and `schema.json` together; script resolves its own directory |
| `error: unrecognized arguments: ...` | Incorrect CLI order or switch | Use `python validate_agl.py SPEC [--trace TRACE_JSON_ARRAY]` |
| `JSONDecodeError: Extra data` | JSONL supplied instead of one array | Convert trace records into a valid JSON array |
| `FAIL: GOAL: contract reference does not resolve` | Inconsistent contract IDs | Make `goal.contract_ref` equal `contract.id` |
| `FAIL: INDEPENDENCE: ...` | Executor and verifier runner IDs equal | Give them distinct IDs **and separately enforce actual independence** |
| `FAIL: BUDGET: ...` | Reserved Goal + Loop amounts exceed declared governance cap | Adjust limits coherently; don't simply inflate the budget without review |
| `FAIL: ENFORCEMENT: ...` | Required runtime guard **declaration** absent | Declare the four guard names; implementing their actual behavior is a separate task |
| Negative lab exits with status `1` | Intentionally invalid fixture | Correct outcome: rejection was demonstrated |
| PowerShell blocks `Activate.ps1` | Activation-policy restriction | Use `.\.venv\Scripts\python.exe` directly; no activation required |

## Checklist: ready to progress beyond v0.4

- [ ] The valid P4 specimen passes structural and semantic checks.
- [ ] All eleven regression tests pass.
- [ ] A valid recorded trace passes the auditor.
- [ ] A replayed `effect_id` and an unauthorized action are each rejected.
- [ ] You can explain why a declared guard is not an enforced guard.
- [ ] You can identify which Full Specification section defines each contract field.
- [ ] You can distinguish native Claude `/goal` or `/loop` behavior from this reference package's capabilities.
- [ ] You can define a concrete v0.5 runtime obligation without claiming v0.4 already implements it.

## What's next: the smallest useful v0.5 prototype

Do not start by wiring three slash commands together. First build an **admission controller** that checks a real proposed action against a trusted policy, allocates a bounded resource reservation, and persists an effect identity before allowing the action to reach an external tool. Then test crash/retry paths and independent evidence capture.

The central research question is whether *well-formed specification + trustworthy runtime guards + credible external verification* is sufficient to support a narrow, conditional safety guarantee. v0.4 documents those conditions; it does not yet satisfy them.