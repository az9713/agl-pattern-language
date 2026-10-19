# Understanding the AGL v0.4 Reference Implementation

**Purpose.** This guide explains what the downloadable reference package implements, how its files correspond to the AGL v0.4 *Full Technical Specification*, what its validator actually checks, and where theory still outruns code. The implementation is a **preflight and retrospective audit prototype**, not a Claude Code plugin, runtime orchestrator, or proof of agent safety.

> **Source boundaries.** “Specification” means the companion `AGL_v0.4.html`. “Implementation” means the original six-file reference package examined for this guide. AGL is our proposed language, not an official Anthropic product. The architecture diagrams and interpretations in this guide are explanatory material, not screenshots or figures from Felix or Anthropic.

## Start with the mental model

A coding agent normally receives a request and attempts to execute it. AGL instead separates four kinds of decisions that are often conflated:

1. **What is worth attempting?** Ambition `A` proposes stronger objectives, methods and investigatory directions.
2. **What is now authorized?** Governance `Γ` and the approved contract `κ` freeze the scope and resources.
3. **How is bounded work completed?** Goal `G` attempts authorized actions; verifier `V` assesses evidence.
4. **What should happen later?** Loop `L` observes changes and can take authorized responses, while strategic review `J` decides whether to reconsider objectives.

**Conceptual lifecycle**

```text
Original problem ── A ──> Proposed ambitions
                              │
                    governed selection (Γ)
                              ▼
                     Approved contract (κ)
                              │
                         G: execute
                              │
                         V: evaluate
                              │
                         L: observe
                              │
                       J: reconsider
                    (if evidence warrants)
```

The Python package **does not execute this lifecycle**. It checks whether an abstract JSON description is structurally admissible, performs a few semantic cross-checks, and optionally inspects a *supplied* trace.

## Seven-minute file orientation

| File | Role | Read it when… |
|---|---|---|
| `AGL_v0.4.html` | **Normative conceptual report**: operator definitions, type system, constraints, conditional safety argument | You want to understand *why* a contract field exists; use sections 2–11 |
| `README.md` | Original project overview and basic commands | You want the terse upstream package instructions |
| `symbols.json` | Registry of **41 unique symbols**, kinds, and meanings | You see `Γ`, `κ`, `ρ_NV`, `P_κ` or another formal symbol and want its precise definition |
| `schema.json` | Draft 2020-12 JSON Schema; validates fields, types, enumerations and per-pattern presence | You need to know which JSON keys are permitted or required |
| `abstract_valid_spec.json` | Valid, deliberately **domain-neutral P4** specimen | You need a starting specification to modify safely |
| `validate_agl.py` | Structural + semantic validator; optional historical event-trace auditor | You want to see exactly which constraints the code checks |
| `test_validator.py` | Eleven positive/negative regression tests for the checker | You want executable proof that the checker catches a set of known bad inputs |

The starter kit adds `labs/trace_pass.json`, `labs/trace_fail_replay.json`, and `labs/spec_fail_scope.json`. These **are documentation exercise files**, not components of the original reference ZIP.

## Mapping the theory to the code

The specification is broader than the validator. Read this as a *traceability matrix*—a conceptual property does not become implemented merely because a JSON field names it.

| Full specification | JSON location | What is checked today? | Not yet implemented |
|---|---|---|---|
| §2: single symbol namespace | `symbols.json` | Registry supplies 41 definitions | No automatic type-checking of every mathematical expression |
| §3: typed, governed composition | `pattern`, `contract`, `governance` | Required operators by pattern; frozen/approved flags; approver match | Actual approval authenticity or a workflow executor |
| §4.1: Speed `S` | `ambition.S.cost_S`, `quality_floor`, `same_outcome_constraint` | Required fields; nonempty constraints | Computing optimal plans or checking real outcome equivalence |
| §4.2: Altitude `H` | `ambition.H` | Required fields and types | Automatically discovering or ranking higher-level objectives |
| §4.3: Depth `D` | `ambition.D.discovery` | Presence of surprise, hypothesis, experiment, evidence and revision declarations | Real discovery, hypothesis validation, novelty search |
| §4.4: Range `R` | `ambition.R.verbify`, `discipline_discovery.input_ref` | Functional output nonempty; discipline search points to verbification output | Actual semantic noun-to-verb transformation or transfer-quality assessment |
| §5: Goal `G` | `goal`, `contract` | Contract reference, permitted-method subset, budgets, evaluator reference | Goal execution and actual completion proof |
| §5: independent verification | `goal.evaluator_ref`, `verifier` | Reference equality; evaluator/executor IDs differ; valid verdict labels | Proving evaluator independence, running tests or verifying provenance |
| §6: Loop `L` | `loop` | Timing consistency; `NO_OP` on no-change; scope and caps; declared guards | Scheduler, event subscriber, durable ledger, runtime guard implementation |
| §6: replay and continuity | `loop.safety`, optional `--trace` | Detects repeated recorded effect IDs, nonmonotonic recorded checkpoints | Exactly-once side effects, authentic event recording, atomic commits |
| §7: P1–P4 compositions | `pattern` + conditional schema rules | Conditional presence constraints | Runtime orchestration; strict prohibition of unused extra operators |
| §9: conditional soundness | `loop.enforcement` and stated assumptions | Guard **names** must be declared | Proving trusted guards work and capture all effects |
| §10: epistemic progress | `ambition.D.discovery` | Shape of a proposed discovery process | Empirical generalization or genuine scientific novelty |

### Pattern requirements actually encoded

The schema's `allOf` conditions require these components:

