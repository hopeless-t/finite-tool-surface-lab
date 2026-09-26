# COUNCIL-006 — pmndrs/math Dogfood Shape

## Question

How should the lab taste-test an unfamiliar computational library without prematurely adopting it?

## Candidates

A. Isolated published-package dogfood on a research branch and GitHub runner.  
B. Add it to root repository dependencies immediately.  
C. Vendor upstream source at a pinned commit.  
D. Inspect only the Agent Skill.  
E. Skip because current experiments do not require it.

## Council

A gives direct runtime evidence while preserving the main Python dependency boundary.

B gives realism but turns exploration into adoption.

C maximizes source identity but creates maintenance and build burden before utility is known.

D tests documentation but not computation.

E violates the purpose of Tool Surface dogfooding: unknown future usefulness is precisely why a bounded taste-test is useful.

## 250k synthetic planning sensitivity

Seed: 20260926.

Criteria:
- isolation;
- reproducibility;
- fidelity to real consumption;
- footprint observability;
- GitHub Actions efficiency;
- maintenance cost.

Result:

```text
A isolated published package   99.9976%
C vendored source               0.0024%
B root dependency               0.0000%
D skill only                    0.0000%
E skip                          0.0000%
```

Mean utility:

```text
A 0.9205
C 0.8232
D 0.7590
B 0.7200
E 0.6469
```

Planning robustness only.

## Decision

```text
ISOLATED_TASTE_TEST_BEFORE_ADOPTION
```

The first taste-test measures usability, correctness, package/Skill footprint, and operational friction. Performance timing remains descriptive until a dedicated benchmark contract freezes it.
