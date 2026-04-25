# Career Ops 2.0 - Test Run Workflow

This file explains how to test the created tool using the currently available placeholder / outdated CV material so you can verify that the technical workflow is functioning correctly before replacing the inputs with final real data.

## What Was Already Installed / Implemented

### Installed
- `career-ops` repository cloned locally
- `career-ops` npm dependencies installed
- `jobspy` Python package installed, but it turned out to be the wrong package for this scraping workflow
- Python dependencies for feed ingestion installed:
  - `requests`
  - `feedparser`
  - `xmltodict`

### Implemented
- `feed-fetcher/fetcher.py`
- `jobspy-wrapper/scrape.py`
- `dedupe-merge/merger.py`
- `pipeline/run_pipeline.py`
- `pipeline/export_ats_lane.mjs`
- `pipeline/ingest_to_career_ops.py`
- ATS-compatible local `career-ops/portals.yml`
- reviewed planning documents

### Verified after the surgical pass
- feed lane works
- ATS export lane works
- merge/dedupe works
- merged-output handoff into `career-ops/data/external_jobs.json` works
- full pipeline now runs successfully end-to-end

### Important current limitation
The pipeline now restores the JobSpy lane using `python-jobspy`, but the overall workflow still stops at discovery, merge, handoff, and queue import.

That means this tool now automates:
- ATS lane
- free-feed lane
- board-scraping lane
- merge layer
- career-ops handoff
- import into `career-ops/data/pipeline.md`

It still does **not** complete downstream evaluation, tailored PDF generation, or tracker/report generation automatically. Those continue inside the separate Career-Ops workflow.

---

## Current Working Architecture

```text
career-ops ATS scan ----\
free feed fetcher -------+--> dedupe/merge --> merged.json --> ingest_to_career_ops --> career-ops/data/external_jobs.json
JobSpy board scraper -----/
```

## What Each Part Does

### 1. ATS lane
Source:
- local `career-ops` scanner

Purpose:
- fetch jobs from API-detectable companies (Greenhouse/Ashby/Lever)

Current state:
- working

Output:
- `data/ats_raw.json`

### 2. Free-feed lane
Sources:
- RemoteOK
- Remotive
- Arbeitnow
- We Work Remotely
- Jobicy
- Python.org jobs feed

Purpose:
- stable no-auth external job discovery

Current state:
- working

Output:
- `data/feeds_raw.json`

### 3. JobSpy lane
Purpose:
- intended board scraping expansion layer

Current state:
- active via `python-jobspy`
- still fails safely by writing valid JSON output if a board blocks requests or the scrape fails

Output:
- `data/jobspy_raw.json`

### 4. Merge / dedupe layer
Purpose:
- combine ATS + feeds + JobSpy outputs
- remove duplicates

Current state:
- working

Output:
- `data/merged.json`

### 5. Pipeline snapshot output
Purpose:
- preserve a timestamped record of a completed run

Output:
- `data/pipeline_output_YYYYMMDD_HHMMSS.json`

### 6. Career-ops ingestion handoff
Purpose:
- feed merged jobs into the local career-ops workspace for downstream evaluation

Output:
- `career-ops/data/external_jobs.json`

---

## What You Need To Provide

For a technical workflow test of the full reachable workflow, you need:

### Required inputs
1. `career-ops/config/profile.yml`
   - this is the real runtime profile path Career-Ops expects
2. `career-ops/cv.md`
   - required for true evaluation/PDF readiness inside Career-Ops
3. `career-ops/portals.yml`
    - already adjusted to ATS-detectable companies for this test pass
4. keywords you want to test with, or defaults from `config/pipeline.yaml`

### Optional inputs
5. article/proof-point digest later
6. real target companies later
7. proxies later if board scraping needs more resilience

---

## The Correct Test Workflow (Sequence)

Follow these in order.

## Step 1 - Verify ATS lane directly

Run:

```bash
cd "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\career-ops"
npm run scan
```

### What this step does
- scans companies from `career-ops/portals.yml`
- detects API-backed companies
- writes/updates career-ops internal scan files

### Expected output
- console scan summary
- new entries in `career-ops/data/pipeline.md`
- new entries in `career-ops/data/scan-history.tsv`

### What to monitor
- how many companies scanned
- how many skipped
- how many new offers added

### Pass condition
- command completes successfully

---

## Step 2 - Verify free-feed lane directly

Run:

```bash
cd "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\feed-fetcher"
python fetcher.py "software engineer" "data engineer"
```

### What this step does
- queries the public feed sources
- normalizes results
- dedupes feed-only results

### Expected output file
- `data/feeds_raw.json`

### What to monitor
- count per source
- total deduped count

### Pass condition
- file exists
- valid JSON
- non-zero jobs

---

## Step 3 - Verify JobSpy lane directly

Run:

```bash
cd "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\jobspy-wrapper"
python scrape.py "software engineer" "data engineer"
```

### What this step currently does
- uses `python-jobspy` to query supported boards
- normalizes returned jobs into pipeline format
- still writes a valid `data/jobspy_raw.json` even when all boards return zero jobs or a scrape fails

### Expected output file
- `data/jobspy_raw.json`

### What to monitor
- file creation
- successful import of the JobSpy library
- number of kept jobs per keyword
- graceful fallback if a site blocks or errors

### Pass condition
- no crash
- valid JSON file written
- either non-zero jobs or explicit safe fallback logging

