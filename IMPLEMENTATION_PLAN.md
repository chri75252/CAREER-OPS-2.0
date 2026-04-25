# CAREER OPS 2.0 — Implementation Plan

> **Approach:** Surgical, no over-engineering. Focus on working architecture.
> **Principle:** Each step produces a working artifact before moving to the next.

---

## Architecture (What We're Building)

```
┌─────────────────────────────────────────────────────────┐
│                    CAREER-OPS CORE                       │
│         Evaluation · Matching · CV Generation           │
└───────────────────────┬─────────────────────────────────┘
                        │ reads merged job data
                        ▼
┌─────────────────────────────────────────────────────────┐
│              MERGED OUTPUT (data/merged.json)            │
│    All lanes combined, deduplicated, normalized          │
└───────┬───────────────┬─────────────────┬───────────────┘
        │               │                 │
        ▼               ▼                 ▼
   Lane 1: ATS     Lane 2: Feeds    Lane 3: JobSpy
   (npm run scan)  (Python script)  (Python script)
   Greenhouse/     RemoteOK/        Indeed/
   Ashby/Lever     Remotive/etc.    LinkedIn/etc.
```

**Data flow:** Each lane writes to `data/<lane>_raw.json` → `dedupe-merge/merger.py` reads all three → writes `data/merged.json` → career-ops evaluation modes consume it.

---

## Step 1: Verify Career-Ops Baseline

**Goal:** Confirm `npm run scan` works with default ATS APIs.

### 1.1 Run the scanner

```bash
cd "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\career-ops"
npm run scan
```

Expected output: JSON job listings from configured companies' ATS APIs.

### 1.2 If scan fails, check Node.js version

```bash
node --version
```

Career-ops requires Node 18+. If missing, install from `https://nodejs.org`.

### 1.3 Verify output format

The scanner writes to `career-ops/data/` or stdout. Career-ops uses a normalized job schema:

```json
{
  "title": "string",
  "company": "string",
  "location": "string",
  "url": "string",
  "description": "string"
}
```

All other lanes must match this schema for the merge layer to work.

---

## Step 2: Free Feed Ingestion (Lane 2)

**Goal:** Fetch jobs from 6 free sources, output to `data/feeds_raw.json`.

### 2.1 Install dependencies

```bash
pip install requests feedparser
```

### 2.2 Create the fetcher script

**File:** `feed-fetcher/fetcher.py`

