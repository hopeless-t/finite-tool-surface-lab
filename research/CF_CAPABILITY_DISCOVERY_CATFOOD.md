# BENCH-007 — Cloudflare cf capability-discovery Catfood

Source inspected: `cloudflare/cf`.

Observed source blobs on 2026-10-02:
- generated command metadata: 5,261,155 bytes;
- generated exact schema metadata: 2,826,987 bytes.

The CLI does not tell coding agents to walk this tree with repeated nested
`--help`. Its agent-specific help instructs them to:

1. describe the task/resource anonymously;
2. run local `cf cli search`;
3. receive five compact JSON matches containing only `command` and `summary`;
4. inspect the exact request with `cf schema <command>`;
5. then invoke the selected command.

The implementation builds a local MiniSearch index with weighted fields and
caps the result at five.

This is a concrete finite-tool-surface pattern:

`huge capability catalogue -> local intent projection -> top-k tiny surface -> exact schema -> invocation`

Second bite: generated mutation commands may return normally after an
interactive confirmation says `Aborted.`. Therefore:

`returncode == 0` is process completion, not proof that an external effect
occurred.

MVCA implication:
mutation providers need semantic receipts/readback. A zero process exit without
an effect receipt remains UNKNOWN, not APPLIED.

This bench performs no Cloudflare API request and grants no authority.
