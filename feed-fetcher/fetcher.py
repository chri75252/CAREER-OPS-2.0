# Feed Fetcher — Free RSS/JSON Job Sources
# Sources: RemoteOK, Remotive, Arbeitnow, We Work Remotely, Jobicy, Python.org Jobs

import requests
import json
import time
import hashlib
import feedparser
import xmltodict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

USER_AGENT = "Mozilla/5.0 (compatible; JobDiscoveryBot/1.0; +https://example.com/bot)"
REQUEST_TIMEOUT = 15
MAX_PER_SOURCE = 100

def fetch_remoteok(keywords: list[str], location: str = "", max_results: int = MAX_PER_SOURCE) -> list[dict]:
    """Fetch jobs from RemoteOK JSON API — no auth required."""
    jobs = []
    url = "https://remoteok.com/api"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            return []
        data = resp.json()
        for item in data[1:]:  # skip header row
            if len(jobs) >= max_results:
                break
            tags = item.get("tags", [])
            if keywords and not any(k.lower() in (item.get("position", "") + " ".join(tags)).lower() for k in keywords):
                continue
            job = {
                "title": item.get("position", ""),
                "company": item.get("company", ""),
                "url": item.get("url", ""),
                "location": location or item.get("location", "Remote"),
                "source": "remoteok",
                "posted_at": item.get("created_at", ""),
                "tags": tags,
                "description": item.get("description", ""),
            }
            if job["title"] and job["company"]:
                jobs.append(job)
    except Exception as e:
        print(f"  [!] RemoteOK error: {e}")
    return jobs

def fetch_remotive(keywords: list[str], location: str = "", max_results: int = MAX_PER_SOURCE) -> list[dict]:
    """Fetch jobs from Remotive JSON API — no auth required."""
    jobs = []
    category = "software-dev"  # main tech category
    url = f"https://remotive.com/api/remote-jobs?category={category}&limit={max_results}"
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            return []
        data = resp.json()
        for item in data.get("jobs", []):
            if keywords and not any(k.lower() in (item.get("title", "") + item.get("description", "")).lower() for k in keywords):
                continue
            job = {
                "title": item.get("title", ""),
                "company": item.get("company_name", ""),
                "url": item.get("url", ""),
                "location": item.get("candidate_required_location", location or "Remote"),
                "source": "remotive",
                "posted_at": item.get("publication_date", ""),
                "tags": item.get("tags", []),
                "description": item.get("description", "")[:500],
            }
            if job["title"] and job["company"]:
                jobs.append(job)
    except Exception as e:
        print(f"  [!] Remotive error: {e}")
    return jobs

def fetch_arbeitnow(keywords: list[str], location: str = "", max_results: int = MAX_PER_SOURCE) -> list[dict]:
    """Fetch jobs from Arbeitnow JSON API — no auth required."""
    jobs = []
    url = "https://arbeitnow.com/api/job-board-api"
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            return []
        data = resp.json()
        for item in data.get("data", []):
            if len(jobs) >= max_results:
                break
            if keywords and not any(k.lower() in (item.get("title", "") + " ".join(item.get("tags", []))).lower() for k in keywords):
                continue
            job = {
                "title": item.get("title", ""),
                "company": item.get("company_name", ""),
                "url": item.get("url", ""),
                "location": location or item.get("location", "Remote"),
                "source": "arbeitnow",
                "posted_at": item.get("created_at", ""),
                "tags": item.get("tags", []),
                "description": item.get("description", "")[:500],
            }
            if job["title"] and job["company"]:
                jobs.append(job)
    except Exception as e:
        print(f"  [!] Arbeitnow error: {e}")
    return jobs

def fetch_weworkremotely(keywords: list[str], location: str = "", max_results: int = MAX_PER_SOURCE) -> list[dict]:
    """Fetch jobs from We Work Remotely RSS — no auth required."""
    jobs = []
    url = "https://weworkremotely.com/remote-jobs.rss"
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            return []
        feed = feedparser.parse(resp.text)
        for entry in feed.entries[:max_results]:
            if keywords and not any(k.lower() in entry.get("title", "").lower() + entry.get("summary", "") for k in keywords):
                continue
            company = ""
            if hasattr(entry, "author"):
                company = entry.author
            elif hasattr(entry, "author_detail") and hasattr(entry.author_detail, "name"):
                company = entry.author_detail.name
            job = {
                "title": entry.get("title", "").replace("<p>", "").replace("</p>", ""),
                "company": company,
                "url": entry.get("link", ""),
                "location": location or "Remote",
                "source": "weworkremotely",
                "posted_at": entry.get("published", ""),
                "tags": [],
                "description": entry.get("summary", "")[:500],
            }
            if job["title"] and job["company"]:
                jobs.append(job)
    except Exception as e:
        print(f"  [!] WeWorkRemotely error: {e}")
    return jobs

