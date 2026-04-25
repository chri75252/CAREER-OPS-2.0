# Career-Ops Workflow Redesign — Surgical Implementation Plan

## Objective

Implement the agreed Career-Ops workflow redesign without breaking existing workflows:

1. keep **Results** and **Queue** as separate lifecycle stages;
2. merge/disambiguate discovery flows over time;
3. add deterministic, no-LLM preliminary ranking;
4. reorder the Queue best-first before `/career-ops pipeline` runs;
5. separate evaluation/scoring reports from Deep/PDF/Apply artifacts;
6. centralize workflow gates for PDF / Apply / Deep thresholds;
7. fix dashboard semantics so sections only reflect the artifacts they are meant to represent.

This is a plan only. No implementation has been applied from this file.

---

## Grounding files inspected

Primary current behavior:

- `career-ops/scan.mjs`
- `career-ops/import-external-jobs.mjs`
- `career-ops/data/pipeline.md`
- `career-ops/data/external_jobs.json`
- `career-ops/portals.yml`
- `career-ops/config/profile.yml`
- `config/pipeline.yaml`
- `pipeline/run_pipeline.py`
- `pipeline/export_ats_lane.mjs`
- `pipeline/ingest_to_career_ops.py`
- `feed-fetcher/fetcher.py`
- `jobspy-wrapper/scrape.py`
- `dedupe-merge/merger.py`

Dashboard/artifact behavior:

- `career-ops/dashboard/internal/data/discovery.go`
- `career-ops/dashboard/internal/model/discovery.go`
- `career-ops/dashboard/internal/ui/screens/discovery.go`
- `career-ops/dashboard/internal/model/workflow_section.go`
- `career-ops/dashboard/internal/data/workflow_status.go`

Workflow docs/scripts:

- `career-ops/modes/pipeline.md`
- `career-ops/modes/auto-pipeline.md`
- `career-ops/modes/oferta.md`
- `career-ops/modes/deep.md`
- `career-ops/modes/pdf.md`
- `career-ops/modes/apply.md`
- `career-ops/generate-pdf.mjs`
- `career-ops/merge-tracker.mjs`
- `career-ops/verify-pipeline.mjs`
- `career-ops/package.json`

---

## Non-goals / hard boundaries

- Do **not** introduce a database.
- Do **not** use LLMs, embeddings, paid APIs, or external services for preliminary ranking.
- Do **not** delete or move existing reports/PDFs/JDs in the first pass.
- Do **not** change `/career-ops pipeline` into a complex selector; keep it top-down after Queue ranking.
- Do **not** make Queue and Results identical views.
- Do **not** break current `pipeline.md` checkbox format.
- Do **not** remove legacy artifact reads until compatibility is proven.

---

## Target lifecycle

```text
Unified discovery sources
  -> normalized Results ledger
  -> deterministic rough ranking
  -> ranked Queue / evaluation inbox
  -> LLM pipeline scoring
  -> evaluation reports + tracker
  -> gated PDF / Deep / Apply workflows
```

### Stage meanings

| Stage | Meaning | Canonical artifact |
|---|---|---|
| Results | Raw normalized discovery ledger, with source/provenance/ranking/status metadata | `career-ops/data/external_jobs.json` initially; optional later alias `discovery-results.json` |
| Queue | Ranked evaluation inbox processed by `/career-ops pipeline` | `career-ops/data/pipeline.md` |
| Evaluation | LLM scoring output | `career-ops/reports/evaluations/*.md` |
| Deep | Actual deep research output | `career-ops/reports/deep/*.md` |
| PDF | Actual tailored CV artifacts | `career-ops/output/*.pdf` and/or `career-ops/output/pdf/*.pdf` |
| Apply | Draft/application workflow artifacts | future `career-ops/reports/apply/*.md` or `career-ops/applications/drafts/*` |
| Track | Canonical application tracker | `career-ops/data/applications.md` |

---

## Recommended implementation phases

### Phase 0 — Safety harness and compatibility checks

Create backups before any implementation pass.

Backup target:

- `backup/career_ops_workflow_redesign_20260424/`

