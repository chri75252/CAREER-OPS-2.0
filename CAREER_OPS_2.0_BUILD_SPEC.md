# CAREER OPS 2.0 — Full Build Specification

> **Status:** Build in Progress  
> **Date:** 2026-04-18  
> **Goal:** Free, open-source, tweakable job-discovery stack that outperforms vanilla career-ops

---

## What This Tool Does

**Core capability:** Automatically discover jobs across multiple free sources → deduplicate → evaluate against your profile → generate tailored applications → track results.

One command runs everything: broad source discovery → merge → dedupe → AI-powered evaluation → ranked shortlist with ready-to-send CVs.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CAREER-OPS (Core)                        │
│         Evaluation · Matching · CV Generation · Tracking    │
└──────────────────────────┬──────────────────────────────────┘
                           │ feeds deduped jobs
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               DEDUPE + MERGE LAYER                          │
│    Hash on (url + title + company) → single job pool        │
└──────┬──────────────┬──────────────────┬───────────────────┘
       │              │                  │
       ▼              ▼                  ▼
  Lane 1          Lane 2             Lane 3
  ATS APIs        JobSpy             Free Feeds
  (Greenhouse,    (Indeed, LinkedIn, (RemoteOK, Remotive,
   Ashby, Lever)   Glassdoor, etc.)   WWR, Arbeitnow)
  ──────────      ──────────         ──────────
  Reliable,       Needs proxy +       Zero auth, stable,
  no anti-bot     rate controls       but fewer boards
```

---

## Recommended Tool Stack

| Tool | Repo | Stars | License | Role |
|------|------|-------|---------|------|
| **career-ops** | `santifer/career-ops` | 35,643 | MIT | Core: evaluation, matching, CV generation, tracking |
| **JobSpy** | `speedyapply/JobSpy` | 3,171 | MIT | Secondary: board scraping (LinkedIn, Indeed, Glassdoor, etc.) |
| **ever-jobs** | `ever-jobs/ever-jobs` | 31 | MIT | Optional: 160+ source aggregator (newer, less field-tested) |
| **stapply-ai/ats-scrapers** | `stapply-ai/ats-scrapers` | 90 | — | Optional: ATS-focused scraper library |

### Free Feed Sources (No Auth Required)
- RemoteOK JSON API — `remoteok.com/api`
- Remotive JSON API — `remotive.com/api/remote-jobs`
- Arbeitnow JSON API — `arbeitnow.com/api/job-board-api`
- We Work Remotely RSS — `weworkremotely.com/remote-jobs.rss`
- Jobicy JSON API — `jobicy.com/api`
- Python.org Jobs RSS — `python.org/jobs/feed`

---

## Evidence-Graded Confidence Matrix

| Tool | Confidence | Known Failure Modes | Evidence Links |
|------|-----------|---------------------|----------------|
| **career-ops** | HIGH | Scanner only hits 3 ATS APIs (Greenhouse/Ashby/Lever); Playwright/WebSearch tiers are agent-flow only, not `scan.mjs` runtime | [#339](https://github.com/santifer/career-ops/issues/339), [#230](https://github.com/santifer/career-ops/issues/230), [#294](https://github.com/santifer/career-ops/pull/294), [#354](https://github.com/santifer/career-ops/pull/354) |
| **JobSpy** | HIGH | 429/403 anti-bot blocks; ZipRecruiter throttles; Glassdoor 403 even with proxies; LinkedIn needs proxy rotation for deep pagination; rate limiter PR still open | [#283](https://github.com/speedyapply/JobSpy/issues/283), [#270](https://github.com/speedyapply/JobSpy/issues/270), [#324](https://github.com/speedyapply/JobSpy/issues/324), [#306](https://github.com/speedyapply/JobSpy/pull/306) |
| **ever-jobs** | MEDIUM | Newer project, lower long-term field history, unmerged architectural ambition | [Repo](https://github.com/ever-jobs/ever-jobs) |
| **stapply-ai/ats-scrapers** | MEDIUM | Smaller ecosystem, ATS-only scope | [Repo](https://github.com/stapply-ai/ats-scrapers) |
| **Feashliaa/job-board-aggregator** | LOW-MEDIUM | Few public issue/discussion pressure; large claims but thin battle-testing | [Repo](https://github.com/Feashliaa/job-board-aggregator) |

---

## Workflows

### Workflow 1: Daily Automated Discovery Run

```
You run one command (or cron triggers it)
       │
       ▼