```python
import requests
import json
import time
import hashlib
import feedparser
import os
import sys

USER_AGENT = "Mozilla/5.0 (compatible; JobDiscoveryBot/1.0)"
TIMEOUT = 15
MAX_PER_SOURCE = 100

def fetch_remoteok():
    jobs = []
    try:
        r = requests.get("https://remoteok.com/api", headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            for item in data[1:]:
                if item.get("position") and item.get("company"):
                    jobs.append({
                        "title": item["position"],
                        "company": item["company"],
                        "url": item.get("url", ""),
                        "location": item.get("location", "Remote"),
                        "source": "remoteok",
                        "posted_at": item.get("created_at", ""),
                        "description": item.get("description", "")[:500],
                    })
    except Exception as e:
        print(f"  RemoteOK error: {e}")
    return jobs

def fetch_remotive():
    jobs = []
    try:
        r = requests.get("https://remotive.com/api/remote-jobs?category=software-dev&limit=50",
                        headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            for item in data.get("jobs", []):
                if item.get("title") and item.get("company_name"):
                    jobs.append({
                        "title": item["title"],
                        "company": item["company_name"],
                        "url": item.get("url", ""),
                        "location": item.get("candidate_required_location", "Remote"),
                        "source": "remotive",
                        "posted_at": item.get("publication_date", ""),
                        "description": item.get("description", "")[:500],
                    })
    except Exception as e:
        print(f"  Remotive error: {e}")
    return jobs

def fetch_arbeitnow():
    jobs = []
    try:
        r = requests.get("https://arbeitnow.com/api/job-board-api",
                        headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            for item in data.get("data", [])[:MAX_PER_SOURCE]:
                tags = item.get("tags", [])
                if isinstance(tags, list):
                    tags = " ".join(tags)
                if item.get("title") and item.get("company_name"):
                    jobs.append({
                        "title": item["title"],
                        "company": item["company_name"],
                        "url": item.get("url", ""),
                        "location": item.get("location", "Remote"),
                        "source": "arbeitnow",
                        "posted_at": item.get("created_at", ""),
                        "description": item.get("description", "")[:500],
                    })
    except Exception as e:
        print(f"  Arbeitnow error: {e}")
    return jobs

def fetch_weworkremotely():
    jobs = []
    try:
        r = requests.get("https://weworkremotely.com/remote-jobs.rss",
                        headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        if r.status_code == 200:
            feed = feedparser.parse(r.text)
            for entry in feed.entries[:MAX_PER_SOURCE]:
                title = entry.get("title", "").replace("<p>", "").replace("</p>", "")
                company = entry.get("author", "")
                if title and company:
                    jobs.append({
                        "title": title,
                        "company": company,
                        "url": entry.get("link", ""),
                        "location": "Remote",
                        "source": "weworkremotely",
                        "posted_at": entry.get("published", ""),
                        "description": entry.get("summary", "")[:500],
                    })
    except Exception as e:
        print(f"  WeWorkRemotely error: {e}")
    return jobs

def fetch_jobicy():
    jobs = []
    try:
        r = requests.get("https://jobicy.com/api/v2/remote-jobs",
                        headers={"User-Agent": USER_AGENT, "Accept": "application/json"}, timeout=TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            for item in data.get("jobs", [])[:MAX_PER_SOURCE]:
                if item.get("title") and item.get("companyName"):
                    jobs.append({
                        "title": item["title"],
                        "company": item["companyName"],
                        "url": item.get("url", ""),
                        "location": item.get("candidateRequiredLocation", "Remote"),
                        "source": "jobicy",
                        "posted_at": item.get("pubDate", ""),
                        "description": item.get("description", "")[:500],
                    })
    except Exception as e:
        print(f"  Jobicy error: {e}")
    return jobs

def fetch_pythonorg():
    jobs = []
    try:
        r = requests.get("https://python.org/jobs/feed",
                        headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        if r.status_code == 200:
            feed = feedparser.parse(r.text)
            for entry in feed.entries[:MAX_PER_SOURCE]:
                title = entry.get("title", "")
                company = entry.get("author", "")
                if title and company:
                    jobs.append({
                        "title": title,
                        "company": company,
                        "url": entry.get("link", ""),
                        "location": "Remote",
                        "source": "pythonorg",
                        "posted_at": entry.get("published", ""),
                        "description": entry.get("summary", "")[:500],
                    })
    except Exception as e:
        print(f"  Python.org error: {e}")
    return jobs

def job_key(job):
    u = job.get("url", "").strip().lower()
    t = job.get("title", "").strip().lower()
    c = job.get("company", "").strip().lower()
    return hashlib.sha256(f"{u}|{t}|{c}".encode()).hexdigest()[:16]

def main():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(data_dir, exist_ok=True)

    sources = [
        ("RemoteOK", fetch_remoteok),
        ("Remotive", fetch_remotive),
        ("Arbeitnow", fetch_arbeitnow),
        ("WeWorkRemotely", fetch_weworkremotely),
        ("Jobicy", fetch_jobicy),
        ("Python.org", fetch_pythonorg),
    ]

    all_jobs = []
    seen = set()

    for name, fetcher in sources:
        print(f"  -> {name}...", end=" ")
        jobs = fetcher()
        print(f"{len(jobs)} jobs")
        for job in jobs:
            key = job_key(job)
            if key not in seen:
                seen.add(key)
                all_jobs.append(job)
        time.sleep(0.5)

    output = os.path.join(data_dir, "feeds_raw.json")
    with open(output, "w", encoding="utf-8") as f:
        json.dump(all_jobs, f, ensure_ascii=False, indent=2)

    print(f"[*] Saved {len(all_jobs)} jobs to {output}")

if __name__ == "__main__":
    main()
```

### 2.3 Test it

```bash
cd "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\feed-fetcher"
python fetcher.py
```

Expected: `data/feeds_raw.json` created with 10-50 jobs.

---

## Step 3: JobSpy Integration (Lane 3)

**Goal:** Scrape job boards, handle failures gracefully, output to `data/jobspy_raw.json`.

### 3.1 Install JobSpy

```bash
pip install jobspy
```

### 3.2 Create the wrapper script

**File:** `jobspy-wrapper/scrape.py`

