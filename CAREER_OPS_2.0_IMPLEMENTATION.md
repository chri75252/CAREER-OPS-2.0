# CAREER OPS 2.0 — Implementation Plan

> **Approach:** Surgical, no over-engineering. Architecture-first. Configuration-agnostic.
> **Goal:** Working pipeline that ingests from 3 lanes → dedupes → feeds career-ops evaluation.
> **Risk mitigation:** Each step is independently testable. Failure in one lane doesn't block others.

---

## Architecture (What We're Building)

```
[Run Pipeline]
     │
     ├── Lane 1: career-ops ATS scan (Greenhouse/Ashby/Lever)
     ├── Lane 2: Free feeds (RemoteOK, Remotive, Arbeitnow, WWR, Jobicy, Python.org)
     └── Lane 3: JobSpy (Indeed, LinkedIn, Google, ZipRecruiter)
           │
           ▼
     [Dedupe + Merge] → merged.json
           │
           ▼
     [Career-Ops Eval] → ranked shortlist + CVs
```

---

## STEP 1: Verify Career-Ops ATS Scan Works

**Why:** This is the most reliable lane. If it works, you always have at least one source.

### 1A. Check career-ops install

```bash
cd "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\career-ops"
node doctor.mjs
```

**Expected output:** All checks pass. If any fail, note which ones and fix before proceeding.

### 1B. Run scan with default portals

```bash
cd "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\career-ops"
node scan.mjs --json 2>&1
```

**What to look for:**
- If it returns JSON with job objects → ✅ working
- If it errors on missing `portals.yml` → the file exists but may be empty or malformed
- If it returns `[]` (empty array) → working, but no ATS companies in portals.yml match

### 1C. Verify output format

The scan output should look like:
```json
[
  {
    "title": "Senior Engineer",
    "company": "Stripe",
    "location": "Remote",
    "url": "https://...",
    "posted": "2025-01-15"
  }
]
```

If the shape differs, note the actual keys — we'll need to normalize in the merge step.

**If scan fails entirely:**
- Check `portals.yml` syntax (valid YAML)
- Check Node version (career-ops needs Node 18+)
- Run `npm install` again if `node_modules` is missing

---

## STEP 2: Test JobSpy Baseline

**Why:** JobSpy is the breadth lane. It will fail without proxies on some boards, but should work on Indeed/Google without them.

### 2A. Quick single-board test (no proxies)

```bash
cd "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\jobspy-wrapper"
python -c "
from scrape import scrape_with_retry
jobs = scrape_with_retry(
    site_name=['indeed'],
    search_term='software engineer',
    location='Remote',
    max_results=10,
    hours_old=72,
)
print(f'Got {len(jobs)} jobs from Indeed')
for j in jobs[:3]:
    print(f'  - {j[\"title\"]} at {j[\"company\"]}')
"
```

**Expected:**
- 5-15 jobs from Indeed → ✅ baseline works
- 0 jobs with 429/403 error → anti-bot blocking, need proxies or skip this board
- ImportError → JobSpy not installed, run `pip install jobspy`

### 2B. Test Google Jobs (usually works without proxies)

```bash
cd "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\jobspy-wrapper"
python -c "
from scrape import scrape_with_retry
jobs = scrape_with_retry(
    site_name=['google'],
    search_term='software engineer',
    location='Remote',
    max_results=10,
    hours_old=72,
)
print(f'Got {len(jobs)} jobs from Google')
for j in jobs[:3]:
    print(f'  - {j[\"title\"]} at {j[\"company\"]}')
"
```

**Expected:** Google Jobs usually returns data without proxies. If it works, you have a viable breadth lane even without LinkedIn.

### 2C. Decision point

| Result | Action |
|--------|--------|
| Indeed works, Google works | Use both. Skip LinkedIn/ZipRecruiter until you add proxies. |
| Only Google works | Use Google only. Add proxies later for more boards. |
| Both fail | JobSpy anti-bot is blocking your IP. Either get proxies or rely on feeds + ATS only. |

---

