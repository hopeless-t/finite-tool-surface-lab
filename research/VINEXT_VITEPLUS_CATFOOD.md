# COMPAT-001 — Vinext compatibility evidence Catfood

Source inspected: `cloudflare/vinext` 1.0-era code and compatibility tests.

Useful atom:

`source API surface -> per-feature status -> test evidence -> workload-required subset -> substitution gate`

Vinext does not flatten every gap into one boolean. Current source uses states including
`supported`, `partial`, `unsupported` and suite-level
`deferred` / `needs-vite-equivalent`.

Catfood translation:

- a global "95% compatible" style claim is not enough for a concrete worker;
- the relevant question is whether *this workload's required features* are supported;
- a supported label without evidence should remain REVIEW;
- compatibility never proves implementation/runtime identity.

Vite+ was inspected in the same bite. Its single `vp` entrypoint unifies runtime,
package manager, dev/build/test/lint/format and task graph control, but that is interface
consolidation, not capability minimization. No Vite+ subsystem is imported here.
