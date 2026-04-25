import argparse
import hashlib
import json
from pathlib import Path


def job_key(job: dict) -> str:
    norm_url = job.get("url", "").strip().lower()
    norm_title = job.get("title", "").strip().lower()
    norm_company = job.get("company", "").strip().lower()
    return hashlib.sha256(f"{norm_url}|{norm_title}|{norm_company}".encode()).hexdigest()[:16]


def output_path() -> Path:
    path = Path(__file__).resolve().parent.parent / "data" / "jobspy_raw.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def write_jobs(jobs: list[dict]) -> list[dict]:
    path = output_path()
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(jobs, handle, ensure_ascii=False, indent=2)
    print(f"[*] Saved {len(jobs)} jobs to {path}")
    return jobs


def normalize_job(record: dict, keyword: str) -> dict | None:
    title = str(record.get("title") or "").strip()
    company = str(record.get("company") or "").strip()
    url = str(record.get("job_url") or record.get("url") or "").strip()
    if not title or not company or not url:
        return None
    description = str(record.get("description") or "")[:1000]
    job_type = record.get("job_type")
    interval = record.get("interval")
    tags = [str(item).strip() for item in [job_type, interval, keyword] if item]
    return {
        "title": title,
        "company": company,
        "url": url,
        "location": str(record.get("location") or "Remote").strip() or "Remote",
        "source": f"jobspy:{record.get('site') or 'board'}",
        "posted_at": str(record.get("date_posted") or ""),
        "tags": tags,
        "description": description,
    }


def scrape_for_keyword(
    keyword: str,
    location: str,
    results_wanted: int,
    boards: list[str],
    hours_old: int,
    country_indeed: str,
) -> list[dict]:
    try:
        from jobspy import scrape_jobs
    except Exception as exc:
        print(f"[!] python-jobspy unavailable: {exc}")
        return []

    try:
        jobs_df = scrape_jobs(
            site_name=boards,
            search_term=keyword,
            google_search_term=f"{keyword} jobs {location}",
            location=location,
            results_wanted=results_wanted,
            hours_old=hours_old,
            is_remote=True,
            verbose=0,
            country_indeed=country_indeed,
        )
    except Exception as exc:
        print(f"[!] JobSpy scrape failed for '{keyword}': {exc}")
        return []

    if jobs_df is None or getattr(jobs_df, "empty", False):
        print(f"[*] JobSpy returned 0 jobs for '{keyword}'")
        return []

    rows = jobs_df.to_dict("records")
    normalized = []
    seen = set()
    for row in rows:
        item = normalize_job(row, keyword)
        if not item:
            continue
        key = job_key(item)
        if key in seen:
            continue
        seen.add(key)
        normalized.append(item)
    print(f"[*] JobSpy kept {len(normalized)} jobs for '{keyword}'")
    return normalized


def main() -> list[dict]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--location", default="Remote")
    parser.add_argument("--results", type=int, default=15)
    parser.add_argument("--hours-old", type=int, default=168)
    parser.add_argument("--boards", default="indeed,google,zip_recruiter")
    parser.add_argument("--country-indeed", default="worldwide")
    parser.add_argument("keywords", nargs="*")
    args = parser.parse_args()

    keywords = args.keywords or ["AI engineer", "solutions engineer", "automation engineer"]
    boards = [board.strip() for board in args.boards.split(",") if board.strip()]
    combined = []
    seen = set()
    for keyword in keywords:
        for job in scrape_for_keyword(
            keyword,
            args.location,
            args.results,
            boards,
            args.hours_old,
            args.country_indeed,
        ):
            key = job_key(job)
            if key in seen:
                continue
            seen.add(key)
            combined.append(job)
    return write_jobs(combined)


if __name__ == "__main__":
    main()