Files likely to change:

- `career-ops/package.json`
- `career-ops/scan.mjs`
- `career-ops/import-external-jobs.mjs`
- `career-ops/dashboard/internal/data/discovery.go`
- `career-ops/dashboard/internal/model/discovery.go`
- `career-ops/dashboard/internal/ui/screens/discovery.go`
- `career-ops/dashboard/internal/model/workflow_section.go`
- `career-ops/dashboard/internal/data/workflow_status.go`
- `career-ops/modes/pipeline.md`
- `career-ops/modes/auto-pipeline.md`
- `career-ops/modes/oferta.md`
- `career-ops/modes/deep.md`
- `career-ops/modes/pdf.md`
- `career-ops/modes/apply.md`
- `career-ops/verify-pipeline.mjs`
- `pipeline/run_pipeline.py`
- new `career-ops/config/workflow.yml`
- new `career-ops/rank-queue.mjs`
- optional new `career-ops/data/queue-ranking.json`

Validation commands after every implementation phase:

```bash
npm run doctor
npm run sync-check
npm run verify
node rank-queue.mjs --dry-run
python -c "import yaml, pathlib; [yaml.safe_load(pathlib.Path(f).read_text(encoding='utf-8')) for f in ['career-ops/config/profile.yml','career-ops/portals.yml','career-ops/config/workflow.yml','config/pipeline.yaml']]"
```

Dashboard validation:

```bash
go test ./...
```

Run from:

- `career-ops/dashboard` for Go dashboard tests/build, if applicable.

---

## Phase 1 — Add central workflow configuration

### Goal

Create one configuration source for ranking weights and workflow gates.

### New file

`career-ops/config/workflow.yml`

### Proposed content

```yaml
workflow_gates:
  action_min_score: 4.0
  auto_pdf_min_score: 4.0
  apply_ready_min_score: 4.0
  deep_research_min_score: 4.0
  high_priority_min_score: 4.2

ranking:
  queue_min_score: 45
  reject_below_score: 25
  weights:
    title: 35
    role_family: 20
    location: 15
    source: 10
    seniority: 10
    company_domain: 5
    recency: 5
  tiers:
    primary: 80
    secondary: 65
    stretch: 50
    weak: 25
  source_weights:
    career-ops-scan: 10
    greenhouse: 9
    ashby: 9
    lever: 8
    jobspy:linkedin: 7
    jobspy:indeed: 6
    jobspy:glassdoor: 6
    jobspy:bayt: 6
    remoteok: 6
    remotive: 6
    weworkremotely: 6
  title_patterns:
    primary:
      - solutions engineer
      - solutions consultant
      - technical account manager
      - implementation manager
      - implementation consultant
      - professional services consultant
      - customer engineer
    secondary:
      - solutions architect
      - customer success architect
      - technical program manager
      - delivery manager
      - product operations
      - business systems
    negative:
      - research scientist
      - applied scientist
      - machine learning engineer
      - ml engineer
      - data scientist
      - backend engineer
      - frontend engineer
      - platform engineer
      - sre
      - account executive
      - sales development
      - recruiter
  location_patterns:
    strong:
      - remote
      - emea
      - europe
      - united kingdom
      - london
      - dublin
      - germany
      - netherlands
      - uae
    weak_negative:
      - onsite only
      - must be based in us
      - us only
```

### Why this is low-risk

- New file only.
- No existing workflows depend on it until scripts/docs are updated.
- Future threshold changes require one edit.

### Diff sketch

```diff
*** Add File: career-ops/config/workflow.yml
+workflow_gates:
+  action_min_score: 4.0
+  auto_pdf_min_score: 4.0
+  apply_ready_min_score: 4.0
+  deep_research_min_score: 4.0
+  high_priority_min_score: 4.2
+ranking:
+  queue_min_score: 45
+  reject_below_score: 25
+  weights:
+    title: 35
+    role_family: 20
+    location: 15
+    source: 10
+    seniority: 10
+    company_domain: 5
+    recency: 5
```

---

## Phase 2 — Add deterministic ranking and queue ordering