## STEP 3: Wire Pipeline Output → Career-Ops Evaluation

**Why:** This is the missing link. We have merged jobs, but career-ops doesn't consume them yet.

### 3A. Understand career-ops evaluation input

Career-ops evaluation modes expect job data in its `data/` or `jds/` directory. The standard flow is:

1. `scan.mjs` writes to `data/` or stdout
2. Evaluation modes read from the same location

We need to drop our `merged.json` into a location career-ops can read.

### 3B. Create the bridge script

Create: `C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\pipeline\bridge_to_career_ops.py`

```python
import json
import os
import sys
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.parent
MERGED = BASE / "data" / "merged.json"
CAREER_OPS_DATA = BASE / "career-ops" / "data"

def normalize_for_career_ops(job: dict) -> dict:
    """Convert our unified job format to career-ops expected format."""
    return {
        "title": job.get("title", ""),
        "company": job.get("company", ""),
        "location": job.get("location", "Remote"),
        "url": job.get("url", ""),
        "posted": job.get("posted_at", datetime.now().isoformat()),
        "source": job.get("source", "unknown"),
        "description": job.get("description", ""),
        "tags": job.get("tags", []),
    }

def bridge():
    if not MERGED.exists():
        print(f"[!] {MERGED} not found. Run the pipeline first.")
        return False

    with open(MERGED, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    if not jobs:
        print("[!] No jobs to bridge.")
        return False

    normalized = [normalize_for_career_ops(j) for j in jobs]

    CAREER_OPS_DATA.mkdir(parents=True, exist_ok=True)
    output = CAREER_OPS_DATA / f"external_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(output, "w", encoding="utf-8") as f:
        json.dump(normalized, f, ensure_ascii=False, indent=2)

    print(f"[+] Bridged {len(normalized)} jobs to career-ops: {output.name}")
    return True

if __name__ == "__main__":
    bridge()
```

### 3C. Update the pipeline runner

Add the bridge step to `C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\pipeline\run_pipeline.py`:

After the existing merge step, add:

```python
    step("4/5 — Bridge to career-ops", run_py,
         str(BASE_DIR / "pipeline" / "bridge_to_career_ops.py"))
```

This ensures the merged output is placed where career-ops can find it.

---

## STEP 4: Create the Single Runner Script

**Why:** One command runs everything. No manual chaining.

Replace `C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\pipeline\run_pipeline.py` with this complete version:

