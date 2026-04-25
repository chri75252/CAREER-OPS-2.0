# Revert Tracking — Career-Ops workflow redesign implementation plan — 2026-04-24

## Scope

This backup note covers the planning pass only. No source-code implementation was applied by this plan.

## Files created in this planning pass

| File | Scope | Revert action |
|---|---|---|
| `.sisyphus/plans/career_ops_workflow_redesign_implementation_plan_20260424.md` | Surgical implementation plan with snippets/diffs | Delete file if reverting planning docs |
| `backup/career_ops_workflow_redesign_plan_20260424/REVERT_TRACKING.md` | Planning-pass revert note | Delete backup folder if reverting planning docs |

## Future implementation pass backup requirement

Before applying any code changes from the plan, create:

- `backup/career_ops_workflow_redesign_20260424/`

and copy every touched file there before editing.

## Planned high-risk files for future backup

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
