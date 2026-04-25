# Graph Report - .  (2026-04-25)

## Corpus Check
- Large corpus: 160 files · ~1,545,178 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder, or use --no-semantic to run AST-only.

## Summary
- 415 nodes · 623 edges · 39 communities detected
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 36 edges (avg confidence: 0.75)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `PipelineModel` - 30 edges
2. `DiscoveryModel` - 21 edges
3. `profile.yml (User Identity)` - 14 edges
4. `ProgressModel` - 12 edges
5. `ViewerModel` - 12 edges
6. `WorkflowStatusModel` - 11 edges
7. `Application Tracker` - 11 edges
8. `Career-Ops System` - 11 edges
9. `fetch_all()` - 9 edges
10. `German Geteilter Kontext` - 9 edges

## Surprising Connections (you probably didn't know these)
- `Christian Haddad CV - Datadog Application` --referenced_by--> `Career-Ops System`  [INFERRED]
  career-ops/output/cv-christian-haddad-datadog-20260421.pdf → README.md
- `Career-Ops Roadmap Phases` --conceptually_related_to--> `Career-Ops System`  [INFERRED]
  career-ops/docs/roadmap-phases.jpg → README.md
- `Career-Ops Hero Banner` --conceptually_related_to--> `Career-Ops System`  [EXTRACTED]
  career-ops/docs/hero-banner.jpg → README.md
- `Career-Ops OG Image` --conceptually_related_to--> `Career-Ops System`  [EXTRACTED]
  career-ops/docs/og-image.jpg → README.md
- `Career-Ops Vision Banner` --conceptually_related_to--> `Career-Ops System`  [EXTRACTED]
  career-ops/docs/vision-banner.jpg → README.md

## Communities

### Community 0 - "Pipeline UI Models"
Cohesion: 0.09
Nodes (13): NewPipelineModel(), statusLabel(), truncateRunes(), PipelineClosedMsg, PipelineLoadReportMsg, PipelineModel, PipelineOpenProgressMsg, PipelineOpenReportMsg (+5 more)

### Community 1 - "Discovery Data Models"
Cohesion: 0.09
Nodes (17): clampCursorByURL(), clampResultCursorByURL(), fallback(), max(), ParseDiscovery(), ParseExternalJobs(), ParsePendingQueue(), ParseQueueRankings() (+9 more)

### Community 2 - "Career-Ops Modes & Data"
Cohesion: 0.07
Nodes (40): article-digest.md (Proof Points), batch-input.tsv (Batch Input), batch-prompt.md (Worker Prompt), batch-state.tsv (Batch Progress), Batch README, batch/tracker-additions/ (TSV Output), portals.yml (Scanner Config), workflow_gates Config (+32 more)

### Community 3 - "Internationalization (DE/FR/JA/PT/RU)"
Cohesion: 0.19
Nodes (29): profile.yml (User Identity), Application Tracker, URL Inbox Second Brain, German Modes README, German Geteilter Kontext, German Angebotsbewertung Mode, German Bewerben Form Assistant, German Pipeline URL Inbox Mode (+21 more)

### Community 4 - "Dashboard Tests"
Cohesion: 0.09
Nodes (5): buildTestModel(), TestKeyFiveOpensTrackProgress(), TestPrimarySectionKeysAndHelpRouting(), TestWorkflowKeysOpenDedicatedStatusScreens(), Theme

### Community 5 - "Project Documentation"
Cohesion: 0.11
Nodes (17): career-ops/AGENTS.md, career-ops/article-digest.md, career-ops/CAREER_OPS_CHEAT_SHEET.md, career-ops/CLAUDE.md, career-ops/CODE_OF_CONDUCT.md, career-ops/CAREER_OPS_CONCISE_GUIDE.md, career-ops/CONTRIBUTING.md, career-ops/cv.md (Christian Haddad) (+9 more)

### Community 6 - "Career Data Processing"
Cohesion: 0.13
Nodes (22): cleanTableCell(), ComputeMetrics(), ComputeProgressMetrics(), enrichAppURLsByCompany(), enrichFromScanHistory(), loadBatchInputURLs(), loadJobURLs(), LoadReportSummary() (+14 more)