```python
import subprocess
import json
import os
import sys
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.parent
DATA = BASE / "data"
CAREER_OPS = BASE / "career-ops"

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")

def run_py(script, *args, cwd=None):
    cmd = [sys.executable, str(script)] + list(args)
    result = subprocess.run(
        cmd, cwd=cwd or str(BASE), capture_output=True, text=True, timeout=300
    )
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0 and result.stderr:
        print(f"[!] {script.name} stderr: {result.stderr}", file=sys.stderr)
    return result.returncode == 0

def load_json(path):
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def dedupe(jobs):
    seen = set()
    result = []
    for j in jobs:
        key = f"{j.get('url','').lower().strip()}|{j.get('title','').lower().strip()}|{j.get('company','').lower().strip()}"
        if key not in seen:
            seen.add(key)
            result.append(j)
    return result

def run_pipeline(keywords=None, location="Remote", max_per_board=30):
    if keywords is None:
        keywords = ["software engineer"]

    DATA.mkdir(parents=True, exist_ok=True)
    log(f"Starting pipeline — keywords: {keywords}")

    all_jobs = []

    # Lane 1: Free feeds
    log("Lane 1: Free feeds")
    feed_script = BASE / "feed-fetcher" / "fetcher.py"
    if feed_script.exists():
        ok = run_py(feed_script, *keywords, cwd=str(BASE / "feed-fetcher"))
        feeds = load_json(DATA / "feeds_raw.json")
        log(f"  Feeds: {len(feeds)} jobs")
        all_jobs.extend(feeds)
    else:
        log("  [!] feed-fetcher not found — skipping")

    # Lane 2: JobSpy
    log("Lane 2: JobSpy")
    jobspy_script = BASE / "jobspy-wrapper" / "scrape.py"
    if jobspy_script.exists():
        ok = run_py(jobspy_script, *keywords, cwd=str(BASE / "jobspy-wrapper"))
        spy = load_json(DATA / "jobspy_raw.json")
        log(f"  JobSpy: {len(spy)} jobs")
        all_jobs.extend(spy)
    else:
        log("  [!] jobspy-wrapper not found — skipping")

    # Lane 3: Career-ops ATS scan
    log("Lane 3: Career-ops ATS scan")
    scan_script = CAREER_OPS / "scan.mjs"
    if scan_script.exists():
        result = subprocess.run(
            ["node", "scan.mjs", "--json"],
            cwd=str(CAREER_OPS),
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0 and result.stdout.strip():
            try:
                ats = json.loads(result.stdout)
                log(f"  ATS: {len(ats)} jobs")
                all_jobs.extend(ats)
            except json.JSONDecodeError:
                log("  [!] ATS scan returned non-JSON output")
        else:
            log(f"  [!] ATS scan failed (exit {result.returncode})")
    else:
        log("  [!] career-ops scan.mjs not found — skipping")

    # Dedupe
    log(f"Deduping — {len(all_jobs)} total before dedupe")
    merged = dedupe(all_jobs)
    log(f"  {len(merged)} unique after dedupe")

    merged_path = DATA / "merged.json"
    with open(merged_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    # Bridge to career-ops
    log("Bridging to career-ops")
    bridge_script = BASE / "pipeline" / "bridge_to_career_ops.py"
    if bridge_script.exists():
        run_py(bridge_script)

    # Final output
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_path = DATA / f"pipeline_{ts}.json"
    with open(final_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    log(f"Pipeline complete — {len(merged)} jobs → {final_path.name}")
    return merged

if __name__ == "__main__":
    keywords = sys.argv[1:] or ["software engineer", "data engineer"]
    run_pipeline(keywords)
```

---

## STEP 5: Set Up Windows Task Scheduler

**Why:** Run the pipeline daily without manual intervention.

### 5A. Create the scheduler batch file

Create: `C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\pipeline\run_daily.bat`

```batch
@echo off
cd /d "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\pipeline"
python run_pipeline.py "software engineer" "data engineer" "backend developer" >> "%~dp0..\data\pipeline_log.txt" 2>&1
echo [%date% %time%] Pipeline run complete >> "%~dp0..\data\pipeline_log.txt"
```

### 5B. Register the scheduled task

Open PowerShell as Administrator and run:

```powershell
$action = New-ScheduledTaskAction `
    -Execute "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\pipeline\run_daily.bat"

$trigger = New-ScheduledTaskTrigger `
    -Daily `
    -At 8:00AM

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable

Register-ScheduledTask `
    -TaskName "CareerOps2.0-DailyPipeline" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Run Career Ops 2.0 job discovery pipeline daily"
```

This runs the pipeline every morning at 8 AM. Adjust the time as needed.

### 5C. Verify the task

```powershell
Get-ScheduledTask -TaskName "CareerOps2.0-DailyPipeline" | Format-List
```

---

## STEP 6: Full End-to-End Test

**Why:** Verify the entire chain works before relying on it.

### 6A. Run the pipeline

```bash
cd "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\pipeline"
python run_pipeline.py "software engineer" "data engineer"
```

### 6B. Verify outputs

Check these files exist and contain data:

```bash
# Check merged output
dir "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\data\merged.json"

# Check career-ops bridge output
dir "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\career-ops\data\external_jobs_*.json"

# Check pipeline log
type "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\data\pipeline_log.txt"
```

### 6C. Verify career-ops can read the bridged data

```bash
cd "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\career-ops"
# The evaluation modes will read from data/external_jobs_*.json
# Run the evaluation mode to confirm it picks up the bridged jobs
```

### 6D. Expected success criteria

