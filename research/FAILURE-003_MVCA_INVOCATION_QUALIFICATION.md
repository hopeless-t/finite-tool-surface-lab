# FAILURE-003 — MVCA Launcher / Provider Invocation Qualification Failure

> **Status:** CROSS-REPOSITORY OPERATIONAL CASE INTAKE
> **Origin:** `hopeless-t/mvca` QP-05 R1 / DIAG-01 / OBS-02
> **Public canonical evidence:** NO
> **Purpose:** Preserve a falsifiable failure pattern that can motivate public Tool Surface experiments without importing MVCA execution authority or private operational claims.

## Event

MVCA QP-05 R1 attempted one bounded runner-host inventory observation through the logical action:

`ldc.runner_host_inventory_v1`

The action contract, one-shot admission, transport, delivery, and typed evidence projection all completed, but the Multipass domain observation remained UNKNOWN.

The operational incident was investigated in:

- `hopeless-t/mvca#130`
- `hopeless-t/mvca#158` — Multipass Launcher / Snap Runtime Surface Encirclement
- `hopeless-t/mvca#166` — Qualified Host Observer Provider v2 proposal

These private/project-specific observations are **case-study input**, not public canonical evidence for this repository.

## Symptom

The inventory helper pinned and invoked:

```text
/snap/multipass/current/bin/multipass
```

That internal binary failed on the host with a root-certificate path error.

The supported launcher forms:

```text
multipass ...
/usr/bin/snap run multipass ...
```

succeeded on the same host and VM.

Replacing only the final binary with the supported Snap launcher **inside the existing bubblewrap capsule** still failed because the capsule did not provide the Snap runtime/confinement surface expected by the supported launcher.

## Atomic causes

### Cause A — path identity was mistaken for invocation identity

The harness treated a pinned executable path as if it completely specified the qualified invocation.

The operational evidence falsified that assumption.

```text
Executable Path Pinned
!=
Supported Invocation Qualified
```

For launcher-mediated software, execution semantics may depend on:

- launcher identity;
- runtime/confinement setup;
- environment construction;
- namespace preparation;
- service/runtime integration;
- provider/adapter behavior;
- output/parser contract.

### Cause B — filesystem exposure was mistaken for capability exposure

The investigation considered Snap runtime surfaces that include Unix sockets and system integration state.

A filesystem read-only bind of a Unix socket does **not** make the service capability read-only. Connecting to the socket still delegates IPC.

```text
Read-only Filesystem Surface
!=
Read-only Capability Surface
```

### Cause C — observer failure could have been mistaken for target failure

An external `strace` attempt changed Snap confinement behavior and invalidated the intended successful-host trace.

The observation was retained as an observer-effect artifact rather than evidence that the underlying target failed.

```text
Observer Failure
!=
Target Failure
```

## Public specification corroboration

Canonical Snap documentation independently supports the general mechanism:

- Snap system architecture describes `snap-confine`, namespaces, and the `/run/snapd.socket` control path:
  https://snapcraft.io/docs/reference/system-architecture/
- Snap startup tracing documents launcher/runtime setup around snapped applications:
  https://snapcraft.io/docs/explanation/how-snaps-work/debuging-startup-performance/
- Snap environment documentation shows snapped execution receives a constructed runtime environment:
  https://snapcraft.io/docs/reference/development/environment-variables/
- Snap debugging guidance warns that ordinary external tracing of confined applications can produce misleading results:
  https://snapcraft.io/docs/how-to-guides/snap-development/debug-snaps/

The public sources support the **mechanism class**. They do not establish the private MVCA incident by themselves.

## Failure classification

```text
FAILURE_CLASS = INVOCATION_QUALIFICATION
TRANSPORT_FAILURE = NO
ADMISSION_FAILURE = NO
ONE_SHOT_REPLAY_FAILURE = NO
TYPED_PROJECTION_FAILURE = NO
DOMAIN_OBSERVATION_COMPLETE = NO
TARGET_ABSENCE_PROVEN = NO
```

The correct terminal observation was UNKNOWN.

## Repair direction selected by MVCA

The rejected repair direction was to reconstruct a broad Snap runtime inside the existing action capsule.

The preferred direction became a separately qualified fixed host observer/provider while preserving:

- logical action identity;
- empty caller params;
- fixed target;
- fixed argv;
- fixed environment;
- exact provider/adapter identity;
- exact result schema;
- one-shot/no-replay semantics;
- retry count zero;
- UNKNOWN on provider/runtime/parser ambiguity.

Historical `v1` remains preserved rather than silently changing meaning.

## Transfer to finite-tool-surface-lab

The incident adds a missing axis to the Tool Surface model.

The current lab already separates:

```text
Available
!= Visible
!= Loaded
!= Selected
!= Authorized
!= Invoked
!= Verified
```

This case motivates, but does not yet canonically prove, an additional distinction:

```text
Invoked Logical Tool
!=
Qualified Invocation
```

A tool schema can remain stable while the provider, launcher, runtime contract, or adapter identity changes underneath it.

Therefore a future experiment should model the active surface not only as a set of logical tools, but also as a mapping:

```text
Logical Tool
    ->
Candidate Provider Binding
    ->
Qualified Invocation Profile
```

## Candidate reusable invariants

These are **research hypotheses** until publicly validated here:

```text
Logical Tool != Provider Implementation
Tool Visibility != Provider Qualification
Selected Tool != Qualified Invocation
Executable Artifact != Qualified Invocation
Provider Replacement != Qualification Continuity
Provider Replacement != Authority Transfer
Path Pinning != Invocation Qualification
Read-only Filesystem Surface != Read-only Capability Surface
Observer Failure != Target Failure
```

## Recommended public falsification lane

Construct a synthetic provider registry where:

- logical tool name/schema is held constant;
- provider/launcher/runtime identity changes independently;
- some bindings are qualified, stale, unsupported, or ambiguous;
- surface selection sees either logical-tool metadata only or qualified-binding metadata.

Measure:

- false-callable rate;
- stale-provider selection;
- qualified-provider recall;
- task/tool coverage;
- requalification cost;
- surface bytes/tokens;
- defer/UNKNOWN rate.

The desired result is not “always use more qualification metadata.”

The experiment should identify the frontier between:

- smaller logical surface;
- sufficient qualified-provider information;
- false executability assumptions;
- requalification overhead.

## Claim ceiling

This file does **not** claim:

- that the MVCA repair is production-qualified;
- that Snap is uniquely problematic;
- that every MCP tool needs a provider layer;
- that a Qualified Invocation Profile is universally optimal;
- that one private MVCA incident is sufficient scientific evidence.

It preserves a failure pattern and converts it into a public, falsifiable research direction.

## Lesson

```text
A Tool can be the right Tool
and still be the wrong Invocation.
```