### Community 7 - "Table Viewer Models"
Cohesion: 0.2
Nodes (6): ViewerClosedMsg, ViewerModel, computeColumnWidths(), isTableLine(), isTableSeparator(), parseTableCells()

### Community 8 - "Job Feed Fetcher"
Cohesion: 0.17
Nodes (16): fetch_all(), fetch_arbeitnow(), fetch_jobicy(), fetch_python_jobs(), fetch_remoteok(), fetch_remotive(), fetch_weworkremotely(), job_key() (+8 more)

### Community 9 - "Workflow Status Screen"
Cohesion: 0.25
Nodes (13): WorkflowStatusClosedMsg, WorkflowStatusRefreshMsg, countChecklistRows(), countTSVRows(), latestFileInfo(), loadApplyStatus(), loadBatchStatus(), loadDeepStatus() (+5 more)

### Community 10 - "Progress Models"
Cohesion: 0.2
Nodes (2): ProgressClosedMsg, ProgressModel

### Community 11 - "Career-Ops System (Branding)"
Cohesion: 0.13
Nodes (15): Ashby ATS, ATS PDF Generation, Career-Ops System, Christian Haddad CV - Datadog Application, Dashboard TUI, Career-Ops Demo Animation, Greenhouse ATS, Career-Ops Hero Banner (+7 more)

### Community 12 - "Dashboard App Models"
Cohesion: 0.21
Nodes (5): appModel, viewState, wfItem, renderWorkflowBar(), renderWorkflowShell()

### Community 13 - "Help Screen Models"
Cohesion: 0.23
Nodes (5): capabilityBadge(), renderHelpShell(), trunc(), HelpClosedMsg, HelpModel

### Community 14 - "Evaluation Framework"
Cohesion: 0.17
Nodes (12): Archetype Detection, Christian Candidate Profile, Dashboard TUI, Datadog Staff AI Engineer Evaluation, Implementation Manager Role, Pipeline Integrity, Scripts Reference, Six-Block Evaluation Framework (+4 more)

### Community 15 - "Workflow Status UI Models"
Cohesion: 0.27
Nodes (1): WorkflowStatusModel

### Community 16 - "Pipeline Orchestrator"
Cohesion: 0.4
Nodes (9): log(), run_jobspy_py(), run_node(), run_npm(), run_pipeline(), run_py(), step(), write_stderr() (+1 more)

### Community 17 - "Workflow Section Models"
Cohesion: 0.29
Nodes (4): WorkflowCapability, WorkflowSection, WorkflowSectionStatus, WorkflowStatusItem

### Community 18 - "JobSpy Scraper"
Cohesion: 0.57
Nodes (6): job_key(), main(), normalize_job(), output_path(), scrape_for_keyword(), write_jobs()

### Community 19 - "Merger & Dedupe"
Cohesion: 0.7
Nodes (4): dedupe(), job_key(), load_json(), merge_sources()

### Community 20 - "Workflow Reports"
Cohesion: 0.67
Nodes (3): Workflow Truth Cheat Sheet, Workflow Forensic Report, Workflow Redesign Report

### Community 21 - "Temp: Pipeline Utils"
Cohesion: 1.0
Nodes (0): 

### Community 22 - "Theme: Catppuccin Mocha"
Cohesion: 1.0
Nodes (0): 

### Community 23 - "Theme: Catppuccin Latte"
Cohesion: 1.0
Nodes (0): 

### Community 24 - "Ingest to Career-Ops"
Cohesion: 1.0
Nodes (0): 

### Community 25 - "Dashboard Truth Reports"
Cohesion: 1.0
Nodes (0): 

### Community 26 - "PolyAI Agent Design Evals"
Cohesion: 1.0
Nodes (2): PolyAI Agent Design Manager Evaluation, PolyAI Agent Designer Evaluation

### Community 27 - "PolyAI Account Mgmt Evals"
Cohesion: 1.0
Nodes (2): PolyAI Account Manager Evaluation, PolyAI Channel Account Manager Evaluation

### Community 28 - "Setup & Customization Guides"
Cohesion: 1.0
Nodes (2): Customization Guide, Setup Guide