| Check | Pass condition |
|-------|---------------|
| Free feeds | At least 1 source returns jobs |
| JobSpy | At least 1 board returns jobs (Google or Indeed) |
| ATS scan | Runs without crash (may return 0 if no portals configured) |
| Dedupe | Merged count < sum of all lanes |
| Bridge | `external_jobs_*.json` exists in career-ops/data/ |
| Pipeline log | No fatal errors in `pipeline_log.txt` |

---

## STEP 7: Soak Test Protocol

**Why:** Confirm reliability over time, not just once.

### 7A. Run daily for 3 days

```bash
# Day 1
python run_pipeline.py "software engineer"

# Day 2
python run_pipeline.py "data engineer"

# Day 3
python run_pipeline.py "backend developer"
```

### 7B. Monitor failure rates

After 3 days, check `pipeline_log.txt`:

```bash
type "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\data\pipeline_log.txt"
```

Count how many runs had errors per source:
- If a source fails 2+ out of 3 runs → demote it (remove from active list)
- If all sources work consistently → pipeline is production-ready

### 7C. Tune rate limits

If you see 429/403 errors in the log:

1. Open `jobspy-wrapper/scrape.py`
2. Increase `RATE_DELAY_MIN` from 2 to 4
3. Increase `RATE_DELAY_MAX` from 5 to 8
4. Re-run and verify errors stop

---

## STEP 8: Optional — Add ever-jobs as Lane 4

**Why:** 160+ sources, but newer and less field-tested. Add only after core pipeline is stable.

### 8A. Clone and install

```bash
cd "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0"
git clone --depth 1 https://github.com/ever-jobs/ever-jobs.git ever-jobs
cd ever-jobs
npm install
```

### 8B. Create wrapper

Create: `C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\ever-jobs\wrapper.py`

```python
import subprocess
import json
from pathlib import Path

BASE = Path(__file__).parent

def fetch_ever_jobs(keywords=None):
    if keywords is None:
        keywords = ["software engineer"]

    result = subprocess.run(
        ["npm", "run", "start", "--", "--keywords", ",".join(keywords), "--json"],
        cwd=str(BASE),
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        print(f"[!] ever-jobs failed: {result.stderr}")
        return []

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []

if __name__ == "__main__":
    import sys
    jobs = fetch_ever_jobs(sys.argv[1:])
    output = BASE.parent / "data" / "ever_jobs_raw.json"
    with open(output, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print(f"[+] ever-jobs: {len(jobs)} jobs → {output.name}")
```

### 8C. Add to pipeline

In `run_pipeline.py`, after the JobSpy lane, add:

```python
    # Lane 4: ever-jobs (optional)
    log("Lane 4: ever-jobs")
    ever_script = BASE / "ever-jobs" / "wrapper.py"
    if ever_script.exists():
        ok = run_py(ever_script, *keywords, cwd=str(BASE / "ever-jobs"))
        ever = load_json(DATA / "ever_jobs_raw.json")
        log(f"  ever-jobs: {len(ever)} jobs")
        all_jobs.extend(ever)
    else:
        log("  [!] ever-jobs not found — skipping")
```

---

## STEP 9: Optional — Add stapply-ai as Lane 5

**Why:** ATS-focused scraper. Same pattern as ever-jobs — add only after core is stable.

### 9A. Clone and install

```bash
cd "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0"
git clone --depth 1 https://github.com/stapply-ai/ats-scrapers.git stapply-ai
cd stapply-ai
pip install -r requirements.txt 2>/dev/null || true
```

### 9B. Create wrapper

Create: `C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\stapply-ai\wrapper.py`

```python
import subprocess
import json
from pathlib import Path

BASE = Path(__file__).parent

def fetch_stapply_jobs(keywords=None):
    if keywords is None:
        keywords = ["software engineer"]

    result = subprocess.run(
        ["python", "main.py", "--keywords", ",".join(keywords), "--output", "json"],
        cwd=str(BASE),
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        print(f"[!] stapply failed: {result.stderr}")
        return []

    output = BASE / "jobs.json"
    if output.exists():
        with open(output) as f:
            return json.load(f)
    return []

if __name__ == "__main__":
    import sys
    jobs = fetch_stapply_jobs(sys.argv[1:])
    output = BASE.parent / "data" / "stapply_raw.json"
    with open(output, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print(f"[+] stapply: {len(jobs)} jobs → {output.name}")
```

