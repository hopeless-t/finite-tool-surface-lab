# FAILURE-001 — BENCH-002 Workload MC Import Failure

## Event

Workflow:

`BENCH-002 Workload Mix Monte Carlo`

Run:

`36233938910`

Failed step:

`Run workload-mixture Monte Carlo`

## Symptom

```text
ModuleNotFoundError: No module named 'finite_tool_surface_lab'
```

## Atomic cause

The workflow checked out the repository and installed NumPy, but did not install the repository package itself before invoking:

`python -m finite_tool_surface_lab.bench002_workload_mc`

## Classification

```text
FAILURE_CLASS = WORKFLOW_PACKAGING
CALCULATION_STARTED = NO
RESEARCH_RESULT_CORRUPTED = NO
ARTIFACT_INPUT_DOWNLOAD = PASS
NUMPY_INSTALL = PASS
```

## Repair

Insert:

`python -m pip install -e .`

after Python setup and before NumPy/analysis execution.

## Lesson

```text
Source Checked Out
!= Python Package Importable
```

Research-compute workflows that call package modules must explicitly install the package or set an equally explicit import path.

No change to BENCH-002 scientific design is required.