### Community 29 - "Greenhouse ATS & Test"
Cohesion: 1.0
Nodes (2): Greenhouse ATS, Test Run Report

### Community 30 - "Pipeline Analysis"
Cohesion: 1.0
Nodes (0): 

### Community 31 - "Graphify Run Script"
Cohesion: 1.0
Nodes (0): 

### Community 32 - "Temp: Probe Utils"
Cohesion: 1.0
Nodes (0): 

### Community 33 - "Changelog"
Cohesion: 1.0
Nodes (1): career-ops/CHANGELOG.md

### Community 34 - "Ofertas Mode"
Cohesion: 1.0
Nodes (1): Ofertas Mode (Multi-Offer Comparison)

### Community 35 - "Project Mode"
Cohesion: 1.0
Nodes (1): Project Mode (Portfolio Evaluation)

### Community 36 - "Training Mode"
Cohesion: 1.0
Nodes (1): Training Mode (Cert Evaluation)

### Community 37 - "Profile Template"
Cohesion: 1.0
Nodes (1): _profile.template.md (Profile Template)

### Community 38 - "PolyAI Director Compliance"
Cohesion: 1.0
Nodes (1): PolyAI Director of Compliance Evaluation

## Knowledge Gaps
- **95 isolated node(s):** `viewState`, `wfItem`, `batchEntry`, `CareerApplication`, `PipelineMetrics` (+90 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Temp: Pipeline Utils`** (2 nodes): `tmp_parse_discovery.go`, `main()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Theme: Catppuccin Mocha`** (2 nodes): `catppuccin.go`, `newCatppuccinMocha()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Theme: Catppuccin Latte`** (2 nodes): `catppuccin_latte.go`, `newCatppuccinLatte()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Ingest to Career-Ops`** (2 nodes): `ingest_to_career_ops.py`, `main()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Truth Reports`** (2 nodes): `DASHBOARD_ROOT_CAUSE_FIX_FINAL_REPORT_20260420.md`, `DASHBOARD_TRUTH_IMPLEMENTATION_TEST_REPORT_20260420.md`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `PolyAI Agent Design Evals`** (2 nodes): `PolyAI Agent Design Manager Evaluation`, `PolyAI Agent Designer Evaluation`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `PolyAI Account Mgmt Evals`** (2 nodes): `PolyAI Account Manager Evaluation`, `PolyAI Channel Account Manager Evaluation`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Setup & Customization Guides`** (2 nodes): `Customization Guide`, `Setup Guide`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Greenhouse ATS & Test`** (2 nodes): `Greenhouse ATS`, `Test Run Report`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Pipeline Analysis`** (1 nodes): `analyze-pipeline.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Graphify Run Script`** (1 nodes): `_graphify_run.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Temp: Probe Utils`** (1 nodes): `tmp_probe.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Changelog`** (1 nodes): `career-ops/CHANGELOG.md`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Ofertas Mode`** (1 nodes): `Ofertas Mode (Multi-Offer Comparison)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Project Mode`** (1 nodes): `Project Mode (Portfolio Evaluation)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Training Mode`** (1 nodes): `Training Mode (Cert Evaluation)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Profile Template`** (1 nodes): `_profile.template.md (Profile Template)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `PolyAI Director Compliance`** (1 nodes): `PolyAI Director of Compliance Evaluation`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `viewState`, `wfItem`, `batchEntry` to the rest of the system?**
  _95 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Pipeline UI Models` be split into smaller, more focused modules?**
  _Cohesion score 0.09 - nodes in this community are weakly interconnected._
- **Should `Discovery Data Models` be split into smaller, more focused modules?**
  _Cohesion score 0.09 - nodes in this community are weakly interconnected._
- **Should `Career-Ops Modes & Data` be split into smaller, more focused modules?**
  _Cohesion score 0.07 - nodes in this community are weakly interconnected._
- **Should `Dashboard Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.09 - nodes in this community are weakly interconnected._
- **Should `Project Documentation` be split into smaller, more focused modules?**
  _Cohesion score 0.11 - nodes in this community are weakly interconnected._
- **Should `Career Data Processing` be split into smaller, more focused modules?**
  _Cohesion score 0.13 - nodes in this community are weakly interconnected._