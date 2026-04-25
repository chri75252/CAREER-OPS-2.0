import subprocess
import json
import sys
import os
from pathlib import Path
from datetime import datetime

import yaml

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CAREER_OPS_DIR = BASE_DIR / "career-ops"
PYTHON_BIN = r"C:\Python313\python.exe"
JOBSPY_PYTHON_BIN = r"C:\Users\chris\AppData\Local\Programs\Python\Python312\python.exe"
CONFIG_PATH = BASE_DIR / "config" / "pipeline.yaml"

def log(msg: str):
    text = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n"
    sys.stdout.buffer.write(text.encode("utf-8", errors="replace"))
    sys.stdout.flush()

def write_stdout(text: str):
    if not text:
        return
    sys.stdout.buffer.write(text.encode("utf-8", errors="replace"))
    if not text.endswith("\n"):
        sys.stdout.buffer.write(b"\n")
    sys.stdout.flush()

def write_stderr(text: str):
    if not text:
        return
    sys.stderr.buffer.write(text.encode("utf-8", errors="replace"))
    if not text.endswith("\n"):
        sys.stderr.buffer.write(b"\n")
    sys.stderr.flush()

def run_py(script: str, *args, cwd: str | None = None) -> bool:
    cmd = [PYTHON_BIN, script] + list(args)
    result = subprocess.run(
        cmd,
        cwd=cwd or str(BASE_DIR),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.stdout:
        write_stdout(result.stdout)
    if result.returncode != 0:
        write_stderr(f"[!] {script} failed: {result.stderr}")
        return False
    return True

def run_jobspy_py(script: str, *args, cwd: str | None = None) -> bool:
    cmd = [JOBSPY_PYTHON_BIN, script] + list(args)
    result = subprocess.run(
        cmd,
        cwd=cwd or str(BASE_DIR),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.stdout:
        write_stdout(result.stdout)
    if result.returncode != 0:
        write_stderr(f"[!] {script} failed: {result.stderr}")
        return False
    return True

def run_node(script: str, *args, cwd: str | None = None) -> bool:
    full = ["node", script, *args]
    result = subprocess.run(
        full,
        cwd=cwd or str(BASE_DIR),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.stdout:
        write_stdout(result.stdout)
    if result.returncode != 0:
        write_stderr(f"[!] node {script} failed: {result.stderr}")
        return False
    return True

def run_npm(script: str, *args, cwd: str | None = None) -> bool:
    npm_exec = "npm.cmd" if os.name == "nt" else "npm"
    full = [npm_exec, "run", script, *args]
    result = subprocess.run(
        full,
        cwd=cwd or str(BASE_DIR),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.stdout:
        write_stdout(result.stdout)
    if result.returncode != 0:
        write_stderr(f"[!] npm run {script} failed: {result.stderr}")
        return False
    return True

def step(name: str, fn, *args, **kwargs):
    log(f"=== {name} ===")
    ok = fn(*args, **kwargs)
    if not ok:
        write_stdout(f"[!] {name} failed -- continuing anyway")
    return ok

def load_pipeline_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    return loaded if isinstance(loaded, dict) else {}

def run_pipeline(
    keywords: list[str],
    location: str = "Remote",
    max_per_board: int = 30,
    jobspy_boards: list[str] | None = None,
    jobspy_hours_old: int = 168,
    jobspy_country_indeed: str = "united arab emirates",
    enable_ats: bool = True,
    enable_feeds: bool = True,
    enable_jobspy: bool = True,
):
    log("Starting pipeline")

    DATA_DIR.mkdir(exist_ok=True)

    boards = jobspy_boards or ["indeed", "google", "zip_recruiter"]
    boards_arg = ",".join(boards)

    if enable_feeds:
        step(
            "1/6 — Free feed fetch",
            run_py,
            str(BASE_DIR / "feed-fetcher" / "fetcher.py"),
            "--location",
            location,
            "--max-per-source",
            str(max_per_board),
            *keywords,
            cwd=str(BASE_DIR / "feed-fetcher"),
        )
    else:
        log("=== 1/6 — Free feed fetch (disabled by config) ===")

    if enable_jobspy:
        step(
            "2/6 — JobSpy board scrape",
            run_jobspy_py,
            str(BASE_DIR / "jobspy-wrapper" / "scrape.py"),
            "--location",
            location,
            "--results",
            str(max_per_board),
            "--boards",
            boards_arg,
            "--hours-old",
            str(jobspy_hours_old),
            "--country-indeed",
            jobspy_country_indeed,
            *keywords,
            cwd=str(BASE_DIR / "jobspy-wrapper"),
        )
    else:
        log("=== 2/6 — JobSpy board scrape (disabled by config) ===")

    if enable_ats:
        step(
            "3/6 — Career-ops ATS export",
            run_node,
            str(BASE_DIR / "pipeline" / "export_ats_lane.mjs"),
            str(BASE_DIR / "pipeline"),
            cwd=str(BASE_DIR / "pipeline"),
        )
    else:
        log("=== 3/6 — Career-ops ATS export (disabled by config) ===")

    step("4/6 — Merge + dedupe", run_py,
         str(BASE_DIR / "dedupe-merge" / "merger.py"))

    step("5/6 — Ingest merged jobs to career-ops", run_py,
         str(BASE_DIR / "pipeline" / "ingest_to_career_ops.py"))

    step("6/6 — Import external jobs into career-ops pipeline", run_npm,
         "import:external",
         cwd=str(CAREER_OPS_DIR))

    merged = DATA_DIR / "merged.json"
    if not merged.exists():
        log("Pipeline complete — no merged.json produced")
        return []

    with open(merged, encoding="utf-8") as fp:
        final = json.load(fp)

    out = DATA_DIR / f"pipeline_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    log(f"Pipeline complete -- {len(final)} unique jobs -> {out.name}")
    log("Workflow boundary reached: discovery, merge, handoff, and queue import completed. Downstream evaluation/PDF/tracker flow still runs inside career-ops.")
    return final

if __name__ == "__main__":
    config = load_pipeline_config()
    sources = config.get("sources") or {}
    jobspy_config = sources.get("jobspy") or {}
    keywords = sys.argv[1:] or config.get("keywords") or ["software engineer", "data engineer"]
    location = config.get("location", "Remote")
    max_per_board = int(config.get("max_per_source", 30))
    jobspy_boards = jobspy_config.get("boards") or ["indeed", "google", "zip_recruiter"]
    jobspy_hours_old = int(jobspy_config.get("hours_old", 168))
    jobspy_country_indeed = str(jobspy_config.get("country_indeed", "united arab emirates"))
    run_pipeline(
        keywords,
        location,
        max_per_board,
        jobspy_boards=jobspy_boards,
        jobspy_hours_old=jobspy_hours_old,
        jobspy_country_indeed=jobspy_country_indeed,
        enable_ats=bool((sources.get("ats") or {}).get("enabled", True)),
        enable_feeds=bool((sources.get("feeds") or {}).get("enabled", True)),
        enable_jobspy=bool(jobspy_config.get("enabled", True)),
    )
