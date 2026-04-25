#!/usr/bin/env node

import { spawnSync } from 'node:child_process';
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { resolve } from 'node:path';

const pipelineDir = resolve(process.argv[2] || process.cwd());
const repoRoot = resolve(pipelineDir, '..');
const careerOpsDir = resolve(repoRoot, 'career-ops');
const outputPath = resolve(repoRoot, 'data', 'ats_raw.json');

mkdirSync(resolve(repoRoot, 'data'), { recursive: true });
mkdirSync(resolve(careerOpsDir, 'data'), { recursive: true });

const pipelinePath = resolve(careerOpsDir, 'data', 'pipeline.md');
const historyPath = resolve(careerOpsDir, 'data', 'scan-history.tsv');

if (!existsSync(pipelinePath)) {
  writeFileSync(pipelinePath, '## Pendientes\n\n## Procesadas\n', 'utf-8');
}

if (!existsSync(historyPath)) {
  writeFileSync(historyPath, 'url\tfirst_seen\tportal\ttitle\tcompany\tstatus\n', 'utf-8');
}

const beforePipeline = existsSync(pipelinePath)
  ? readFileSync(pipelinePath, 'utf-8')
  : '';
const beforeHistory = existsSync(historyPath)
  ? readFileSync(historyPath, 'utf-8')
  : '';

const result = spawnSync('npm', ['run', 'scan'], {
  cwd: careerOpsDir,
  encoding: 'utf-8',
  shell: true,
});

if (result.stdout) process.stdout.write(result.stdout);
if (result.stderr) process.stderr.write(result.stderr);

const afterPipeline = existsSync(pipelinePath)
  ? readFileSync(pipelinePath, 'utf-8')
  : '';
const afterHistory = existsSync(historyPath)
  ? readFileSync(historyPath, 'utf-8')
  : '';

const beforePipelineSet = new Set(beforePipeline.split(/\r?\n/));
const newOffers = [];
for (const line of afterPipeline.split(/\r?\n/)) {
  if (!line.startsWith('- [ ] ')) continue;
  if (beforePipelineSet.has(line)) continue;
  const payload = line.slice(6);
  const parts = payload.split(' | ');
  if (parts.length >= 3) {
    newOffers.push({
      url: parts[0].trim(),
      company: parts[1].trim(),
      title: parts[2].trim(),
      location: '',
      description: '',
      source: 'career-ops-scan',
    });
  }
}

if (newOffers.length === 0 && afterHistory !== beforeHistory) {
  const beforeHistorySet = new Set(beforeHistory.split(/\r?\n/));
  for (const row of afterHistory.split(/\r?\n/).filter(Boolean)) {
    if (beforeHistorySet.has(row)) continue;
    const cols = row.split('\t');
    if (cols.length >= 5 && cols[0] !== 'url') {
      newOffers.push({
        url: cols[0].trim(),
        company: cols[4].trim(),
        title: cols[3].trim(),
        location: '',
        description: '',
        source: cols[2].trim() || 'career-ops-scan',
      });
    }
  }
}

writeFileSync(outputPath, JSON.stringify(newOffers, null, 2), 'utf-8');

if (result.status !== 0) {
  process.exit(result.status ?? 1);
}