┌─────────────────────────────────────────────────────┐
│  LANE 1: ATS APIs (Greenhouse/Ashby/Lever)          │
│  → Direct API calls, no scraping, no blocks          │
└─────────────────────┬───────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────┐
│  LANE 2: Free JSON/RSS feeds                         │
│  → RemoteOK, Remotive, Arbeitnow, WeWorkRemotely    │
│  → Simple HTTP fetch, no auth, no anti-bot           │
└─────────────────────┬───────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────┐
│  LANE 3: JobSpy (Indeed, LinkedIn, Google, etc.)    │
│  → Scraped with rate limits + proxy rotation        │
└─────────────────────┬───────────────────────────────┘
                      ▼
              DEDUPLICATION LAYER
         URL + title/company hash merge
                      │
                      ▼
           ┌────────────────────┐
           │  UNIFIED JOB POOL   │
           │  (no duplicates)    │
           └─────────┬──────────┘
                     ▼
        ┌──────────────────────────┐
        │    CAREER-OPS CORE       │
        │  Evaluation · Scoring    │
        │  CV Generation · Tracking│
        └──────────────────────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
   Ranked shortlist      Tailored CV/PDF
   per role/target       per job
```

### Workflow 2: Targeted Company Research

```
You specify: [Company A, Company B, Company C...] + [role title]
       │
       ▼
Career-ops scans each company's ATS (Greenhouse/Ashby/Lever)
       │
       ▼
Results evaluated against your profile
       │
       ▼
Sorted by match score → top matches flagged
       │
       ▼
CV regenerated/tailored per role → ready to apply
```

### Workflow 3: Broad Discovery Sweep

```
You specify: [keywords] + [location] + [remote preference]
       │
       ▼
JobSpy scrapes Indeed, LinkedIn, Google Jobs, ZipRecruiter
       │
       ▼
Free feeds (RemoteOK, Remotive, WWR) contribute additional listings
       │
       ▼
Deduped, merged, evaluated
       │
       ▼
Ranked shortlist (not limited to companies you already knew)
```

### Daily Usage Pattern

```
Every morning (or twice daily):
  1. Run pipeline → get fresh ranked jobs
  2. Review top 5-10 matches in career-ops dashboard
  3. Pick 1-3 to apply → career-ops generates tailored CV
  4. Submit → track in dashboard