```python
import sys
import json
import os
import time
import random
import hashlib
from typing import Optional

try:
    from jobspy import scrape_jobs
except ImportError:
    print("[!] JobSpy not installed: pip install jobspy")
    sys.exit(1)

MAX_RETRIES = 3
RETRY_BASE_DELAY = 2
RATE_DELAY_MIN = 2
RATE_DELAY_MAX = 5
CIRCUIT_BREAKER_LIMIT = 3

PROXY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proxies.txt")

def load_proxies():
    try:
        with open(PROXY_FILE, "r") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return []

def get_proxy():
    proxies = load_proxies()
    if not proxies:
        return None
    proxy = random.choice(proxies)
    return {"http": proxy, "https": proxy}

def job_key(job):
    u = job.get("url", "").strip().lower()
    t = job.get("title", "").strip().lower()
    c = job.get("company", "").strip().lower()
    return hashlib.sha256(f"{u}|{t}|{c}".encode()).hexdigest()[:16]

def scrape_single_board(board, search_term, location, max_results=50, country="usa"):
    proxies = get_proxy()
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            delay = random.uniform(RATE_DELAY_MIN, RATE_DELAY_MAX)
            print(f"  -> {board} (attempt {attempt+1}, delay={delay:.1f}s)...", end=" ")

            results = scrape_jobs(
                site_name=[board],
                search_term=search_term,
                location=location,
                results_wanted=max_results,
                hours_old=72,
                country_indeed=country,
                proxies=proxies,
                rate_delay_min=RATE_DELAY_MIN,
                rate_delay_max=RATE_DELAY_MAX,
            )

            jobs = []
            for _, row in results.iterrows():
                job = {
                    "title": str(row.get("title", "")),
                    "company": str(row.get("company", "")),
                    "url": str(row.get("url", "")),
                    "location": str(row.get("location", location)),
                    "source": board,
                    "posted_at": str(row.get("date_posted", "")),
                    "description": str(row.get("description", ""))[:500],
                }
                if job["title"] and job["company"]:
                    jobs.append(job)

            print(f"{len(jobs)} jobs")
            return jobs, True

        except Exception as e:
            last_error = str(e)
            print(f"failed: {last_error}")
            if attempt < MAX_RETRIES - 1:
                wait = RETRY_BASE_DELAY * (2 ** attempt)
                print(f"    Retrying in {wait}s...")
                time.sleep(wait)

    print(f"  [!] {board} failed after {MAX_RETRIES} attempts: {last_error}")
    return [], False

def main():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(data_dir, exist_ok=True)

    boards = ["indeed", "google"]
    search_term = "software engineer"
    location = "Remote"
    max_per_board = 30

    all_jobs = []
    seen = set()
    failure_count = {}

    print("[*] Running JobSpy board scraper...")

    for board in boards:
        if failure_count.get(board, 0) >= CIRCUIT_BREAKER_LIMIT:
            print(f"  [!] {board} circuit-open (skipped)")
            continue

        jobs, success = scrape_single_board(board, search_term, location, max_per_board)

        if not success:
            failure_count[board] = failure_count.get(board, 0) + 1
        else:
            failure_count[board] = 0
            for job in jobs:
                key = job_key(job)
                if key not in seen:
                    seen.add(key)
                    all_jobs.append(job)

        time.sleep(random.uniform(1, 3))

    output = os.path.join(data_dir, "jobspy_raw.json")
    with open(output, "w", encoding="utf-8") as f:
        json.dump(all_jobs, f, ensure_ascii=False, indent=2)

    print(f"[*] Saved {len(all_jobs)} jobs to {output}")

if __name__ == "__main__":
    main()
```

### 3.3 Test it

```bash
cd "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\jobspy-wrapper"
python scrape.py
```

Expected: `data/jobspy_raw.json` created. If Indeed/Google block without proxies, the script will retry and fail gracefully — that's the correct behavior for this step.

---

## Step 4: Dedup + Merge Layer

**Goal:** Read all 3 lane outputs, deduplicate, write single `data/merged.json`.

### 4.1 Create the merger script

**File:** `dedupe-merge/merger.py`

```python
import json
import hashlib
import os
from pathlib import Path

def job_key(job):
    u = job.get("url", "").strip().lower()
    t = job.get("title", "").strip().lower()
    c = job.get("company", "").strip().lower()
    return hashlib.sha256(f"{u}|{t}|{c}".encode()).hexdigest()[:16]

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    base = Path(__file__).parent.parent / "data"
    sources = [
        base / "ats_raw.json",
        base / "feeds_raw.json",
        base / "jobspy_raw.json",
    ]

    all_jobs = []
    for src in sources:
        jobs = load_json(str(src))
        print(f"  {src.name}: {len(jobs)} jobs loaded")
        all_jobs.extend(jobs)

    print(f"  Total before dedupe: {len(all_jobs)}")

    seen = set()
    merged = []
    for job in all_jobs:
        key = job_key(job)
        if key not in seen:
            seen.add(key)
            merged.append(job)

    print(f"  Total after dedupe: {len(merged)}")

    output = base / "merged.json"
    with open(output, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print(f"[*] Merged output: {output}")

if __name__ == "__main__":
    main()
```