### Goal

Add cheap, explainable, no-LLM ranking before expensive LLM scoring.

### New file

`career-ops/rank-queue.mjs`

### Inputs

- `career-ops/data/pipeline.md`
- `career-ops/data/external_jobs.json`
- `career-ops/portals.yml`
- `career-ops/config/profile.yml`
- `career-ops/config/workflow.yml`
- parent `config/pipeline.yaml` if present
- `career-ops/data/applications.md` for already-evaluated dedup/status awareness

### Outputs

- rewrites `career-ops/data/pipeline.md` with **unprocessed `- [ ]` entries sorted best-first**;
- preserves `## Procesadas` entries below unprocessed entries;
- writes sidecar metadata:
  - `career-ops/data/queue-ranking.json`

### Do not store ranking metadata directly in `pipeline.md`

Reason: current parsers and LLM pipeline docs expect simple lines like:

```md
- [ ] URL | Company | Title
```

Adding columns risks breaking agents or scripts that split by ` | `.

Use `queue-ranking.json` instead:

```json
{
  "generated_at": "2026-04-24T04:00:00.000Z",
  "items": [
    {
      "url": "https://...",
      "company": "Hightouch",
      "title": "Implementation Manager, EMEA",
      "rough_score": 92,
      "fit_tier": "primary",
      "role_family": "implementation",
      "reason_codes": ["TITLE_PRIMARY", "LOCATION_EMEA", "SOURCE_ATS"]
    }
  ]
}
```

### Ranking algorithm

Deterministic score out of 100.

Recommended first-pass factors:

| Factor | Max points | Notes |
|---|---:|---|
| Title match | 35 | primary/secondary/negative patterns from `workflow.yml` + `portals.yml` |
| Role family | 20 | matches target archetypes in `profile.yml` |
| Location / remote | 15 | remote/EMEA/GMT/UAE-friendly signals |
| Source quality | 10 | ATS/company pages > LinkedIn > generic boards |
| Seniority alignment | 10 | senior/lead boost; junior/intern reject |
| Company/domain fit | 5 | tracked company or domain keywords |
| Recency | 5 | only if valid `posted_at` exists |

Hard negative penalties:

- junior/intern: strong penalty or reject;
- pure ML/research/software engineering: penalty unless title also has solutions/implementation context;
- AE/SDR/recruiter: reject/low score;
- location restrictions incompatible with UAE/remote: penalty.

### Ranking function sketch

```js
function rankJob(job, cfg) {
  const haystack = `${job.title || ''} ${job.company || ''} ${job.location || ''} ${(job.tags || []).join(' ')} ${job.description || ''}`.toLowerCase();
  const reasons = [];
  let score = 0;

  if (matchesAny(haystack, cfg.ranking.title_patterns.negative)) {
    score -= 30;
    reasons.push('NEGATIVE_TITLE');
  }

  if (matchesAny(haystack, cfg.ranking.title_patterns.primary)) {
    score += 35;
    reasons.push('TITLE_PRIMARY');
  } else if (matchesAny(haystack, cfg.ranking.title_patterns.secondary)) {
    score += 24;
    reasons.push('TITLE_SECONDARY');
  }

  if (matchesAny(haystack, cfg.ranking.location_patterns.strong)) {
    score += 15;
    reasons.push('LOCATION_STRONG');
  }

  if (/senior|lead|principal|staff|director/.test(haystack)) {
    score += 8;
    reasons.push('SENIORITY_STRONG');
  }
  if (/junior|intern|graduate/.test(haystack)) {
    score -= 25;
    reasons.push('SENIORITY_NEGATIVE');
  }

  score += sourceScore(job.source, cfg);
  const bounded = Math.max(0, Math.min(100, score));
  return { rough_score: bounded, fit_tier: tierForScore(bounded, cfg), reason_codes: reasons };
}
```

### Queue rewrite strategy

Parse `pipeline.md` section-aware:

