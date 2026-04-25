# Career Ops 2.0 - Reviewed Implementation Plan

Status: review draft for approval before implementation

This plan is based on:
- the existing local files in `C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0`
- the earlier research/spec work
- an Oracle review of the actual implementation state
- a Momus plan critique focused on sequencing, verification, and scope control

It replaces the looser earlier planning with a stricter execution order.

## Bottom Line

The current project is only partially working.

What is effectively in place now:
- `feed-fetcher/fetcher.py` exists and has already produced real output
- `dedupe-merge/merger.py` exists and has already produced `data/merged.json`
- `jobspy-wrapper/scrape.py` exists, but live scraping is still unverified
- `career-ops` is cloned and installed, but ATS scan/evaluation wiring is not yet proven

What is currently broken or unreliable:
- `pipeline/run_pipeline.py` references `yaml_safe_load` but does not define/import it
- `pipeline/run_pipeline.py` assumes `career-ops` supports `npm run scan --json --output ...`, which is not proven by the local scanner contract
- the ATS lane is not yet properly exported into `data/ats_raw.json`
- JobSpy defaults are too broad for v1 safety (`linkedin`, `zip_recruiter` should not be default-first)

So the next step is not broad new implementation. It is a surgical correction pass.

## Current State

### Already implemented
- `feed-fetcher/fetcher.py`
- `jobspy-wrapper/scrape.py`
- `dedupe-merge/merger.py`
- `pipeline/run_pipeline.py`
- local `career-ops/` install

### Already validated
- feed lane has produced `data/feeds_raw.json`
- merger has produced `data/merged.json`

### Implemented but not yet validated
- JobSpy lane live run
- ATS scan lane export into shared `data/ats_raw.json`
- full pipeline end-to-end
- merged-output handoff into `career-ops` evaluation

### Known defects
- `pipeline/run_pipeline.py:48` uses `yaml_safe_load`
- `pipeline/run_pipeline.py:67-68` uses an unverified/likely invalid scan invocation
- current `jobspy-wrapper/scrape.py` defaults to higher-risk boards in `boards = ["indeed", "linkedin", "google", "zip_recruiter"]`

## v1 Objective

Build a minimal reliable v1 pipeline with exactly these parts:

1. ATS lane via local `career-ops`
2. Free-feed lane
3. JobSpy lane
4. Merge + dedupe
5. Feed merged output into `career-ops` evaluation

Nothing else is required for v1.

## Non-Goals

These stay out of scope for v1:

- no database
- no Docker
- no custom UI
- no background services beyond simple manual runs
- no optional repo integrations (`ever-jobs`, `stapply-ai`, etc.)
- no advanced proxy rotation system
- no scheduling automation until manual runs are stable
- no changes to `career-ops` core unless a blocker is proven

## Target Architecture

```text
career-ops ATS scan ----\
free feed fetcher -------+--> dedupe/merge --> merged.json --> career-ops eval/match/pdf
JobSpy scrape ----------/
```

Rule:
- each lane writes its own raw JSON
- merge reads raw JSON only
- evaluation consumes merged output only
- one lane failing must not destroy the other two

## Execution Order

## Phase 0 - Contract Baseline

Purpose:
- determine the real local contracts before changing any code

Actions:
1. verify how local `career-ops` scan actually runs
2. verify where local `career-ops` scan actually writes output
3. verify that feed lane still writes valid `data/feeds_raw.json`
4. verify the expected output shape for JobSpy lane

Deliverable:
- a confirmed lane contract for ATS, feeds, and JobSpy

## Phase 1 - Fix Orchestration Only

Purpose:
- repair the broken runner without rewriting working lanes

Actions:
1. remove or fix the dead `load_config()` path in `pipeline/run_pipeline.py`
2. remove the unsupported `npm run scan --json --output ...` assumption
3. make ATS export use the actual local `career-ops` output path/contract
4. keep feed and merge code mostly unchanged
5. keep failure handling explicit, not silent

Deliverable:
- corrected `pipeline/run_pipeline.py`

## Phase 2 - Narrow JobSpy Scope

Purpose:
- maximize probability of a successful first run

Actions:
1. change JobSpy default boards from:
   - `indeed`, `linkedin`, `google`, `zip_recruiter`
   to:
   - `indeed`, `google`