| Pattern | Required operators/objects | Meaning |
|---|---|---|
| `P1` | `ambition`, `goal`, `contract`, `verifier`, `governance` | Ambition → committed goal → verification |
| `P2` | `ambition`, `loop`, `contract`, `verifier`, `governance` | Opportunity discovery, governed by a discovery charter |
| `P3` | `goal`, `loop`, `contract`, `verifier`, `governance` | Bounded delivery followed by monitored feedback |
| `P4` | `ambition`, `goal`, `loop`, `contract`, `verifier`, `governance` | Full governed improvement cycle |

`agl_version` and `pattern` are always required. The checker **does not forbid additional operator objects** outside the minimal requirements. It is not yet a full typed compiler.

## Read the contract in dependency order

Do not start by editing `loop.safety` or the ambition prose in isolation. First understand the references:

```text
                       governance.permission_scope
                                   │
               ┌───────────────────┘
               ▼
        contract.authorized_actions
             │                │
             ▼                ▼
goal.execution_policy...  loop.response.authorized_actions

contract.id ───────────> goal.contract_ref
       └───────────────> loop.contract_ref
       └───────────────> loop.safety.scope.approved_contract_ref

verifier.id ───────────> goal.evaluator_ref
```

The validator checks those references and set-inclusion relationships. This is why changing one field often requires reconciling related fields. A contract is a deliberately *frozen target* while a given goal runs; proposal generation and contract selection are separate.

### Interpreting the P4 specimen

The provided specimen is a deliberately bland P4 configuration. It sets a contract ID of `contract-alpha`, authorizes `read` and `propose`, gives `G` a money cap of `10`, reserves a Loop cumulative cap of `20`, and sets a governance total cap of `30`.

Those values are **synthetic test data**, not recommended prices, permissions, or defaults for a real project. A schema-valid specimen is not automatically a desirable or production-safe contract.

## What the validator really does

### Layer 1 — Structural/schema checks

`jsonschema.Draft202012Validator` checks required keys, types, allowed values, object structures, and pattern-dependent operator presence. This includes requiring all four ambition dimensions when `ambition` exists.

### Layer 2 — Cross-field static semantics

`validate_static()` verifies the contract is marked approved/frozen, the approver string agrees with governance, action scopes are subsets of authorized scopes, goal/loop/verifier references match, evaluator ID differs from executor ID, and declared resource ceilings fit within the declared governance cap.

A few distinctive rules in the current code:

- Fixed loop intervals must be **at least 60 seconds**; adaptive/event modes must omit `interval_seconds`.
- Loop's `no_change` policy must be `NO_OP`.
- Four guard **names** must be present: `authorization`, `lease`, `budget`, `dedupe`.
- Goal `max_money` plus Loop cumulative `money_limit` may not exceed the governance `max_money_total` value.
- The verifier must advertise the distinct verdict labels `PASS`, `FAIL`, and `INCONCLUSIVE`.

**These checks validate declarations and relationships.** They neither run the actual guards nor authenticate approvers. The current checker also does not assert, for example, that the free-text `goal.objective` equals `contract.objective`.

### Layer 3 — Optional recorded-trace audit

`validate_trace()` accepts a **JSON array** of historical records with kinds `observation`, `action`, and `checkpoint`. It checks the observed action names, contract ID, `authorization_checked` flag, nonempty lease reference, prior observed event, effect identity, recorded spending and checkpoint order.

Crucially, `authorization_checked: true` is a claim **in the log**. The tool cannot establish that authorization happened in reality. A `lease_id` string is not proof of an actual distributed lock. Likewise, a `PASS` proves only that the supplied data passed the checker.

**Format trap:** The abstract `loop.output.evidence_log` names `evidence/log.jsonl`, but the implemented CLI uses `json.loads()` on the entire `--trace` file. For the current checker, supply **one JSON array**, not newline-delimited JSONL.

### Layer 4 — Real runtime enforcement (not included)

A working AGL orchestrator would need actual pre-action permission checks, provider-aware idempotency, durable transactional state, concurrency control, resource accounting, reproducible tests and trustable evidence provenance.

### Layer 5 — Scientific validity (not included)

Neither schema validation nor trace auditing verifies empirical truth, causal claims or novelty. The Depth discovery fields define an *intended method*, not the fact of a scientific discovery.

## Why the tests matter—and what they cannot prove

The eleven tests exercise both acceptance and rejection paths: valid specimen, missing noun-to-verb field, missing discovery mechanism, evaluator identity collision, scope escalation, insufficient budget, missing guard declaration, short fixed interval, valid trace, duplicate effect ID, and descending checkpoint version.

A green test suite means **those specific checks worked for those test fixtures**. It does not establish exhaustive schema soundness, correct behavior of all untested inputs, or end-to-end safety.

## Reading order relative to the Full Technical Specification

For an efficient first pass, read **Full Spec §0–3 → this guide → Full Spec §4–7 → the hands-on tab → Full Spec §8–11**. The reference code makes more sense after understanding why ambition proposals, approved contracts, evidence, evaluation, and loop state are separate objects.

## Current maturity assessment

| Capability | Status |
|---|---|
| Formal vocabulary and operator contracts | **Specified** |
| JSON structure + selected static refinements | **Implemented** |
| Selected historical event-trace consistency checks | **Implemented** |
| Actual `/be-ambitious`, `/goal`, `/loop` orchestration | **Not implemented** |
| Enforced authorization, atomicity, replay protection | **Not implemented** |
| Trusted independent validation of real artifacts | **Not implemented** |
| End-to-end soundness or scientific-discovery proof | **Not established** |

This boundary is deliberate. v0.4's genuine deliverable is an inspectable contract and checker—a foundation on which a future runtime could be built, rather than a runtime dressed up as a specification.