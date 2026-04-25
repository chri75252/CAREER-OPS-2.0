# Dashboard Truth Sections Implementation Plan (2026-04-20)

## Objective
Make all seven workflow-bar sections in the dashboard reflect truthful, section-relevant information from existing artifacts, without adding in-dashboard workflow execution.

## Scope
- Replace `3/4/6/7 -> Help` routing with dedicated status screens.
- Add a single workflow section registry for bar/help/routing consistency.
- Keep discovery/tracker file contracts unchanged.
- Add explicit source/status labeling and truthful empty-state reasons.
- Align dashboard/operator/setup docs to OpenCode-first, runner-neutral wording.

## Non-Goals
- No in-dashboard command launchers in this pass.
- No unification of discovery storage and tracker storage.
- No artifact format changes unless reader correctness requires it.

## Edit Order
1. Add model registry types for workflow sections.
2. Add data summarizer for section status (PDF/APPLY/DEEP/BATCH).
3. Add reusable workflow-status screen.
4. Wire `dashboard/main.go` routing and workflow bar state.
5. Add source/status labels to discovery/pipeline/progress/viewer/help.
6. Update `dashboard/DASHBOARD_OPERATOR_GUIDE.md` and `docs/SETUP.md`.

## Verification Order (implementation phase)
1. `gofmt` changed Go files.
2. `go test ./...` in `career-ops/dashboard`.
3. `go build -o career-dashboard.exe .` in `career-ops/dashboard`.

## Full Testing Matrix (next phase, not yet executed)
1. Fixture states: discovery-only / tracker-only / both / neither.
2. Section rendering checks for keys `1..7` and `?`.
3. Artifact reflection checks after command runs:
   - `npm run doctor`
   - `npm run sync-check`
   - `npm run verify`
   - `npm run scan`
   - `python pipeline/run_pipeline.py ...`
   - `npm run import:external`
   - OpenCode commands: `/career-ops scan|pipeline|tracker|pdf|apply|deep|batch`
4. Report expected vs actual in a final validation report.
