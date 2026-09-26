# FAILURE-002 — VAL-002 Artifact Path Mismatch

## Event

Workflow:

`VAL-002 pmndrs math catalogue`

Run:

`36237164578`

## State

```text
Node 20 extract = PASS
Node 22 extract = PASS
catalog generation = PASS
artifact upload = PASS
compare = FAIL
scientific comparison executed = NO
```

## Symptom

```text
diff: replay/val002-pmndrs-math-node-20/catalog.json:
No such file or directory
```

## Cause

The uploaded artifact preserved the `out/` subdirectory.

Actual path:

```text
replay/val002-pmndrs-math-node-20/out/catalog.json
```

The compare step incorrectly expected the file at artifact root.

## Classification

```text
FAILURE_CLASS = WORKFLOW_ARTIFACT_PATH
CORPUS_GENERATION = SUCCESS
COMPARISON = NOT EXECUTED
RESEARCH_RESULT = NONE
```

## Repair

Correct compare/readback paths only.

No change to adapter semantics, pinned package, seed, or acceptance criteria.
