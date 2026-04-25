# Revert Tracking - Career-Ops workflow redesign implementation - 2026-04-24

## Scope

Implement surgical pass for ranking, queue ordering, and dashboard artifact clarity.

## Files planned for edit

| File | Change scope | Backup path | Validation |
|---|---|---|---|
| `career-ops/package.json` | add rank scripts | `backup/career_ops_workflow_redesign_20260424/package.json.bak` | npm scripts list |
| `career-ops/scan.mjs` | trigger rank post-scan (non-fatal) | `backup/career_ops_workflow_redesign_20260424/scan.mjs.bak` | scan dry-run and normal run |
| `career-ops/import-external-jobs.mjs` | trigger rank post-import (non-fatal) | `backup/career_ops_workflow_redesign_20260424/import-external-jobs.mjs.bak` | import run |
| `career-ops/dashboard/internal/model/discovery.go` | optional ranking metadata fields | `backup/career_ops_workflow_redesign_20260424/discovery.model.go.bak` | go test |
| `career-ops/dashboard/internal/data/discovery.go` | read queue ranking sidecar | `backup/career_ops_workflow_redesign_20260424/discovery.data.go.bak` | go test |
| `career-ops/dashboard/internal/ui/screens/discovery.go` | render queue rank prefix and results hints | `backup/career_ops_workflow_redesign_20260424/discovery.screen.go.bak` | go test/manual view |
| `career-ops/dashboard/internal/model/workflow_section.go` | clarify section source artifacts for PDF/APPLY/DEEP | `backup/career_ops_workflow_redesign_20260424/workflow_section.go.bak` | go test/manual view |
| `career-ops/dashboard/internal/data/workflow_status.go` | improve section source, names, output folder hints | `backup/career_ops_workflow_redesign_20260424/workflow_status.go.bak` | go test/manual view |
| `career-ops/dashboard/internal/ui/screens/help.go` | add output folder guidance by section | `backup/career_ops_workflow_redesign_20260424/help.go.bak` | go test/manual view |
| `career-ops/config/workflow.yml` | new workflow gates + ranking config | n/a (new file) | yaml parse |
| `career-ops/rank-queue.mjs` | new deterministic queue ranking | n/a (new file) | rank dry-run/write |
| `career-ops/discover-all.mjs` | new unified discovery wrapper | n/a (new file) | npm run discover:dry-run |
| `career-ops/modes/pipeline.md` | evaluation path + gate references | `backup/career_ops_workflow_redesign_20260424/pipeline.md.bak` | agent mode read |
| `career-ops/modes/auto-pipeline.md` | conditional PDF + gate references | `backup/career_ops_workflow_redesign_20260424/auto-pipeline.md.bak` | agent mode read |
| `career-ops/modes/oferta.md` | reports/evaluations/ path | `backup/career_ops_workflow_redesign_20260424/oferta.md.bak` | agent mode read |
| `career-ops/modes/deep.md` | artifact contract section | `backup/career_ops_workflow_redesign_20260424/deep.md.bak` | agent mode read |
| `career-ops/modes/pdf.md` | gate section | `backup/career_ops_workflow_redesign_20260424/pdf.md.bak` | agent mode read |
| `career-ops/modes/apply.md` | gate section + path updates | `backup/career_ops_workflow_redesign_20260424/apply.md.bak` | agent mode read |

## Notes

- Keep `data/pipeline.md` format unchanged (`- [ ] URL | Company | Title`).
- Ranking must never block scan/import primary writes.
- No destructive migration of existing reports/output paths in this pass.

## Validation run result

- Completed on 2026-04-24: `npm run doctor`, `npm run sync-check`, `npm run verify`, `npm run rank:dry-run`, `npm run rank`, `go test ./...` (dashboard), and workflow YAML parse check.
- Completed on 2026-04-24 (pass 2): All above re-verified after Phase 4-6 changes. Added `npm run discover:dry-run`, `npm run discover:rank`, dashboard build, `verify-pipeline.mjs` report path fallback check.
- Phase 1-6 all passing. No regressions detected.
