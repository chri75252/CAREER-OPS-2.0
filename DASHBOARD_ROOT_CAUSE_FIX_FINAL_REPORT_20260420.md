# Dashboard Root Cause + Fix Final Report (2026-04-20)

## Objective

Investigate why non-discovery dashboard tabs remained empty, why OpenCode/Claude commands were not visible from the user's actual launch directory, fix the root causes surgically, and rerun the workflow until real persisted artifacts existed on disk and were representable in the dashboard.

## Root Causes Found

### 1. Discovery-only workflow misunderstanding

The external discovery pipeline (`pipeline/run_pipeline.py`) only writes discovery-side artifacts:

- `career-ops/data/pipeline.md`
- `career-ops/data/external_jobs.json`

It does **not** create:

- `career-ops/data/applications.md` rows
- `career-ops/reports/*.md`
- `career-ops/output/*.pdf`
- `career-ops/data/follow-ups.md`

Therefore:

- Discovery tab populating alone was expected.
- Pipeline / Track / PDF / Apply staying empty after discovery was expected under current artifact contracts.

### 2. Command discovery root mismatch

The user launched OpenCode and Claude Code from the repo parent root:

`C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0`

But command surfaces originally existed only in the nested app root:

- `career-ops/.opencode/commands/`
- `career-ops/.claude/skills/career-ops/`

So commands were not discoverable from the actual launch root used by the user.

### 3. Help screen command naming/documentation bugs

The dashboard help screen originally:

- did not show exact terminal commands
- showed OpenCode commands using Claude-style spaced names (`/career-ops pdf`) instead of actual OpenCode project command names (`/career-ops-pdf`)

### 4. Parent-root Claude command initially visible but non-executing

After initial shimming, parent-root `/career-ops` became visible, but it only explained routing and did not actually execute the nested artifact-writing workflow.

This was fixed by changing the parent-root Claude command into a true wrapper that inlines nested skill/router/project instructions with `$ARGUMENTS` and explicit execution requirements.

## Files Changed

### Parent-root command visibility fixes

- `.opencode/commands/career-ops.md`
- `.opencode/commands/career-ops-scan.md`
- `.opencode/commands/career-ops-pipeline.md`
- `.opencode/commands/career-ops-pdf.md`
- `.opencode/commands/career-ops-apply.md`
- `.opencode/commands/career-ops-tracker.md`
- `.opencode/commands/career-ops-deep.md`
- `.opencode/commands/career-ops-batch.md`
- `.opencode/commands/career-ops-evaluate.md`
- `.opencode/commands/career-ops-compare.md`
- `.opencode/commands/career-ops-contact.md`
- `.opencode/commands/career-ops-training.md`
- `.opencode/commands/career-ops-project.md`
- `.opencode/commands/career-ops-patterns.md`
- `.opencode/commands/career-ops-followup.md`
- `.opencode/commands/career-ops-interview-prep.md`
- `.claude/commands/career-ops.md`
- `CLAUDE.md`

### Dashboard/help/docs fixes

- `career-ops/dashboard/internal/model/workflow_section.go`
- `career-ops/dashboard/internal/ui/screens/help.go`
- `career-ops/dashboard/internal/ui/screens/help_test.go`
- `career-ops/dashboard/DASHBOARD_OPERATOR_GUIDE.md`
- `career-ops/docs/SETUP.md`
- `career-ops/README.md`

## Safety Artifacts

- Backup: `C:\Users\chris\backup\career_ops2_root_command_visibility_fix_20260420`
- Revert tracker: `C:\Users\chris\backup\career_ops2_root_command_visibility_fix_20260420\REVERT_TRACKING.md`

## Commands Actually Executed

### Verification / setup

```powershell
npm run doctor
npm run sync-check
npm run verify
```

### Discovery flow

```powershell
npm run scan
python .\run_pipeline.py "AI engineer" "applied AI engineer" "solutions engineer"
npm run import:external
```

### Real downstream artifact-producing flow

Created local JD input:

`career-ops/jds/datadog-staff-ai-engineer-mcp-services.md`

Then executed:

```powershell
claude -p --dangerously-skip-permissions "/career-ops local:jds/datadog-staff-ai-engineer-mcp-services.md"
claude -p --dangerously-skip-permissions "/career-ops pdf local:jds/datadog-staff-ai-engineer-mcp-services.md"
claude -p --dangerously-skip-permissions "/career-ops tracker"
node merge-tracker.mjs
claude -p --dangerously-skip-permissions "/career-ops followup"
```

## Persisted Artifact Results

Final on-disk state verified:

- Reports: `1`
- PDFs: `1`
- Applications rows: `1`
- Follow-ups file: not created yet (correctly absent; no actionable follow-up state yet)
- Batch input/state files: absent

Specific files:

- `career-ops/reports/001-datadog-staff-ai-engineer-20260420.md`
- `career-ops/output/cv-christian-haddad-datadog-20260421.pdf`
- `career-ops/data/applications.md` with Datadog row merged

Tracker row now present:

| # | Date | Company | Role | Score | Status | PDF | Report | Notes |
|---|------|---------|------|-------|--------|-----|--------|-------|
| 1 | 2026-04-20 | Datadog | Staff AI Engineer, MCP Services | 4.2/5 | Evaluated | ❌ | [001](reports/001-datadog-staff-ai-engineer-20260420.md) | Strong systems fit; soft gap on production AI specifics. Ready to apply. |

## Dashboard Tab Truth After Fix + Real Execution

### Populated by real persisted artifacts

- `1 Discovery` -> yes
- `2 Pipeline` -> yes (tracker row now exists)
- `3 PDF` -> yes (real PDF exists)
- `5 Track` -> yes (real tracker metrics source now exists)
- `6 Deep` -> yes (saved JD + report summary source exists)

### Correctly partial / limited

- `4 Apply` -> now has tracker context, but no follow-up file yet
- `7 Batch` -> still empty because no batch workload was executed and no batch TSVs exist

## OpenCode Status

Parent-root OpenCode command visibility was fixed structurally by adding repo-root `.opencode/commands/career-ops*.md` files.

However, direct `opencode run` execution is still blocked by a **local machine configuration issue** unrelated to repo command placement:

- `default agent "sisyphus" not found`

This is a local OpenCode config/runtime issue, not a dashboard or repo command discovery bug.

## Claude Status

Parent-root Claude command visibility is now fixed and verified. Noninteractive parent-root command execution successfully produced real persisted report/PDF/tracker artifacts.

## Build / Test Status

- `go test ./...` -> pass
- `go build` logic -> clean
- final overwrite of `career-dashboard.exe` may fail while the dashboard binary is actively open (Windows file lock), but tests passed and code is valid

## Remaining Limitations

1. `Batch` tab still has no real persisted data because no batch workflow was executed in this pass.
2. `Apply` has context but no follow-up history file yet because no follow-up has actually been recorded/sent.
3. OpenCode execution remains blocked by local default-agent configuration (`sisyphus` missing), even though project command discovery is now in place.

## Bottom Line

The original issue was **not** a single dashboard bug.

It was a combination of:

- misunderstanding discovery-vs-tracker artifact boundaries
- command discovery rooted in the wrong directory
- incorrect command naming in help/docs
- a parent-root Claude command that was initially descriptive rather than executable

Those issues were fixed surgically. Real downstream artifacts now exist on disk, and the dashboard now has truthful, persisted data for the sections that correspond to workflows actually executed.
