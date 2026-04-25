# Revert Tracking — Career-Ops Scan Parity Repair — 2026-04-25

## Scope

Repair the post-`/career-ops-scan` inconsistency where `external_jobs.json` became invalid and queue scores disappeared/staled. Make scan slash commands route to the tested unified discovery workflow, restore a valid Results ledger, regenerate queue ranking, bottom `[x]` entries, and improve dashboard artifact-name visibility.

## Backups

| Original file | Backup file | Planned change | Validation |
|---|---|---|---|
| `career-ops/data/external_jobs.json` | `backup/career_ops_scan_parity_20260425/external_jobs.json.bak` | Restore valid Results ledger from parent `data/merged.json` | JSON parse + dashboard Results |
| `career-ops/data/queue-ranking.json` | `backup/career_ops_scan_parity_20260425/queue-ranking.json.bak` | Regenerate with `npm run rank` | JSON parse + Queue scores |
| `career-ops/data/pipeline.md` | `backup/career_ops_scan_parity_20260425/pipeline.md.bak` | Reorder pending entries and bottom `[x]` entries | inspect section order |
| `career-ops/rank-queue.mjs` | `backup/career_ops_scan_parity_20260425/rank-queue.mjs.bak` | Preserve done entries at bottom | rank dry-run/write |
| `career-ops/config/workflow.yml` | `backup/career_ops_scan_parity_20260425/workflow.yml.bak` | Add explicit title patterns | YAML parse + score sanity |
| `.opencode/commands/career-ops-scan.md` | `backup/career_ops_scan_parity_20260425/parent-career-ops-scan.md.bak` | Route slash scan to unified discover | command file read |
| `career-ops/.opencode/commands/career-ops-scan.md` | `backup/career_ops_scan_parity_20260425/nested-career-ops-scan.md.bak` | Route nested slash scan to unified discover | command file read |
| `career-ops/.claude/skills/career-ops/SKILL.md` | `backup/career_ops_scan_parity_20260425/career-ops-SKILL.md.bak` | Clarify scan/rank routing | command file read |
| `career-ops/dashboard/internal/data/workflow_status.go` | `backup/career_ops_scan_parity_20260425/workflow_status.go.bak` | More artifact names + report path fix | `go test ./...` |
| `career-ops/dashboard/internal/ui/screens/help.go` | `backup/career_ops_scan_parity_20260425/help.go.bak` | Fix stale report path text | `go test ./...` |
| `career-ops/dashboard/internal/ui/screens/pipeline.go` | `backup/career_ops_scan_parity_20260425/pipeline.go.bak` | Fix stale source label | `go test ./...` |

## Restore commands

Run from repo parent root:

```bat
copy backup\career_ops_scan_parity_20260425\external_jobs.json.bak career-ops\data\external_jobs.json
copy backup\career_ops_scan_parity_20260425\queue-ranking.json.bak career-ops\data\queue-ranking.json
copy backup\career_ops_scan_parity_20260425\pipeline.md.bak career-ops\data\pipeline.md
copy backup\career_ops_scan_parity_20260425\rank-queue.mjs.bak career-ops\rank-queue.mjs
copy backup\career_ops_scan_parity_20260425\workflow.yml.bak career-ops\config\workflow.yml
copy backup\career_ops_scan_parity_20260425\parent-career-ops-scan.md.bak .opencode\commands\career-ops-scan.md
copy backup\career_ops_scan_parity_20260425\nested-career-ops-scan.md.bak career-ops\.opencode\commands\career-ops-scan.md
copy backup\career_ops_scan_parity_20260425\career-ops-SKILL.md.bak career-ops\.claude\skills\career-ops\SKILL.md
copy backup\career_ops_scan_parity_20260425\workflow_status.go.bak career-ops\dashboard\internal\data\workflow_status.go
copy backup\career_ops_scan_parity_20260425\help.go.bak career-ops\dashboard\internal\ui\screens\help.go
copy backup\career_ops_scan_parity_20260425\pipeline.go.bak career-ops\dashboard\internal\ui\screens\pipeline.go
```

## Validation results

- `external_jobs.json` restored from parent `data/merged.json` and JSON-validated: 1091 jobs.
- `npm run rank:dry-run`: passed; 2262 pending entries analyzed; top ranked roles now score as `primary` after title-pattern config.
- `npm run rank`: passed; regenerated `data/queue-ranking.json`; moved `[x]` entries to bottom of `## Pendientes` while preserving them.
- `npm run doctor`: passed.
- `npm run sync-check`: passed.
- `npm run verify`: passed, 0 errors/0 warnings.
- `npm run discover:dry-run`: passed; Results ledger count 1091; ranking dry-run executed.
- `npm run discover:rank`: passed; import idempotent, ranking regenerated.
- Dashboard `go test ./...`: passed.
- Dashboard `go build -o career-dashboard.exe .`: passed.