```js
function parsePipelineSections(raw) {
  const lines = raw.split(/\r?\n/);
  const before = [];
  const pending = [];
  const processed = [];
  let section = 'before';

  for (const line of lines) {
    if (/^##\s+Pendientes/i.test(line.trim())) { section = 'pending'; continue; }
    if (/^##\s+Procesadas/i.test(line.trim())) { section = 'processed'; continue; }
    if (section === 'pending' && line.trim().startsWith('- [ ]')) pending.push(parseQueueLine(line));
    else if (section === 'processed' && line.trim().startsWith('- [x]')) processed.push(line);
    else if (section === 'before') before.push(line);
  }
  return { before, pending, processed };
}
```

Write back:

```md
## Pendientes

- [ ] best-url | Company | Title
- [ ] next-best-url | Company | Title

## Procesadas

- [x] already-processed...
```

### Dry-run mode

`node rank-queue.mjs --dry-run` should:

- not write files;
- print top 25 before/after;
- print counts by `fit_tier`;
- print number of existing processed rows preserved.

### Diff sketch: package script

```diff
diff --git a/career-ops/package.json b/career-ops/package.json
@@
     "liveness": "node check-liveness.mjs",
     "scan": "node scan.mjs",
-    "import:external": "node import-external-jobs.mjs"
+    "import:external": "node import-external-jobs.mjs",
+    "rank": "node rank-queue.mjs",
+    "rank:dry-run": "node rank-queue.mjs --dry-run"
```

### Diff sketch: rank after external import

Modify `career-ops/import-external-jobs.mjs` after successful import:

```diff
diff --git a/career-ops/import-external-jobs.mjs b/career-ops/import-external-jobs.mjs
@@
 import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
 import { join, dirname } from 'path';
 import { fileURLToPath } from 'url';
+import { spawnSync } from 'child_process';
@@
 console.log(`Imported ${imported} external job(s) into data/pipeline.md`);
+
+const rankResult = spawnSync(process.execPath, [join(CAREER_OPS, 'rank-queue.mjs')], {
+  cwd: CAREER_OPS,
+  stdio: 'inherit',
+});
+if (rankResult.status !== 0) {
+  console.warn('⚠️  Queue ranking failed; imported jobs were preserved in pipeline.md.');
+}
```

### Diff sketch: rank after scan

Modify `career-ops/scan.mjs` after appending new offers:

```diff
diff --git a/career-ops/scan.mjs b/career-ops/scan.mjs
@@
 import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
 import { join, dirname } from 'path';
 import { fileURLToPath } from 'url';
+import { spawnSync } from 'child_process';
@@
 console.log(`New offers added: ${newOffers.length}`);
+if (newOffers.length > 0) {
+  const rankResult = spawnSync(process.execPath, [join(__dirname, 'rank-queue.mjs')], {
+    cwd: __dirname,
+    stdio: 'inherit',
+  });
+  if (rankResult.status !== 0) {
+    console.warn('⚠️  Queue ranking failed; scan results were still preserved.');
+  }
+}
```

Safety behavior: ranking failure must never erase scan/import output.

---

## Phase 3 — Dashboard support for ranking metadata

### Goal

Show enough ranking metadata to make Queue ordering explainable without rewriting dashboard architecture.

### Current files

- `dashboard/internal/model/discovery.go`
- `dashboard/internal/data/discovery.go`
- `dashboard/internal/ui/screens/discovery.go`

### Model changes

Add optional fields to `PendingJob` and `ExternalJob`:

```diff
diff --git a/career-ops/dashboard/internal/model/discovery.go b/career-ops/dashboard/internal/model/discovery.go
@@
 type PendingJob struct {
     Done    bool
     URL     string
     Company string
     Title   string
+    RoughScore int
+    FitTier    string
+    ReasonCodes []string
 }
@@
 type ExternalJob struct {
     Title       string   `json:"title"`
     Company     string   `json:"company"`
     URL         string   `json:"url"`
     Location    string   `json:"location"`
     Source      string   `json:"source"`
     PostedAt    string   `json:"posted_at"`
     Tags        []string `json:"tags"`
     Description string   `json:"description"`
+    RoughScore  int      `json:"rough_score"`
+    FitTier     string   `json:"fit_tier"`
+    ReasonCodes []string `json:"reason_codes"`
 }
```

