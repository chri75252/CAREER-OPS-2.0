# Unified Career-Ops Dashboard Discovery Integration Plan

Date: 2026-04-20
Scope: Surgical extension of existing Go TUI dashboard to show discovery queue/results and keep native applications/progress/report views.

## Current constraints
- `dashboard/main.go` exits if `applications.md` is missing.
- Dashboard currently parses tracker data only (`applications.md`).
- Discovery pipeline already writes:
  - `career-ops/data/pipeline.md`
  - `career-ops/data/external_jobs.json`

## Minimum required fixes

1. `career-ops/dashboard/main.go`
   - make startup tolerant when tracker file is missing
   - add `viewDiscovery` state and routing
   - load discovery dataset and default to discovery view when no tracker data

2. `career-ops/dashboard/internal/data/discovery.go` (new)
   - parse queue rows from `data/pipeline.md`
   - parse discovery records from `data/external_jobs.json`
   - return a unified discovery aggregate

3. `career-ops/dashboard/internal/model/discovery.go` (new)
   - `PendingJob`
   - `ExternalJob`
   - `DiscoveryData`

4. `career-ops/dashboard/internal/ui/screens/discovery.go` (new)
   - queue/results tabs
   - cursor + paging navigation
   - open URL action
   - switch to applications view

5. `career-ops/dashboard/internal/ui/screens/pipeline.go`
   - minimal help text/nav hint to discovery

6. `career-ops/dashboard/internal/ui/screens/progress.go`
   - minimal help text/nav hint to discovery

7. `career-ops/docs/SETUP.md`
   - document discovery-first launch behavior and unified TUI workflow

8. Tests
   - `career-ops/dashboard/internal/data/discovery_test.go` (new)
   - `career-ops/dashboard/internal/ui/screens/discovery_test.go` (new)

## Ordered implementation sequence
1. backup + revert tracking
2. add discovery models
3. add discovery parser
4. add discovery screen
5. wire main startup/routing
6. update nav/help hints
7. add tests
8. update docs
9. run build/tests and manual runtime checks

## Validation sequence
1. `go test ./...` from `career-ops/dashboard`
2. `go build -o career-dashboard.exe .`
3. launch dashboard without `applications.md` and confirm discovery view opens
4. confirm queue tab shows rows from `data/pipeline.md`
5. confirm results tab shows rows from `data/external_jobs.json`
6. confirm tracker mode still launches when `applications.md` exists

## Non-goals
- no browser/localhost UI
- no command-trigger execution from dashboard in this pass
- no changes to pipeline producers or file formats