2. keep proxy support optional
3. treat `linkedin` and `zip_recruiter` as post-v1 additions unless proven stable

Deliverable:
- safer default JobSpy lane for v1

## Phase 3 - Validate Each Lane Independently

Purpose:
- prove each lane separately before merging

Actions:
1. ATS lane test
2. feed lane test
3. JobSpy lane test

Deliverable:
- each lane either produces valid JSON or fails with explicit, visible reason

## Phase 4 - Merge and Dedupe Validation

Purpose:
- confirm merge correctness before evaluation handoff

Actions:
1. run merger on all existing raw files
2. verify `data/merged.json` is a valid list
3. verify merged count is sane relative to source counts

Deliverable:
- valid deduped merged job file

## Phase 5 - Career-Ops Evaluation Handoff

Purpose:
- prove the merged output can actually be consumed downstream

Actions:
1. implement the smallest possible adapter if needed
2. copy/import merged jobs into a path `career-ops` evaluation actually reads
3. run one real evaluation handoff

Deliverable:
- one confirmed evaluation path from merged jobs into `career-ops`

## Phase 6 - Repeatability Check

Purpose:
- make sure success is repeatable, not accidental

Actions:
1. run end-to-end twice
2. compare artifact presence and basic counts
3. confirm no silent critical-step failure

Deliverable:
- two consecutive clean runs

## Validation Order (Hard Gates)

The next phase does not start until the current gate passes.

### Gate A - ATS Contract
Pass only if:
- local `career-ops` scan runs successfully
- actual ATS output path/format is identified
- ATS export to `data/ats_raw.json` is possible and valid

### Gate B - Feed Lane
Pass only if:
- `data/feeds_raw.json` exists
- it is valid JSON
- it contains non-zero records

### Gate C - JobSpy Lane
Pass only if:
- `data/jobspy_raw.json` exists
- it is valid JSON
- if it is empty, the reason is explicit and logged

### Gate D - Merge
Pass only if:
- `data/merged.json` exists
- it is valid JSON
- dedupe sanity passes

### Gate E - Evaluation Handoff
Pass only if:
- merged output is accepted by `career-ops` evaluation entrypoint
- at least one real record is processed

### Gate F - Repeatability
Pass only if:
- two consecutive runs complete with the same artifact pattern
- no silent critical failures occur

## Rollback Scope

If a gate fails, rollback only the smallest recent change set.

Editable scope for the first pass:
- `pipeline/run_pipeline.py`
- small new adapter(s) in `pipeline/` if required
- narrow defaults in `jobspy-wrapper/scrape.py`

Avoid touching unless strictly necessary:
- `career-ops/*` core internals
- feed fetcher lane
- merger lane

Rollback order:
1. new adapter files
2. runner changes
3. JobSpy default-board changes

## Concrete Review Points For You

Before I implement anything, you should review and confirm these policy choices:

1. **Strict gate policy**
   - no silent “continue anyway” for critical steps like ATS contract/export and final handoff

2. **v1 scope policy**
   - no extra repos
   - no scheduler yet
   - no DB/UI/Docker

3. **JobSpy safety policy**
   - default-first boards should be `indeed` + `google`
   - `linkedin` + `zip_recruiter` only after stability proof

4. **career-ops core policy**
   - keep `career-ops` mostly untouched unless a real blocker forces a change

## Exact Files Most Likely To Change In The Next Pass

- `C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\pipeline\run_pipeline.py`
- `C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\jobspy-wrapper\scrape.py`
- optional small new file under `C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\pipeline\`

## What Will Not Be Changed In The Next Pass

- `feed-fetcher/fetcher.py` unless validation proves a real bug
- `dedupe-merge/merger.py` unless merge contract validation reveals a real defect
- optional expansion repos
- scheduler automation

## Final Review Summary

This reviewed plan is intentionally narrower than the earlier spec.

The earlier planning overreached in three places:
- it assumed a richer `career-ops` CLI contract than the local files prove
- it treated JobSpy broader-board support as day-one scope
- it blurred “working lanes” with “working end-to-end orchestration”

The corrected plan fixes that by:
- verifying the ATS lane contract first
- repairing only the broken orchestration pieces
- keeping working components intact
- enforcing hard validation gates before implementation proceeds
