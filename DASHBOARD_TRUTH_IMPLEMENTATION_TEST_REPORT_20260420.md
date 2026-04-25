# Dashboard Truth Sections - Implementation + Testing Report (2026-04-20)

## 1) Objective

Implement the approved surgical pass so the dashboard reflects section-relevant truth across all workflow bar sections (`1..7`) without adding in-dashboard workflow launchers, then execute testing up to command/compile/test evidence.

## 2) Safety + Continuity Artifacts

- Backup root: `C:\Users\chris\backup\career_ops2_dashboard_truth_sections_20260420`
- Revert tracking: `C:\Users\chris\backup\career_ops2_dashboard_truth_sections_20260420\REVERT_TRACKING.md`
- Persisted plan: `.sisyphus/plans/dashboard_truth_sections_implementation_20260420.md`

## 3) Implemented Changes

### New files

- `career-ops/dashboard/internal/model/workflow_section.go`
- `career-ops/dashboard/internal/data/workflow_status.go`
- `career-ops/dashboard/internal/ui/screens/workflow_status.go`
- `career-ops/dashboard/internal/data/workflow_status_test.go`
- `career-ops/dashboard/main_test.go`
- `career-ops/dashboard/internal/ui/screens/help_test.go`
- `career-ops/dashboard/internal/ui/screens/workflow_status_test.go`

### Updated files

- `career-ops/dashboard/main.go`
- `career-ops/dashboard/internal/ui/screens/help.go`
- `career-ops/dashboard/internal/ui/screens/discovery.go`
- `career-ops/dashboard/internal/ui/screens/pipeline.go`
- `career-ops/dashboard/internal/ui/screens/progress.go`
- `career-ops/dashboard/internal/ui/screens/viewer.go`
- `career-ops/dashboard/DASHBOARD_OPERATOR_GUIDE.md`
- `career-ops/docs/SETUP.md`

### What changed functionally

1. Added one workflow section registry with capabilities, command mapping, and source artifacts.
2. Replaced `3/4/6/7 -> Help` routing with dedicated workflow status screens.
3. Added artifact summary loaders for PDF/APPLY/DEEP/BATCH sections.
4. Added source/status labeling and explicit empty-state reasoning in core screens.
5. Reworked help/setup/operator docs to OpenCode-first, runner-neutral wording.

## 4) Verification Results (Implementation Phase)

Executed in `career-ops/dashboard`:

- `gofmt -w ...` on changed Go files
- `go test ./...`
- `go build -o career-dashboard.exe .`

Result: **PASS**

Notes:
- Go LSP diagnostics were unavailable in this environment (`gopls` not installed).

## 5) Command/Feature Test Matrix Executed

Executed in `career-ops`:

1. `npm run doctor` -> **PASS**
2. `npm run sync-check` -> **PASS**
3. `npm run verify` -> **PASS**
4. `npm run scan` -> **PASS** (0 new offers this run, duplicate-filter dominated)
5. `python pipeline/run_pipeline.py "AI engineer" "applied AI engineer" "solutions engineer"` -> **PASS**
6. `npm run import:external` -> **PASS** (`No new external jobs to import` on second run, dedupe behavior confirmed)

## 6) Artifact Outcomes After Test Run

Collected artifact summary after the command matrix:

- `feeds_raw`: 3
- `jobspy_raw`: 138
- `ats_raw`: 0
- `merged`: 141
- `external_jobs`: 141
- `latest_pipeline_output`: `pipeline_output_20260420_200431.json`
- `pipeline_pending`: 1074
- `pipeline_done`: 0
- `applications_rows`: 0
- `reports`: 0
- `pdfs`: 0
- `batch_input_exists`: false
- `batch_state_exists`: false

Interpretation:

- Discovery artifacts are populated and should render in section `1`.
- Tracker artifacts remain empty (`applications_rows=0`), so sections `2` and `5` correctly show tracker-empty states.
- PDF/APPLY/DEEP/BATCH sections now have dedicated status rendering and should reflect missing/available artifacts truthfully rather than routing to static Help.

## 7) OpenCode Command Execution Check

Checks performed:

- `opencode --help` -> available
- `opencode agent list` -> available
- `opencode run "/career-ops"` in repo root -> failed with config error:
  - `default agent "sisyphus" not found`

Conclusion:

- Command files exist under `career-ops/.opencode/commands/` and docs were aligned to OpenCode-first.
- In this shell execution context, direct `opencode run` slash invocation is blocked by local OpenCode default-agent config mismatch, not by dashboard code.

## 8) Automated UI Behavior Coverage Added

New/updated tests now verify:

- workflow key routing to dedicated screens (`3/4/6/7`) in `career-ops/dashboard/main_test.go`
- primary key routing for `1/2/5/?` in `career-ops/dashboard/main_test.go`
- help wording guard (`OpenCode` presence and removal of `claude ->` phrasing) in `career-ops/dashboard/internal/ui/screens/help_test.go`
- workflow status screen rendering of summary/source/items/notes in `career-ops/dashboard/internal/ui/screens/workflow_status_test.go`
- workflow status data loading for PDF/APPLY/BATCH in `career-ops/dashboard/internal/data/workflow_status_test.go`

## 9) Expected Dashboard Behavior Now

- `1 Discovery`: reflects `data/pipeline.md` + `data/external_jobs.json`
- `2 Pipeline`: reflects `data/applications.md` + `reports/*`
- `3 PDF`: dedicated status summary from `output/*.pdf` (+ reports context)
- `4 Apply`: dedicated status summary from tracker/follow-up artifacts
- `5 Track`: progress analytics from tracker artifacts
- `6 Deep`: dedicated status summary from `reports/*` + `jds/*`
- `7 Batch`: dedicated status summary from batch input/state/report artifacts
- `? Help`: truthful capability + command + source mapping (OpenCode-first)

## 10) Remaining Items Deferred to Next Phase

Not executed in this pass:

1. Full interactive/manual section-by-section runtime walkthrough screenshots inside TUI (`1..7` + refresh cycles) after each external command step.
2. Full OpenCode slash-command execution validation until local OpenCode default-agent mismatch (`sisyphus`) is fixed.

## 11) Status

Implementation requested in this phase is complete.
Testing up to compile/unit/command evidence is complete.
The dashboard now has section-truth reflection for all workflow bar sections, with explicit source and empty-state reasoning.