### Loader changes

Read `data/queue-ranking.json` if present and enrich pending jobs by URL.

```diff
diff --git a/career-ops/dashboard/internal/data/discovery.go b/career-ops/dashboard/internal/data/discovery.go
@@
 pending, pendingErr := ParsePendingQueue(careerOpsPath)
 results, resultsErr := ParseExternalJobs(careerOpsPath)
+rankings := ParseQueueRankings(careerOpsPath)
@@
 for i := range pending {
+    if ranking, ok := rankings[pending[i].URL]; ok {
+        pending[i].RoughScore = ranking.RoughScore
+        pending[i].FitTier = ranking.FitTier
+        pending[i].ReasonCodes = ranking.ReasonCodes
+    }
 }
```

### UI changes

Change Queue line rendering from:

```text
[ ] Company | Title
```

to:

```text
[92 primary] Company | Title
```

Keep fallback if no ranking metadata:

```text
[ ] Company | Title
```

No dashboard navigation changes needed.

---

## Phase 3.5 — Dashboard visibility improvements for real outputs

### Goal

Make dashboard sections show:

1. not only counts, but also recent item names for workflows that actually produced outputs;
2. the folder/path where those outputs are stored;
3. concise "investigation paths" in Help for operator-facing vs debug-facing artifacts.

### User-facing behavior requirement

For sections like PDF / Deep / Apply, the dashboard should not stop at:

- `PDF files: 3`
- `Reports: 5`

It should also show recent concrete items, for example:

- `Latest PDF: cv-christian-haddad-hightouch-implementation-manager.pdf`
- `Recent PDFs: Hightouch | Implementation Manager, EMEA; Intercom | Solutions Engineer`
- `Latest Deep report: 014-hightouch-implementation-manager.md`
- `Recent Apply drafts: Hightouch | Implementation Manager, EMEA`

### Small, low-risk implementation approach

Do not build a new relational mapping layer in pass 1.

Instead:

- derive recent filenames from each section's artifact directory;
- when possible, infer display names from file names or linked tracker/report rows;
- show top 3 recent names only;
- preserve current count summaries.

### Files likely to change

- `career-ops/dashboard/internal/data/workflow_status.go`
- `career-ops/dashboard/internal/ui/screens/help.go`
- optional: `career-ops/dashboard/internal/model/workflow_section.go`

### Diff sketch — per-section output folders in dashboard status

```diff
diff --git a/career-ops/dashboard/internal/data/workflow_status.go b/career-ops/dashboard/internal/data/workflow_status.go
@@
   return model.WorkflowSectionStatus{
     Section:      section,
     Availability: availability,
     Summary:      summary,
     Source:       "output/*.pdf + output/*.html",
     Items:        items,
-    Notes:        notes,
+    Notes: append(notes,
+      "Output folder: output/ (later compatible with output/pdf/ and output/html/).",
+      "Shows recent generated item names, not just counts.",
+    ),
   }
```

### Diff sketch — recent item names

```diff
diff --git a/career-ops/dashboard/internal/data/workflow_status.go b/career-ops/dashboard/internal/data/workflow_status.go
@@
   if len(pdfFiles) > 0 {
     availability = "available"
     summary = fmt.Sprintf("Detected %d generated PDF(s).", len(pdfFiles))
     items = append(items, model.WorkflowStatusItem{Label: "Latest PDF", Value: latestFileInfo(pdfFiles)})
+    items = append(items, model.WorkflowStatusItem{Label: "Recent PDFs", Value: recentBaseNames(pdfFiles, 3)})
   }
```

Equivalent pattern for:

- Deep: recent deep report names
- Apply: recent apply-draft names or latest actionable company/role rows
- Pipeline: keep existing company/role display, but ensure output folder hint points to `reports/evaluations/` once introduced

### Help section additions

Each section in Help should state:

- primary output folder the user actually cares about;
- secondary/internal/debug folder(s) only for investigation;
- short note on whether the section shows counts only, names only, or both.