---

## Step 4 - Run the full pipeline

Run:

```bash
cd "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\pipeline"
"C:\Python313\python.exe" run_pipeline.py "software engineer" "data engineer"
```

### What this step does
In order, it:

1. runs feed fetcher
2. runs JobSpy fallback lane
3. runs ATS export adapter
4. runs merge + dedupe
5. ingests merged jobs into `career-ops/data/external_jobs.json`
6. imports external jobs into `career-ops/data/pipeline.md`
7. writes timestamped snapshot output

### Expected outputs
- `data/feeds_raw.json`
- `data/jobspy_raw.json`
- `data/ats_raw.json`
- `data/merged.json`
- `data/pipeline_output_YYYYMMDD_HHMMSS.json`
- `career-ops/data/external_jobs.json`
- `career-ops/data/pipeline.md`

### What to monitor
- lane counts shown in terminal
- final unique job count
- snapshot filename

### Pass condition
- pipeline completes without crashing
- all expected files exist

---

## Step 5 - Review the outputs in order

### A. Review ATS-only results
File:
- `data/ats_raw.json`

Expected info:
- ATS-sourced jobs only

### B. Review feed-only results
File:
- `data/feeds_raw.json`

Expected info:
- free-feed jobs only

### C. Review JobSpy lane output
File:
- `data/jobspy_raw.json`

Expected info:
- currently empty fallback-safe file

### D. Review merged pool
File:
- `data/merged.json`

Expected info:
- all successful lane outputs merged
- deduplicated job pool

### E. Review timestamped final snapshot
File:
- `data/pipeline_output_YYYYMMDD_HHMMSS.json`

Expected info:
- archival copy of the merged output from that exact run

### F. Review career-ops handoff file
File:
- `career-ops/data/external_jobs.json`

Expected info:
- merged jobs available for downstream career-ops use

### G. Review career-ops pending queue
File:
- `career-ops/data/pipeline.md`

Expected info:
- imported jobs appended as pending checklist lines
- dedupe-safe repeated imports

---

## What the Final Output Currently Is

The main final technical output of the created tool is:

- `data/pipeline_output_YYYYMMDD_HHMMSS.json`

and the downstream integration outputs are:

- `career-ops/data/external_jobs.json`
- `career-ops/data/pipeline.md`

So the tool currently gives you:
1. one merged deduplicated job pool
2. one archived run snapshot
3. one career-ops-ready job handoff file
4. one populated Career-Ops pending queue for downstream evaluation

---

## What You Should Expect From Each Workflow Stage

| Stage | Input | Output | Expected behavior |
|---|---|---|---|
| ATS scan | `career-ops/portals.yml` | ATS jobs | scans API-detectable companies |
| Feed fetch | keywords | `feeds_raw.json` | fetches public jobs without auth |
| JobSpy lane | keywords | `jobspy_raw.json` | scrapes supported boards, or safely returns empty JSON on failure |
| Merge | raw JSON files | `merged.json` | combines and dedupes |
| Snapshot | merged jobs | `pipeline_output_*.json` | archives the run |
| Handoff | merged jobs | `career-ops/data/external_jobs.json` | exposes data to career-ops |
| Queue import | external jobs | `career-ops/data/pipeline.md` | appends pending items for downstream Career-Ops processing |

---

## Where The Outdated CV / Existing CV Fits In This Test

You asked to use the outdated CV / cover-letter context for a test run plan.

### What is actually available locally
I found CV examples in the local repo, including:
- `career-ops/examples/cv-example.md`
- `career-ops/examples/dual-track-engineer-instructor/cv.md`

I did **not** find a local cover-letter file in this project directory.

### What this means for the test
For this workflow:
- discovery/ingestion still does not depend on a polished final CV
- but real Career-Ops evaluation/PDF readiness does depend on `career-ops/config/profile.yml` and `career-ops/cv.md`

So for this test pass, an outdated but factual CV is acceptable as long as it is present in the correct file path and format.

---

## Minimum Technical Success Criteria

The tool should be considered technically working for the reachable automated workflow if all of these are true:

1. ATS scan command completes
2. `data/feeds_raw.json` exists and is non-empty
3. `data/jobspy_raw.json` exists and is valid JSON
4. `data/ats_raw.json` exists and is valid JSON
5. `data/merged.json` exists and is valid JSON
6. `data/pipeline_output_YYYYMMDD_HHMMSS.json` exists
7. `career-ops/data/external_jobs.json` exists
8. `career-ops/data/pipeline.md` receives imported pending entries when new jobs exist

Current status after implementation:
- all reachable sections now pass when source systems return data, including JobSpy-safe scraping and queue import

---

## What Still Needs To Be Done Later (Not Needed For This Technical Test)

1. replace placeholder/outdated profile/CV inputs with your real final data
2. optionally add proxies if board coverage needs hardening
3. verify career-ops downstream evaluation, PDF, and tracker flow against the imported queue in your preferred CLI/agent flow

---

## Fastest Practical Test You Can Run

```bash
cd "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\career-ops"
npm run scan

cd "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\pipeline"
"C:\Python313\python.exe" run_pipeline.py "software engineer" "data engineer"
```

Then inspect:
- `data/merged.json`
- `data/pipeline_output_YYYYMMDD_HHMMSS.json`
- `career-ops/data/external_jobs.json`

If those three look correct, the tool is technically working in its current v1 state.