```

**Time per day:** ~10-15 minutes to review and apply to top matches.

---

## Implementation Plan

### Phase 1: Base Install + Configure (Day 1)

| Step | Action | Effort |
|------|--------|--------|
| 1.1 | Install career-ops (`git clone` + `npm install`) | 10 min |
| 1.2 | Configure `portals.yml` with target companies | 30 min |
| 1.3 | Configure `profile.yml` with role/location preferences | 15 min |
| 1.4 | Verify `npm run scan` works against Greenhouse/Ashby/Lever | 15 min |
| 1.5 | Verify evaluation/matching modes work | 15 min |

### Phase 2: Free Feed Sources (Day 1-2)

| Step | Action | Effort |
|------|--------|--------|
| 2.1 | Create feed fetcher script (RemoteOK, Remotive, Arbeitnow, WWR) | 2-3 hrs |
| 2.2 | Normalize output to `{title, company, url, location, source}` | 1 hr |
| 2.3 | Test feed ingestion runs | 1 hr |

### Phase 3: JobSpy Integration (Day 2-3)

| Step | Action | Effort |
|------|--------|--------|
| 3.1 | Install JobSpy (`pip install jobspy`) | 5 min |
| 3.2 | Write JobSpy wrapper script with rate limits | 2-3 hrs |
| 3.3 | Add proxy config (rotate residential proxies for LinkedIn) | 1 hr |
| 3.4 | Normalize JobSpy output to shared schema | 1 hr |
| 3.5 | Test single-board scrape runs | 1 hr |

### Phase 4: Dedup + Merge Layer (Day 3)

| Step | Action | Effort |
|------|--------|--------|
| 4.1 | Build merge script (combine all lanes) | 1 hr |
| 4.2 | Implement hash-based dedupe (URL + title/company) | 1 hr |
| 4.3 | Test dedupe accuracy | 1 hr |

### Phase 5: Reliability Controls (Day 3-4)

| Step | Action | Effort |
|------|--------|--------|
| 5.1 | Per-source rate budgets + jitter | 1-2 hrs |
| 5.2 | Retry with exponential backoff on 429/403 | 1-2 hrs |
| 5.3 | Source isolation (one failure ≠ full stop) | 1 hr |
| 5.4 | Circuit breaker (skip source after 3x failure) | 1 hr |

### Phase 6: Orchestration Wiring (Day 4)

| Step | Action | Effort |
|------|--------|--------|
| 6.1 | Create single runner script (all lanes → dedupe → career-ops) | 2 hrs |
| 6.2 | Set up cron/Task Scheduler for daily runs | 30 min |
| 6.3 | End-to-end test run | 1 hr |

### Phase 7: Soak Test + Tune (Days 5-14)

| Step | Action | Effort |
|------|--------|--------|
| 7.1 | Run daily for 3-7 days | Passive |
| 7.2 | Monitor failure rates per source | Passive |
| 7.3 | Tune rate limits based on 429/403 frequency | 1-2 hrs |
| 7.4 | Adjust proxy rotation if needed | 1 hr |
| 7.5 | Demote consistently failing sources | 30 min |

---

## Total Effort Summary

| Phase | Hours |
|-------|-------|
| Phase 1: Base install | ~1.5 |
| Phase 2: Free feeds | ~4 |
| Phase 3: JobSpy | ~6 |
| Phase 4: Dedup/merge | ~3 |
| Phase 5: Reliability controls | ~5 |
| Phase 6: Orchestration | ~3.5 |
| Phase 7: Soak test | ~5 |
| **Total** | **~28 hours** |

**Timeline:** ~2-3 weeks at ~1-2 hrs/day. Can be compressed to 3-5 focused days.

---

## File Structure

```
CARRER OPS 2.0/
├── career-ops/                    # Core evaluation/matching engine (git clone)
│   ├── scan.mjs                   # ATS scanner (Greenhouse/Ashby/Lever)
│   ├── modes/                     # Career-ops workflow modes
│   ├── templates/                 # Config templates
│   └── ...
│
├── jobspy-wrapper/                # JobSpy integration layer
│   ├── scrape.py                  # Main JobSpy wrapper script
│   ├── proxies.txt                # Proxy list (optional)
│   └── requirements.txt           # Python dependencies
│
├── feed-fetcher/                  # Free RSS/JSON feed ingestion
│   ├── fetcher.py                 # Multi-source feed fetcher
│   └── sources.py                 # Feed source definitions
│
├── dedupe-merge/                  # Deduplication + merge layer
│   ├── dedupe.py                  # Hash-based dedupe logic
│   └── merger.py                  # Merge all lanes into unified pool
│
├── pipeline/                      # Orchestration
│   ├── run_pipeline.py            # Main runner: all lanes → dedupe → career-ops
│   └── schedule.yaml              # Cron/scheduler config
│
├── config/                        # Shared configuration
│   ├── profile.yml                # Your CV/role targeting (career-ops)
│   ├── portals.yml                # Target companies (career-ops)
│   └── pipeline.yaml              # Source priorities, rate limits, thresholds
│
└── README.md                      # This file
```

---

## Key Constraints

- **Zero paid APIs** — all sources are free or self-hosted
- **MIT license** — all core tools are MIT-licensed
- **Proxy costs** — optional for JobSpy heavy usage; can run without proxies at reduced volume
- **No career-ops core modifications** — all changes are additive wrappers/config

---

## Known Limitations

1. **Career-ops scanner gap:** `scan.mjs` only hits 3 ATS APIs — broader search via JobSpy and feeds
2. **JobSpy anti-bot:** Real 429/403 issues documented in GitHub; proxy rotation required for reliable long-run
3. **Rate limiter PR open:** JobSpy PR #306 (thread-safe rate limiting) not yet merged — must implement externally
4. **Dedup accuracy:** Hash-based dedupe may miss near-duplicates with slightly different titles
5. **Source drift:** Free APIs and RSS feeds can change format or go offline without notice

---

## Success Criteria

| Checkpoint | Criteria |
|------------|----------|
| **Day 3** | Pipeline runs end-to-end without full-stop failures; each source isolated |
| **Day 7** | Stable daily throughput; retry/backoff reducing 429/403 recurrence |
| **Day 14** | Consistent output quality; low duplicate drift; no daily babysitting required |
| **Gate** | If a source fails 3x consecutively, auto-demote it; continue with remaining sources |

---

## Research Provenance

All recommendations validated against live GitHub data:

- Career-ops repo metadata + issues: [#339](https://github.com/santifer/career-ops/issues/339), [#230](https://github.com/santifer/career-ops/issues/230), [#294](https://github.com/santifer/career-ops/pull/294), [#354](https://github.com/santifer/career-ops/pull/354)
- JobSpy repo metadata + issues: [#283](https://github.com/speedyapply/JobSpy/issues/283), [#270](https://github.com/speedyapply/JobSpy/issues/270), [#324](https://github.com/speedyapply/JobSpy/issues/324), [#306](https://github.com/speedyapply/JobSpy/pull/306)
- Ever-jobs: [api.github.com/repos/ever-jobs/ever-jobs](https://api.github.com/repos/ever-jobs/ever-jobs)
- Stapply: [api.github.com/repos/stapply-ai/ats-scrapers](https://api.github.com/repos/stapply-ai/ats-scrapers)
- Feashliaa: [api.github.com/repos/Feashliaa/job-board-aggregator](https://api.github.com/repos/Feashliaa/job-board-aggregator)