---

## File Tree After Completion

```
CARRER OPS 2.0/
├── CAREER_OPS_2.0_BUILD_SPEC.md      ← Spec document
├── CAREER_OPS_2.0_IMPLEMENTATION.md  ← This file
│
├── career-ops/                       ← Core engine (cloned)
│   ├── scan.mjs                      ← ATS scanner
│   ├── profile.yml                   ← Your CV (edit)
│   ├── portals.yml                   ← Target companies (edit)
│   ├── data/                         ← Job input/output
│   │   └── external_jobs_*.json      ← Bridged from pipeline
│   └── modes/                        ← 14 workflow modes
│
├── feed-fetcher/
│   └── fetcher.py                    ← 6 free feeds (tested ✅)
│
├── jobspy-wrapper/
│   ├── scrape.py                     ← JobSpy with rate limits + retries
│   └── proxies.txt                   ← Add proxies here
│
├── dedupe-merge/
│   └── merger.py                     ← Deduplicate + merge (tested ✅)
│
├── pipeline/
│   ├── run_pipeline.py               ← Single runner (all lanes)
│   ├── bridge_to_career_ops.py       ← Bridge output to career-ops
│   └── run_daily.bat                 ← Windows scheduler entry
│
├── config/
│   ├── profile.example.yml
│   ├── portals.example.yml
│   └── pipeline.yaml
│
├── data/
│   ├── feeds_raw.json                ← Lane 1 output
│   ├── jobspy_raw.json               ← Lane 2 output
│   ├── merged.json                   ← Deduped output
│   ├── pipeline_*.json               ← Timestamped snapshots
│   └── pipeline_log.txt              ← Run log
│
└── ever-jobs/                        ← Optional Lane 4
└── stapply-ai/                       ← Optional Lane 5
```

---

## Execution Order (Do These In Order)

1. **Step 1** — Verify career-ops scan (10 min)
2. **Step 2** — Test JobSpy baseline (15 min)
3. **Step 3** — Create bridge script (5 min)
4. **Step 4** — Replace pipeline runner (5 min)
5. **Step 5** — Set up scheduler (5 min)
6. **Step 6** — Full end-to-end test (15 min)
7. **Step 7** — Soak test (3 days, passive)
8. **Step 8** — Add ever-jobs (optional, 30 min)
9. **Step 9** — Add stapply-ai (optional, 30 min)

**Total active work: ~1.5 hours.** Soak test is passive.

---

## Failure Modes and Recovery

| Failure | Symptom | Fix |
|---------|---------|-----|
| Career-ops scan crashes | `node scan.mjs` exits non-zero | Check `portals.yml` syntax, run `node doctor.mjs` |
| JobSpy returns 0 jobs | All boards fail with 429/403 | Add proxies to `proxies.txt`, or skip JobSpy lane |
| Feed fetcher returns 0 jobs | All feeds fail | Check network connectivity, verify API endpoints haven't changed |
| Dedupe produces 0 results | Bug in hash function | Check that all lanes produce jobs with `url` field |
| Bridge produces no output | `merged.json` doesn't exist | Run pipeline first, check lane outputs |
| Scheduler doesn't fire | Task not registered | Run `Get-ScheduledTask` to verify, re-register if needed |

---

## What This Plan Guarantees

1. **At least one lane always works** — free feeds have no auth, no anti-bot
2. **Failure isolation** — each lane runs independently; one failure doesn't stop others
3. **Deduplication** — URL + title + company hash prevents duplicates across lanes
4. **Career-ops integration** — bridged output placed where career-ops evaluation modes can read it
5. **Scheduling** — daily runs via Windows Task Scheduler
6. **Logging** — every run logged for debugging
7. **Extensibility** — add more lanes by following the same pattern (clone → wrapper → add to pipeline)