def fetch_jobicy(keywords: list[str], location: str = "", max_results: int = MAX_PER_SOURCE) -> list[dict]:
    """Fetch jobs from Jobicy JSON API — no auth required."""
    jobs = []
    url = "https://jobicy.com/api/v2/remote-jobs"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            return []
        data = resp.json()
        for item in data.get("jobs", [])[:max_results]:
            if keywords and not any(k.lower() in (item.get("title", "") + item.get("description", "")).lower() for k in keywords):
                continue
            job = {
                "title": item.get("title", ""),
                "company": item.get("companyName", ""),
                "url": item.get("url", ""),
                "location": location or item.get("candidateRequiredLocation", "Remote"),
                "source": "jobicy",
                "posted_at": item.get("pubDate", ""),
                "tags": item.get("tags", []),
                "description": item.get("description", "")[:500],
            }
            if job["title"] and job["company"]:
                jobs.append(job)
    except Exception as e:
        print(f"  [!] Jobicy error: {e}")
    return jobs

def fetch_python_jobs(keywords: list[str], max_results: int = MAX_PER_SOURCE) -> list[dict]:
    """Fetch jobs from Python.org Jobs RSS — no auth required."""
    jobs = []
    url = "https://python.org/jobs/feed"
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            return []
        feed = feedparser.parse(resp.text)
        for entry in feed.entries[:max_results]:
            if keywords and not any(k.lower() in entry.get("title", "").lower() + entry.get("summary", "") for k in keywords):
                continue
            company = ""
            if hasattr(entry, "author"):
                company = entry.author
            job = {
                "title": entry.get("title", ""),
                "company": company,
                "url": entry.get("link", ""),
                "location": "Remote",
                "source": "pythonorg",
                "posted_at": entry.get("published", ""),
                "tags": [],
                "description": entry.get("summary", "")[:500],
            }
            if job["title"] and job["company"]:
                jobs.append(job)
    except Exception as e:
        print(f"  [!] Python.org Jobs error: {e}")
    return jobs

def job_key(job: dict) -> str:
    """Generate a dedupe key from a job dict."""
    norm_url = job.get("url", "").strip().lower()
    norm_title = job.get("title", "").strip().lower()
    norm_company = job.get("company", "").strip().lower()
    return hashlib.sha256(f"{norm_url}|{norm_title}|{norm_company}".encode()).hexdigest()[:16]

def fetch_all(keywords: list[str], location: str = "", max_per_source: int = MAX_PER_SOURCE) -> list[dict]:
    """
    Fetch from all free feed sources.
    Returns deduplicated list of jobs.
    """
    print("[*] Fetching free feed sources...")
    all_jobs = []
    seen_keys = set()

    sources = [
        ("RemoteOK", lambda: fetch_remoteok(keywords, location, max_per_source)),
        ("Remotive", lambda: fetch_remotive(keywords, location, max_per_source)),
        ("Arbeitnow", lambda: fetch_arbeitnow(keywords, location, max_per_source)),
        ("WeWorkRemotely", lambda: fetch_weworkremotely(keywords, location, max_per_source)),
        ("Jobicy", lambda: fetch_jobicy(keywords, location, max_per_source)),
        ("Python.org", lambda: fetch_python_jobs(keywords, max_per_source)),
    ]

    for name, fetcher in sources:
        print(f"  -> {name}...", end=" ")
        jobs = fetcher()
        print(f"{len(jobs)} jobs")
        for job in jobs:
            key = job_key(job)
            if key not in seen_keys:
                seen_keys.add(key)
                all_jobs.append(job)
        time.sleep(0.5)  # polite delay between sources

    print(f"[*] Free feeds total (deduped): {len(all_jobs)}")
    return all_jobs

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--location", default="")
    parser.add_argument("--max-per-source", type=int, default=MAX_PER_SOURCE)
    parser.add_argument("keywords", nargs="*")
    args = parser.parse_args()

    keywords = args.keywords or ["python", "data engineer", "backend"]
    jobs = fetch_all(keywords, location=args.location, max_per_source=args.max_per_source)
    output_path = Path(__file__).resolve().parent.parent / "data" / "feeds_raw.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print(f"[*] Saved {len(jobs)} jobs to {output_path}")