Example entries:

```text
PDF
- Main outputs: output/*.pdf
- Supporting/debug: output/*.html

Deep
- Main outputs: reports/deep/*.md
- Supporting/debug: jds/*

Pipeline
- Main outputs: reports/evaluations/*.md + data/applications.md
- Supporting/debug: batch/tracker-additions/
```

### Constraint

This visibility improvement must be included in the implementation pass so dashboard sections become more operator-legible without changing workflow logic.

---

## Phase 4 — Separate evaluation, Deep, PDF, and Apply artifacts

### Goal

Stop dashboard sections from looking updated because unrelated workflow artifacts share folders.

### Current collision

Current `workflow_section.go` declares:

```go
PDF:  []string{"output/*.pdf", "reports/*"}
DEEP: []string{"reports/*", "jds/*"}
BATCH: []string{"batch/batch-input.tsv", "batch/batch-state.tsv", "reports/*"}
```

This makes evaluation reports activate PDF/DEEP/BATCH semantics.

### Target artifact contract

| Workflow | New output path | Backward-compatible read? |
|---|---|---|
| Evaluation scoring | `reports/evaluations/*.md` | yes, keep legacy report links valid |
| Deep research | `reports/deep/*.md` | no need to count legacy eval reports |
| PDF final | `output/*.pdf` initially, later `output/pdf/*.pdf` | yes |
| PDF HTML intermediate | `output/*.html` initially, later `output/html/*.html` | yes |
| Apply drafts | `reports/apply/*.md` or `applications/drafts/*.md` | new only |
| Tracker | `data/applications.md` | unchanged |

### Dashboard section source changes

```diff
diff --git a/career-ops/dashboard/internal/model/workflow_section.go b/career-ops/dashboard/internal/model/workflow_section.go
@@
- SourceArtifacts: []string{"data/applications.md", "reports/*"},
+ SourceArtifacts: []string{"data/applications.md", "reports/evaluations/*"},
@@
- SourceArtifacts: []string{"output/*.pdf", "reports/*"},
+ SourceArtifacts: []string{"output/*.pdf", "output/pdf/*.pdf", "output/*.html"},
@@
- SourceArtifacts: []string{"reports/*", "jds/*"},
+ SourceArtifacts: []string{"reports/deep/*", "jds/*"},
@@
- SourceArtifacts: []string{"batch/batch-input.tsv", "batch/batch-state.tsv", "reports/*"},
+ SourceArtifacts: []string{"batch/batch-input.tsv", "batch/batch-state.tsv", "reports/evaluations/*"},
```

### PDF status loader changes

Current loader counts reports. Remove that count or rename it to legacy context and do not use for availability.

```diff
diff --git a/career-ops/dashboard/internal/data/workflow_status.go b/career-ops/dashboard/internal/data/workflow_status.go
@@
 pdfPattern := filepath.Join(careerOpsPath, "output", "*.pdf")
 pdfFiles, _ := filepath.Glob(pdfPattern)
-reportPattern := filepath.Join(careerOpsPath, "reports", "*.md")
-reportFiles, _ := filepath.Glob(reportPattern)
+htmlPattern := filepath.Join(careerOpsPath, "output", "*.html")
+htmlFiles, _ := filepath.Glob(htmlPattern)
@@
 items := []model.WorkflowStatusItem{
   {Label: "PDF files", Value: fmt.Sprintf("%d", len(pdfFiles))},
-  {Label: "Reports", Value: fmt.Sprintf("%d", len(reportFiles))},
+  {Label: "HTML drafts", Value: fmt.Sprintf("%d", len(htmlFiles))},
 }
@@
-Source: "output/*.pdf + reports/*",
+Source: "output/*.pdf + output/*.html",
```

### Deep status loader changes