### 4.2 Test it

```bash
cd "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\dedupe-merge"
python merger.py
```

Expected: `data/merged.json` created with deduplicated jobs from all available lanes.

---

## Step 5: Pipeline Orchestrator

**Goal:** Single command runs all lanes, merges, produces final output.

### 5.1 Create the pipeline runner

**File:** `pipeline/run_pipeline.py`

```python
import subprocess
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CAREER_OPS_DIR = BASE_DIR / "career-ops"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def run_step(name, cmd, cwd=None):
    log(f"=== {name} ===")
    result = subprocess.run(cmd, cwd=cwd or str(BASE_DIR), capture_output=True, text=True)
    if result.stdout:
        for line in result.stdout.strip().split("\n"):
            print(f"    {line}")
    if result.returncode != 0:
        print(f"  [!] {name} failed: {result.stderr[:200]}")
        return False
    return True

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def job_key(job):
    u = job.get("url", "").strip().lower()
    t = job.get("title", "").strip().lower()
    c = job.get("company", "").strip().lower()
    return hashlib.sha256(f"{u}|{t}|{c}".encode()).hexdigest()[:16]

def main():
    DATA_DIR.mkdir(exist_ok=True)

    log("Starting pipeline")

    import hashlib

    run_step(
        "1/3 — Free feed fetch",
        [sys.executable, str(BASE_DIR / "feed-fetcher" / "fetcher.py")],
        cwd=str(BASE_DIR / "feed-fetcher"),
    )

    run_step(
        "2/3 — JobSpy board scrape",
        [sys.executable, str(BASE_DIR / "jobspy-wrapper" / "scrape.py")],
        cwd=str(BASE_DIR / "jobspy-wrapper"),
    )

    run_step(
        "3/3 — Merge + dedupe",
        [sys.executable, str(BASE_DIR / "dedupe-merge" / "merger.py")],
        cwd=str(BASE_DIR / "dedupe-merge"),
    )

    merged = load_json(str(DATA_DIR / "merged.json"))
    log(f"Pipeline complete — {len(merged)} unique jobs in data/merged.json")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot = DATA_DIR / f"pipeline_output_{timestamp}.json"
    with open(snapshot, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    log(f"Snapshot saved: {snapshot.name}")

if __name__ == "__main__":
    main()
```

### 5.2 Test it

```bash
cd "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\pipeline"
python run_pipeline.py
```

Expected: All 3 steps run, `data/merged.json` + `data/pipeline_output_*.json` created.

---

## Step 6: Wire Into Career-Ops Evaluation

**Goal:** Feed merged job data into career-ops for scoring/matching/CV generation.

### 6.1 Understand career-ops data contract

Career-ops expects job data in its `data/` directory or `jds/` directory. The format follows its `DATA_CONTRACT.md`:

```json
{
  "title": "...",
  "company": "...",
  "url": "...",
  "location": "...",
  "description": "..."
}
```

Our merged output already matches this schema.

### 6.2 Create the bridge script

**File:** `pipeline/career_ops_bridge.py`

```python
import json
import os
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CAREER_OPS_DATA = BASE_DIR / "career-ops" / "data"
CAREER_OPS_JDS = BASE_DIR / "career-ops" / "jds"

def main():
    merged_path = DATA_DIR / "merged.json"
    if not merged_path.exists():
        print("[!] data/merged.json not found. Run pipeline first.")
        return

    with open(merged_path, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    os.makedirs(CAREER_OPS_DATA, exist_ok=True)
    os.makedirs(CAREER_OPS_JDS, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    career_ops_input = []
    for job in jobs:
        career_ops_input.append({
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "url": job.get("url", ""),
            "location": job.get("location", ""),
            "description": job.get("description", ""),
            "source": job.get("source", "external"),
            "posted_at": job.get("posted_at", ""),
        })

    output_path = CAREER_OPS_DATA / f"external_jobs_{timestamp}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(career_ops_input, f, ensure_ascii=False, indent=2)

    print(f"[*] Wrote {len(career_ops_input)} jobs to {output_path}")
    print(f"[*] Career-ops can now evaluate these jobs via its modes")

if __name__ == "__main__":
    main()
```

### 6.3 Test the bridge

```bash
cd "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\pipeline"
python career_ops_bridge.py
```

Expected: `career-ops/data/external_jobs_*.json` created with normalized jobs.

