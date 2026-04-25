import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
MERGED = BASE / "data" / "merged.json"
CAREER_OPS_DATA = BASE / "career-ops" / "data"

def main():
    if not MERGED.exists():
        raise SystemExit("merged.json not found")

    with open(MERGED, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    CAREER_OPS_DATA.mkdir(parents=True, exist_ok=True)
    out = CAREER_OPS_DATA / "external_jobs.json"

    with open(out, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

    print(f"Ingested {len(jobs)} jobs -> {out}")

if __name__ == "__main__":
    main()