```diff
diff --git a/career-ops/dashboard/internal/data/workflow_status.go b/career-ops/dashboard/internal/data/workflow_status.go
@@
-reportPattern := filepath.Join(careerOpsPath, "reports", "*.md")
+reportPattern := filepath.Join(careerOpsPath, "reports", "deep", "*.md")
 reports, _ := filepath.Glob(reportPattern)
@@
-summary = fmt.Sprintf("Detected %d report(s) and %d JD file(s).", len(reports), len(jds))
+summary = fmt.Sprintf("Detected %d deep report(s) and %d JD file(s).", len(reports), len(jds))
@@
-"Deep mode has no dedicated dashboard artifact contract.",
-"This section summarizes closest related files (reports and saved JDs).",
+"Deep status counts only reports/deep/* and saved JDs.",
+"Evaluation reports no longer count as Deep workflow outputs.",
```

### Apply status change

Keep current tracker/follow-up read for now, but change wording so it is not interpreted as workflow execution.

Optional new draft folder later:

- `reports/apply/*.md`

First pass should **not** require apply draft folder unless mode docs are updated to write there.

When apply-specific artifacts are introduced, Apply status must show recent draft names/company-role labels, not just counts.

---

## Phase 5 — Update workflow docs to respect gates and new paths

### Files

- `career-ops/modes/pipeline.md`
- `career-ops/modes/auto-pipeline.md`
- `career-ops/modes/oferta.md`
- `career-ops/modes/deep.md`
- `career-ops/modes/pdf.md`
- `career-ops/modes/apply.md`

### Pipeline mode diff sketch

```diff
diff --git a/career-ops/modes/pipeline.md b/career-ops/modes/pipeline.md
@@
-d. **Ejecutar auto-pipeline completo**: Evaluación A-F → Report .md → PDF (si score >= 3.0) → Tracker
+d. **Ejecutar evaluación**: Evaluación A-G → `reports/evaluations/{NUM}-{slug}-{date}.md` → Tracker
+e. **Generar PDF solo si score >= `workflow_gates.auto_pdf_min_score`** en `config/workflow.yml`.
+f. **No contar reportes de evaluación como Deep**; Deep usa `/career-ops deep` y escribe `reports/deep/`.
-e. **Mover de "Pendientes" a "Procesadas"**
+g. **Mover de "Pendientes" a "Procesadas"**
```

### Auto-pipeline diff sketch

