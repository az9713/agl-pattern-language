# AGL v0.4 — Ambition · Goal · Loop

**A typed pattern language for outcome-oriented Claude workflows**, with a formal specification, reference JSON Schema and Python validator, a readable onboarding manual, and reproducible labs.

> **Status:** Research / reference implementation (v0.4). **Not** an Anthropic product, an official Claude Code extension, or an autonomous execution engine. The reference checker validates declarations and audits supplied event traces; it does not enforce permissions on live agents or independently prove real-world correctness.

## Read the documentation online

**[Open the live documentation home](https://az9713.github.io/agl-pattern-language/)** · **[Full technical specification](https://az9713.github.io/agl-pattern-language/AGL_v0.4.html)** · **[Interactive onboarding manual](https://az9713.github.io/agl-pattern-language/ONBOARDING.html)**

GitHub's README renderer does not permit embedding a live interactive website in the document itself. The screenshots below are genuine previews of the published HTML, and each image is a link to the live page.

[![AGL v0.4 technical specification preview](docs/assets/spec-preview.webp)](https://az9713.github.io/agl-pattern-language/AGL_v0.4.html)

[![AGL v0.4 onboarding manual preview](docs/assets/onboarding-preview.webp)](https://az9713.github.io/agl-pattern-language/ONBOARDING.html)

## Why AGL?

The motivating observation is that productivity with Claude is constrained not just by execution speed but by what users choose to delegate, how deeply tasks are investigated, which disciplines are consulted, and how outcomes are verified. AGL treats **Ambition** (`A`), **Goal** (`G`), and **Loop** (`L`) as separate, composable operators, surrounded by verification (`V`) and governance (`Γ`).

| Operator | Responsibility | Related Claude capability |
| --- | --- | --- |
| `A` — Ambition | Generate improved objectives and expert-grade methods using **Speed, Altitude, Depth, Range** | External [`/be-ambitious` skill](https://github.com/az9713/be-ambitious-skill) |
| `G` — Goal | Execute a frozen, bounded, verifiable contract | `/goal` |
| `L` — Loop | Revisit new evidence on a schedule, without replaying effects | `/loop` |
| `V` — Verification | Evaluate witnesses against explicit acceptance rules | Executable checks and external evidence |
| `Γ` — Governance | Enforce permissions, approvals, and resource ceilings | Must be supplied by the surrounding runtime |

The patterns are *abstract designs*, not literal slash-command nesting syntax:

- **P1 — Ambitious Sprint:** `A → Select → G → V`
- **P2 — Opportunity Radar:** `A → L[new evidence ⇒ A]`
- **P3 — Completion Watchdog:** `G → V → L[new issue ⇒ authorized response]`
- **P4 — Evolutionary Factory:** `(A → Select → G → V → L → J)*`, where `J` is strategic review

## Companion `/be-ambitious` skill

The `/be-ambitious` Claude Code skill is **not bundled in this repository**. AGL v0.4 specifies the Ambition operator (`A`) and its four dimensions, but its reference implementation validates abstract contracts rather than installing the skill. To use the actual skill, consult the separate repository: **[az9713/be-ambitious-skill](https://github.com/az9713/be-ambitious-skill)**. Follow that repository's own installation and usage instructions. AGL's `A` contract and the external skill are related conceptually; they should not be assumed to have identical schemas or implementation behavior.

## Contents

| File | What it does |
| --- | --- |
| [`index.html`](index.html) | GitHub Pages entrypoint linking both documents |
| [`AGL_v0.4.html`](AGL_v0.4.html) | Formal specification, symbol registry, typing and safety semantics |
| [`ONBOARDING.html`](ONBOARDING.html) | Two-tab architecture and Windows onboarding guide |
| [`START_HERE.md`](START_HERE.md) | Short onboarding checklist |
| [`docs/01_Concepts.md`](docs/01_Concepts.md) | Implementation-to-specification mapping |
| [`docs/02_Onboarding.md`](docs/02_Onboarding.md) | Text version of the exercises |
| [`schema.json`](schema.json) | JSON Schema for the reference contract |
| [`symbols.json`](symbols.json) | Canonical symbol definitions |
| [`abstract_valid_spec.json`](abstract_valid_spec.json) | Example of a valid abstract P4 contract |
| [`validate_agl.py`](validate_agl.py) | Structural validator and retrospective event-trace auditor |
| [`test_validator.py`](test_validator.py) | Eleven positive/negative regression tests |
| [`lab2_explained.py`](lab2_explained.py) | Guided, explanation-rich walkthrough of all 11 tests |
| [`labs/`](labs/) | Passing and deliberately invalid contract/trace fixtures |

## Windows quick start

Python 3.10+ is recommended. In PowerShell, from the repository root:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe validate_agl.py abstract_valid_spec.json
.\.venv\Scripts\python.exe lab2_explained.py --guided
.\.venv\Scripts\python.exe -m unittest -v test_validator.py
```

Then audit a passing trace:

```powershell
.\.venv\Scripts\python.exe validate_agl.py abstract_valid_spec.json --trace labs\trace_pass.json
```

The two negative specimens should be **rejected intentionally**:

```powershell
.\.venv\Scripts\python.exe validate_agl.py abstract_valid_spec.json --trace labs\trace_fail_replay.json
.\.venv\Scripts\python.exe validate_agl.py labs\spec_fail_scope.json
```

Use `lab2_explained.py --list`, `--case 10`, or `--guided` to see the *reason* for each expected PASS/FAIL rather than only a test-suite summary.

## Validation boundaries

**What this release checks:** contract structure, selected cross-field semantics, evaluator/executor identity separation, bounded budget declarations, unauthorized actions declared in the spec, and selected faults in a supplied trace (e.g. duplicate effect IDs).

**What it does not do:** run Claude autonomously; provision durable schedulers; ensure externally enforced idempotency; provide transactional state, complete logs, or independent scientific verification. A green test suite is **not a proof of agent safety or productivity gains**.

## Original sources and commentary

1. **Felix Rieseberg** — [*How to Be More Ambitious: A Tutorial for Humans with Models*](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/) — origin of Speed, Altitude, Depth, and Range.
2. **Jay** — [Video commentary on Felix’s article](https://www.youtube.com/watch?v=NarezKh3w4o) — accessible business applications, multi-agent costs, and the importance of purpose and pacing.
3. **Ray** — [Video commentary on Felix’s article](https://www.youtube.com/watch?v=RbfQayMNtJc) — operational framing: outcome-owning agents, tooling prerequisites, reducing human handoffs, and improving the software factory itself.
4. **Anthropic** — [Claude Code `/goal` documentation](https://code.claude.com/docs/en/goal) and [scheduled tasks / `/loop` documentation](https://code.claude.com/docs/en/scheduled-tasks) — actual command capabilities and limitations.

**Attribution boundary:** AGL’s notation, schemas, validator and safety contracts are a separate research synthesis; they are not claims made or endorsed by the article author, video hosts, or Anthropic. The video hosts' observations are reported commentary, not independently verified empirical benchmarks.

## GitHub Pages

This repository includes a GitHub Actions deployment workflow (`.github/workflows/pages.yml`). After pushing, open **Settings → Pages → Build and deployment → Source: GitHub Actions** (if not already configured). The workflow then publishes `index.html` and both interactive HTML documents from the default branch. The deployment status—not the existence of a README link—is authoritative evidence that Pages is live.

No ZIP archives, local paths, account credentials, or personal notes are required in the public repository.