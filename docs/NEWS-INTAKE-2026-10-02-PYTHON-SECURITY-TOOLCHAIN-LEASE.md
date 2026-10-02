# News Intake 2026-10-02 — Python Security Releases and Toolchain Leases

Status: RESEARCH INTAKE / NO TOOLCHAIN UPGRADE

Primary sources:
- https://www.python.org/downloads/release/python-3148/
- https://blog.python.org/2026/10/python-31022-31117/

Python 3.14.8 was released as an expedited security release with multiple CVE fixes.
The same coordinated release wave includes 3.12.15 and 3.13.16.

## Research problem

Two desirable properties conflict:

    exact patch pin -> strong reproducibility
    floating minor line -> security freshness

An exact pin can become stale after an upstream security release.
A floating pin can change behavior without an explicit repository revision.

Therefore a runtime identity needs a time-sensitive qualification coordinate.

## Toolchain lease model

Represent a toolchain binding as:

    ToolchainBinding = (
      runtime,
      exact_version,
      artifact/hash where available,
      qualified_at,
      security_source_snapshot,
      lease_state
    )

Lease state:
- CURRENT
- REQUALIFY_REQUIRED
- EXPIRED
- UNKNOWN

A new upstream security release does not prove that the current runtime is exploitable in
this project. It is sufficient to invalidate an indefinite "current forever" assumption.

## Hypothesis FTS-TC-H1 — immutable identity needs mutable freshness

Reproducibility identity and security freshness should be independent fields.

    same exact binary
      can remain reproducible
      while becoming stale for security policy

## Hypothesis FTS-TC-H2 — automatic silent patch drift is also evidence loss

If CI requests only "3.12", the resolved patch can change across runs.
That may be a good maintenance policy but weakens exact replay unless the resolved patch
is recorded in evidence.

## Proposed experiment

For each CI/runtime lane record:
- requested version,
- resolved exact version,
- executable path,
- build/runtime hash where practical,
- upstream security release date,
- qualification date.

When a security release appears:
- do not silently mutate a frozen evidence run,
- open a requalification lane,
- compare regression/evidence,
- promote only after pass.

## Current Catfood observation

Some Catfood repositories request a minor line such as Python 3.12, while MVCA Gate 0 has
used an exact patch version in its frozen environment.

This intake intentionally does not change either policy.

## Claim ceiling

    TOOLCHAIN_SECURITY_LEASE_HYPOTHESIS_DEFINED

No CVE exploitability claim for Catfood code and no runtime upgrade is made here.