---

## Step 7: End-to-End Validation

**Goal:** Run the full pipeline and verify output at every stage.

### 7.1 Full pipeline run

```bash
cd "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0"
python pipeline/run_pipeline.py
python pipeline/career_ops_bridge.py
```

### 7.2 Verify outputs

```bash
dir "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\data"
```

Expected files:
- `data/feeds_raw.json` — from free feeds
- `data/jobspy_raw.json` — from JobSpy (may be empty if blocked)
- `data/merged.json` — deduplicated combination
- `data/pipeline_output_*.json` — timestamped snapshot
- `career-ops/data/external_jobs_*.json` — career-ops input

### 7.3 Verify job count

```bash
python -c "import json; d=json.load(open('data/merged.json')); print(f'{len(d)} jobs in merged output')"
```

---

## Step 8: Scheduling (Optional)

**Goal:** Run pipeline automatically on a schedule.

### 8.1 Windows Task Scheduler

Create `pipeline/schedule.bat`:

```batch
@echo off
cd /d "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0"
python pipeline\run_pipeline.py >> pipeline\pipeline.log 2>&1
python pipeline\career_ops_bridge.py >> pipeline\pipeline.log 2>&1
echo %date% %time% — Pipeline completed >> pipeline\pipeline.log
```

### 8.2 Register with Task Scheduler

```powershell
$action = New-ScheduledTaskAction -Execute "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\pipeline\schedule.bat"
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
Register-ScheduledTask -TaskName "CareerOps20-Pipeline" -Action $action -Trigger $trigger -Description "Daily job discovery pipeline"
```

---

## Step 9: Adding More Sources (Future)

### 9.1 Add ever-jobs (optional 160+ source aggregator)

```bash
cd "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0"
git clone https://github.com/ever-jobs/ever-jobs.git ever-jobs
cd ever-jobs
npm install
```

Then add to `feed-fetcher/fetcher.py`:

```python
def fetch_everjobs():
    import subprocess
    result = subprocess.run(
        ["npm", "run", "start", "--", "--format=json"],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        return [{
            "title": item.get("title", ""),
            "company": item.get("company", ""),
            "url": item.get("url", ""),
            "location": item.get("location", "Remote"),
            "source": "everjobs",
            "posted_at": item.get("posted_at", ""),
            "description": item.get("description", "")[:500],
        } for item in data if item.get("title") and item.get("company")]
    return []
```

### 9.2 Add stapply-ai/ats-scrapers (optional)

```bash
cd "C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0"
git clone https://github.com/stapply-ai/ats-scrapers.git ats-scrapers
cd ats-scrapers
uv sync
```

Then create `ats-scrapers/run_scrapers.py`:

```python
import subprocess
import json
import os

def run_ats_scrapers():
    result = subprocess.run(
        ["python", "main.py"],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode == 0:
        with open("output/jobs.json", "r") as f:
            return json.load(f)
    return []
```

---

## What This Gives You

| Stage | Input | Output | Status |
|-------|-------|--------|--------|
| Lane 1: ATS | career-ops `portals.yml` | `data/ats_raw.json` | Ready after Step 1 |
| Lane 2: Feeds | 6 free APIs | `data/feeds_raw.json` | Ready after Step 2 |
| Lane 3: JobSpy | Board scraping | `data/jobspy_raw.json` | Ready after Step 3 |
| Merge | All 3 lanes | `data/merged.json` | Ready after Step 4 |
| Pipeline | Single command | `data/pipeline_output_*.json` | Ready after Step 5 |
| Bridge | Merged jobs | `career-ops/data/external_jobs_*.json` | Ready after Step 6 |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `feedparser` not found | `pip install feedparser` |
| `requests` not found | `pip install requests` |
| JobSpy returns 0 jobs | Add proxies to `jobspy-wrapper/proxies.txt` |
| Career-ops scan fails | Check Node.js version (need 18+), run `npm install` in career-ops dir |
| Merge produces 0 jobs | Check that at least one lane produced output — verify `data/feeds_raw.json` exists |
| Pipeline hangs | One lane may be blocking — check console output for which step is stuck |

---

## Next Steps After This Plan

1. **Edit `career-ops/profile.yml`** with your real CV/role details
2. **Edit `career-ops/portals.yml`** with your target companies
3. **Add proxies** to `jobspy-wrapper/proxies.txt` for reliable JobSpy coverage
4. **Run the full pipeline** and verify output
5. **Set up scheduling** for daily runs
6. **Soak test** — run daily for 7-14 days, monitor failure rates, adjust
