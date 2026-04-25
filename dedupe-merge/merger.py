import json
import hashlib
import os
from pathlib import Path

def job_key(job: dict) -> str:
    u = job.get("url", "").strip().lower()
    t = job.get("title", "").strip().lower()
    c = job.get("company", "").strip().lower()
    return hashlib.sha256(f"{u}|{t}|{c}".encode()).hexdigest()[:16]

def load_json(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def dedupe(jobs: list[dict]) -> list[dict]:
    seen = set()
    result = []
    for job in jobs:
        key = job_key(job)
        if key not in seen:
            seen.add(key)
            result.append(job)
    return result

def merge_sources(sources: list[str], output: str = "merged.json"):
    all_jobs = []
    for src in sources:
        jobs = load_json(src)
        print(f"  {src}: {len(jobs)} jobs loaded")
        all_jobs.extend(jobs)
    print(f"  Total before dedupe: {len(all_jobs)}")
    merged = dedupe(all_jobs)
    print(f"  Total after dedupe: {len(merged)}")
    with open(output, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    return merged

if __name__ == "__main__":
    base = Path(__file__).parent.parent / "data"
    sources = [
        base / "ats_raw.json",
        base / "feeds_raw.json",
        base / "jobspy_raw.json",
    ]
    output = base / "merged.json"
    merge_sources([str(s) for s in sources if s.exists()], str(output))
