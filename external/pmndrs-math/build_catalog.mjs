import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

import * as mathRoot from 'math';
import { mulberry32 } from 'math/random';

const args = process.argv.slice(2);
const outIndex = args.indexOf('--out');
if (outIndex < 0 || !args[outIndex + 1]) throw new Error('MISSING_OUT');
const outPath = path.resolve(args[outIndex + 1]);

const seedIndex = args.indexOf('--seed');
const seed = seedIndex >= 0 ? Number(args[seedIndex + 1]) : 20260926;

const sampleIndex = args.indexOf('--sample-pairs');
const samplePairs = sampleIndex >= 0 ? Number(args[sampleIndex + 1]) : 64;

const root = path.dirname(new URL(import.meta.url).pathname);
const apiPath = path.join(root, 'node_modules', 'math', 'API.md');
const pkgPath = path.join(root, 'node_modules', 'math', 'package.json');
const lockPath = path.join(root, 'package-lock.json');

if (!fs.existsSync(apiPath)) throw new Error('API_DOCS_MISSING');
if (!fs.existsSync(pkgPath)) throw new Error('PACKAGE_JSON_MISSING');
if (!fs.existsSync(lockPath)) throw new Error('PACKAGE_LOCK_MISSING');

const api = fs.readFileSync(apiPath, 'utf8');
const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
const lock = JSON.parse(fs.readFileSync(lockPath, 'utf8'));
const integrity = lock.packages?.['node_modules/math']?.integrity ?? null;

const namespaces = [
  'vec2', 'vec3', 'vec4', 'euler', 'quat', 'quat2',
  'mat2', 'mat2d', 'mat3', 'mat4',
];

function descriptionFor(namespace, name) {
  const needles = [
    `\`${namespace}.${name}(`,
    `\`${namespace}.${name} =`,
  ];
  for (const line of api.split('\n')) {
    if (needles.some((needle) => line.includes(needle))) {
      const marker = ' — ';
      return line.includes(marker)
        ? line.slice(line.indexOf(marker) + marker.length).trim()
        : line.trim();
    }
  }
  return '';
}

const records = [];
const equivalenceGroups = [];

for (const namespace of namespaces) {
  const object = mathRoot[namespace];
  if (!object || typeof object !== 'object') {
    throw new Error(`NAMESPACE_MISSING:${namespace}`);
  }

  const functions = Object.entries(object)
    .filter(([, value]) => typeof value === 'function')
    .sort(([a], [b]) => a.localeCompare(b));

  const byIdentity = new Map();
  for (const [name, fn] of functions) {
    if (!byIdentity.has(fn)) byIdentity.set(fn, []);
    byIdentity.get(fn).push(name);
  }

  const canonicalByName = new Map();
  for (const names of byIdentity.values()) {
    names.sort();
    const canonical = names[0];
    for (const name of names) canonicalByName.set(name, canonical);
    if (names.length > 1) {
      equivalenceGroups.push({
        group_id: `eq:${namespace}:${canonical}`,
        namespace,
        canonical,
        members: [...names],
      });
    }
  }

  for (const [name, fn] of functions) {
    const canonical = canonicalByName.get(name);
    records.push({
      tool_id: `${namespace}.${name}`,
      namespace,
      name,
      arity: fn.length,
      description: descriptionFor(namespace, name),
      equivalence_group: `eq:${namespace}:${canonical}`,
      alias_of: name === canonical ? null : `${namespace}.${canonical}`,
    });
  }
}

records.sort((a, b) => a.tool_id.localeCompare(b.tool_id));
equivalenceGroups.sort((a, b) => a.group_id.localeCompare(b.group_id));

const byName = new Map();
for (const record of records) {
  if (!byName.has(record.name)) byName.set(record.name, []);
  byName.get(record.name).push(record.tool_id);
}

const homonymGroups = [...byName.entries()]
  .filter(([, members]) => members.length > 1)
  .map(([name, members]) => ({
    group_id: `homonym:${name}`,
    name,
    members: members.sort(),
  }))
  .sort((a, b) => a.group_id.localeCompare(b.group_id));

const aliasPairs = [];
for (const group of equivalenceGroups) {
  for (let i = 0; i < group.members.length; i++) {
    for (let j = i + 1; j < group.members.length; j++) {
      aliasPairs.push([
        `${group.namespace}.${group.members[i]}`,
        `${group.namespace}.${group.members[j]}`,
      ]);
    }
  }
}

const homonymPairs = [];
for (const group of homonymGroups) {
  for (let i = 0; i < group.members.length; i++) {
    for (let j = i + 1; j < group.members.length; j++) {
      homonymPairs.push([group.members[i], group.members[j]]);
    }
  }
}

function deterministicSample(items, count, state) {
  if (items.length <= count) return [...items];
  const pool = items.map((item) => [...item]);
  const out = [];
  while (out.length < count && pool.length) {
    const index = mulberry32.next(state) % pool.length;
    out.push(pool[index]);
    pool.splice(index, 1);
  }
  return out;
}

const rngState = mulberry32.create(seed);
const samples = {
  alias_pairs: deterministicSample(aliasPairs, samplePairs, rngState),
  homonym_pairs: deterministicSample(homonymPairs, samplePairs, rngState),
};

const catalog = {
  schema_version: 'ftsl-external-tool-catalog-v0.1',
  source: {
    package: pkg.name,
    version: pkg.version,
    npm_integrity: integrity,
    repository: pkg.repository,
  },
  namespaces,
  tool_count: records.length,
  alias_equivalence_group_count: equivalenceGroups.length,
  cross_type_homonym_group_count: homonymGroups.length,
  records,
  equivalence_groups: equivalenceGroups,
  homonym_groups: homonymGroups,
  deterministic_samples: {
    seed,
    requested_pairs_per_class: samplePairs,
    ...samples,
  },
};

const text = JSON.stringify(catalog, null, 2) + '\n';
fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, text);

const digest = crypto.createHash('sha256').update(text).digest('hex');
console.log(JSON.stringify({
  tool_count: catalog.tool_count,
  alias_equivalence_group_count: catalog.alias_equivalence_group_count,
  cross_type_homonym_group_count: catalog.cross_type_homonym_group_count,
  sampled_alias_pairs: samples.alias_pairs.length,
  sampled_homonym_pairs: samples.homonym_pairs.length,
  catalog_sha256: digest,
}, null, 2));