```diff
diff --git a/career-ops/modes/auto-pipeline.md b/career-ops/modes/auto-pipeline.md
@@
-## Paso 2 — Guardar Report .md
-Guardar la evaluación completa en `reports/{###}-{company-slug}-{YYYY-MM-DD}.md`
+## Paso 2 — Guardar Evaluation Report .md
+Guardar la evaluación completa en `reports/evaluations/{###}-{company-slug}-{YYYY-MM-DD}.md`
@@
-## Paso 3 — Generar PDF
-Ejecutar el pipeline completo de `pdf` (leer `modes/pdf.md`).
+## Paso 3 — Generar PDF condicional
+Solo ejecutar `pdf` si el score final es >= `workflow_gates.auto_pdf_min_score` en `config/workflow.yml`.
@@
-## Paso 4 — Draft Application Answers (solo si score >= 4.5)
+## Paso 4 — Draft Application Answers (solo si score >= `workflow_gates.apply_ready_min_score`)
```

### Deep mode update

Deep should read evaluation reports as input but write separate deep artifacts.

```diff
diff --git a/career-ops/modes/deep.md b/career-ops/modes/deep.md
@@
+## Artifact contract
+- Input: JD URL/text, optional `reports/evaluations/{NUM}-{slug}.md`
+- Output: `reports/deep/{NUM}-{company-slug}-{YYYY-MM-DD}.md`
+- Deep reports are separate from evaluation reports and are the only reports counted by the DEEP dashboard section.
```

### PDF mode update

```diff
diff --git a/career-ops/modes/pdf.md b/career-ops/modes/pdf.md
@@
+## Gate
+Automatic PDF generation during pipeline requires score >= `workflow_gates.auto_pdf_min_score`.
+Manual `/career-ops pdf` may still be run for lower-scoring roles if the user explicitly requests it.
```

---

## Phase 6 — Optional unification of discovery command surface

### Do not do this first

Merging command surfaces has larger blast radius than ranking/dashboard truth fixes.

Recommended after Phases 1-5 are stable:

1. keep `npm run scan` working exactly as it does today;
2. add a new explicit script, e.g. `npm run discover:all`, for ATS + JobSpy + feeds;
3. later point `/career-ops scan` to `discover:all` if tests pass.

### Suggested wrapper

New file later:

- `career-ops/discover-all.mjs`

Responsibilities:

```text
1. Run career-ops scan lane or parent pipeline wrapper.
2. Ensure external_jobs.json exists.
3. Run import:external.
4. Run rank.
5. Print concise summary: Results count, Queue count, top 10 ranked jobs.
```

For now, avoid replacing `scan.mjs` wholesale.

---

## Phase 7 — Validation plan

### Unit-like script validation

1. Parse YAML:

```bash
python -c "import yaml, pathlib; [yaml.safe_load(pathlib.Path(f).read_text(encoding='utf-8')) for f in ['career-ops/config/workflow.yml','career-ops/config/profile.yml','career-ops/portals.yml','config/pipeline.yaml']]"
```

2. Ranking dry run:

```bash
cd career-ops
node rank-queue.mjs --dry-run
```

Expected:

- no file writes;
- printed top 25 before/after;
- printed tier counts;
- exit 0.

3. Ranking write:

```bash
node rank-queue.mjs
```

Expected:

- `data/pipeline.md` still has `## Pendientes` and `## Procesadas`;
- only unprocessed rows reorder;
- processed rows remain preserved;
- `data/queue-ranking.json` exists.

4. Existing checks:

```bash
npm run doctor
npm run sync-check
npm run verify
```

5. Dashboard checks:

```bash
cd career-ops/dashboard
go test ./...
go build ./...
```

### Behavioral validation

1. Open dashboard.
2. Discovery Queue shows best-fit ranked jobs at top.
3. Discovery Results remains raw discovery ledger.
4. PDF section does not become available merely because evaluation reports exist.
5. Deep section does not count evaluation reports.
6. Pipeline still reads `data/pipeline.md` top-down.
7. Track still reads `data/applications.md`.

---

## Rollback plan

If any phase fails:

1. restore touched files from `backup/career_ops_workflow_redesign_20260424/`;
2. remove new files:
   - `career-ops/rank-queue.mjs`
   - `career-ops/config/workflow.yml`
   - `career-ops/data/queue-ranking.json`
3. keep old artifacts untouched:
   - `reports/*.md`
   - `output/*`
   - `jds/*`
   - `data/applications.md`
   - `data/pipeline.md` from backup.

---

## Recommended implementation order

1. Add `config/workflow.yml`.
2. Add `rank-queue.mjs` with dry-run mode.
3. Run ranking dry-run and inspect top 25.
4. Add `npm run rank` / `rank:dry-run`.
5. Wire rank after `scan.mjs` and `import-external-jobs.mjs`, but with non-fatal warnings if rank fails.
6. Add dashboard ranking metadata sidecar read.
7. Fix PDF/Deep dashboard source artifacts.
8. Update mode docs for new paths and thresholds.
9. Only after stable: add unified discovery wrapper.

---

## What not to implement in first pass

- Do not migrate old reports into subfolders automatically.
- Do not change `pipeline.md` into JSON.
- Do not remove `external_jobs.json`.
- Do not rename dashboard tabs yet; add clearer labels/notes first.
- Do not make JobSpy/feed collectors depend on Career-Ops dashboard code.
- Do not add fuzzy ML/embedding matching.
- Do not make ranking a hard reject gate until scores are validated on real results.

---

## Expected outcome after implementation

- `/career-ops scan` still works.
- Parent discovery still works.
- Queue is automatically ranked best-first.
- Existing unprocessed queue entries are re-ranked, not ignored.
- Processed/analyzed entries no longer compete with pending queue order.
- Pipeline can remain top-down because Queue order is meaningful.
- PDF and Deep dashboard sections stop reflecting ordinary evaluation reports.
- PDF/Apply/Deep gating can be changed from one config file.
- The system becomes easier to reason about without a disruptive rewrite.
