import fs from 'node:fs';
import path from 'node:path';
import { performance } from 'node:perf_hooks';

import { vec3 } from 'math';
import { mulberry32 } from 'math/random';
import { quickhull2 } from 'math/geometry';

const ROOT = path.resolve(import.meta.dirname);
const pkgRoot = path.resolve(ROOT, 'node_modules', 'math');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function dirStats(root) {
  let bytes = 0;
  let files = 0;
  const stack = [root];
  while (stack.length) {
    const current = stack.pop();
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) stack.push(full);
      else if (entry.isFile()) {
        files += 1;
        bytes += fs.statSync(full).size;
      }
    }
  }
  return { files, bytes };
}

function median(values) {
  const x = [...values].sort((a, b) => a - b);
  const mid = Math.floor(x.length / 2);
  return x.length % 2 ? x[mid] : (x[mid - 1] + x[mid]) / 2;
}

function bench(label, fn, blocks = 9) {
  for (let i = 0; i < 3; i++) fn();
  const ms = [];
  let checksum = 0;
  for (let i = 0; i < blocks; i++) {
    const t0 = performance.now();
    checksum += fn();
    ms.push(performance.now() - t0);
  }
  return { label, blocks, median_ms: median(ms), min_ms: Math.min(...ms), max_ms: Math.max(...ms), checksum };
}

const correctness = {};

{
  const a = [1, 2, 3];
  const b = [4, 5, 6];
  const out = [0, 0, 0];
  const returned = vec3.add(out, a, b);
  assert(returned === out, 'vec3.add must return caller-owned out');
  assert(JSON.stringify(out) === JSON.stringify([5, 7, 9]), 'vec3.add result mismatch');
  correctness.out_identity = true;
}

{
  const v = [3, 4, 0];
  const returned = vec3.normalize(v, v);
  assert(returned === v, 'vec3.normalize alias must return same object');
  assert(Math.abs(v[0] - 0.6) < 1e-12 && Math.abs(v[1] - 0.8) < 1e-12, 'alias normalize mismatch');
  correctness.alias_safe = true;
}

{
  const s1 = mulberry32.create(123456789);
  const s2 = mulberry32.create(123456789);
  const a = Array.from({ length: 32 }, () => mulberry32.next(s1));
  const b = Array.from({ length: 32 }, () => mulberry32.next(s2));
  assert(JSON.stringify(a) === JSON.stringify(b), 'seeded RNG replay mismatch');
  correctness.seeded_rng_replay = true;
  correctness.rng_prefix = a.slice(0, 8);
}

{
  const points = [
    0, 0,
    1, 0,
    1, 1,
    0, 1,
    0.5, 0.5,
  ];
  const hull = quickhull2(points);
  const set = new Set(hull);
  assert(set.size === 4, 'quickhull2 hull cardinality mismatch');
  for (const index of [0, 1, 2, 3]) assert(set.has(index), 'quickhull2 missing square vertex');
  assert(!set.has(4), 'quickhull2 incorrectly includes interior point');
  correctness.quickhull2 = true;
  correctness.quickhull2_indices = hull;
}

const skillPath = path.join(pkgRoot, 'skills', 'math', 'SKILL.md');
const apiPath = path.join(pkgRoot, 'API.md');
assert(fs.existsSync(skillPath), 'published package missing skills/math/SKILL.md');
assert(fs.existsSync(apiPath), 'published package missing API.md');

const skillText = fs.readFileSync(skillPath, 'utf8');
const skill = {
  present: true,
  bytes: Buffer.byteLength(skillText),
  lines: skillText.split('\n').length,
  mentions_allocation: /allocat/i.test(skillText),
  mentions_caller_owned: /caller-owned/i.test(skillText),
  mentions_monomorphic: /monomorphic/i.test(skillText),
};

const footprint = dirStats(pkgRoot);

const N = 400_000;
const A = [1.25, 2.5, 3.75];
const B = [0.5, 0.25, 0.125];

const mathBench = bench('math_vec3_scaleAndAdd_in_place', () => {
  const out = [0, 0, 0];
  let sum = 0;
  for (let i = 0; i < N; i++) {
    vec3.scaleAndAdd(out, A, B, (i & 31) * 0.01);
    sum += out[0] + out[1] + out[2];
  }
  return sum;
});

const manualInPlaceBench = bench('manual_in_place', () => {
  const out = [0, 0, 0];
  let sum = 0;
  for (let i = 0; i < N; i++) {
    const scale = (i & 31) * 0.01;
    out[0] = A[0] + B[0] * scale;
    out[1] = A[1] + B[1] * scale;
    out[2] = A[2] + B[2] * scale;
    sum += out[0] + out[1] + out[2];
  }
  return sum;
});

const allocatingBench = bench('allocating_array_baseline', () => {
  let sum = 0;
  for (let i = 0; i < N; i++) {
    const scale = (i & 31) * 0.01;
    const out = [
      A[0] + B[0] * scale,
      A[1] + B[1] * scale,
      A[2] + B[2] * scale,
    ];
    sum += out[0] + out[1] + out[2];
  }
  return sum;
});

const report = {
  schema_version: 'ftsl-dogfood-pmndrs-math-v0.1',
  package: {
    name: 'math',
    requested_version: '0.1.0',
    upstream_repo: 'pmndrs/math',
    observed_upstream_commit: '983a607676026c5f1b950f876bc688988de824e5',
  },
  runtime: {
    node: process.version,
    platform: process.platform,
    arch: process.arch,
  },
  correctness,
  skill,
  footprint,
  benchmark: {
    note: 'Descriptive GitHub-runner timing only; not a canonical performance benchmark.',
    iterations_per_block: N,
    results: [mathBench, manualInPlaceBench, allocatingBench],
  },
  taste_dimensions: {
    import_smoke: 'PASS',
    alias_semantics: 'PASS',
    deterministic_rng: 'PASS',
    geometry_smoke: 'PASS',
    shipped_agent_skill: 'PASS',
  },
};

fs.mkdirSync(path.join(ROOT, 'out'), { recursive: true });
fs.writeFileSync(path.join(ROOT, 'out', 'report.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
