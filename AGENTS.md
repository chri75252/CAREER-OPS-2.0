# AGENTS.md

Authoritative contributor guide for Career-Ops 2.0 — the Multi-Agent Job Search System. This file is the authoritative project core. It covers architecture, verification protocols, mode system wiring, data contracts, and operational constraints for this repository.

---

## 0. ABSOLUTE RULES (CRITICAL)

- **NO PROACTIVE SCRIPT EDITS**
  NEVER proactively edit any script, configuration, or structural file if the user explicitly instructs "DO NOT EDIT ANY FILES/SCRIPTS FOR NOW" or gives a similar directive to only investigate/report. Do not ignore this instruction under *any* circumstances, even if you spot an obvious or trivial bug. Report the issue and WAIT for explicit permission to edit.

- **NEVER POST EVALUATION TEXT IN CHAT**
  For single-evaluation runs (`/career-ops` with JD text provided), produce Blocks A-G per `modes/oferta.md` and write outputs **only to files** (report + conditional HTML + tracker TSV). Do not post the evaluation text in chat.

- **READ REQUIRED GROUNDING FILES FIRST**
  Before any evaluation or mode run, read: `cv.md`, `config/profile.yml`, `modes/_profile.md`, `templates/states.yml`. These are the data contract foundation.

### 0.1 Evidence Collection Order (Tool Routing Policy)

Follow this default tool order when investigating or implementing tasks:

1. **Everything (`es`)** — file/path discovery when path is unknown.
2. **Graphify** — fast high-signal architecture overview before reading individual files. Read `graphify-out/GRAPH_REPORT.md` for god nodes and community structure.
3. **GitNexus** — symbol/process/impact analysis before any meaningful edit; **mandatory before rename, extract, refactor, or blast-radius work**.
4. **grep / read / LSP** — direct proof of actual file content.
5. **CRG** — structural/community/review context only **after scope is bounded**; never first-pass discovery.
6. **Context7** — external library/API docs when tool or library behavior is uncertain; jump forward when implementing unfamiliar APIs.
7. **Playwright** — live browser truth when UI/DOM/runtime behavior is the source of truth; jump forward when browser assumptions are the question.
8. **claude-mem / Supermemory** — **conditional only**. Use Supermemory only for continuity, prior rationale, or explicit handoff recovery. Do not use it as primary evidence when current code/logs/files are available.

**Reorder Triggers:**
- If path already known: Skip Everything.
- If live DOM/selector validity in question: Playwright jumps to position 2-3.
- If unfamiliar library implementation: Context7 jumps to position 3-4.
- If refactor/rename/blast-radius work: GitNexus jumps to position 1.
- If trivial content search: Skip Graphify/GitNexus, go to grep/read.

### 0.2 OpenCode Custom Registry

Custom OpenCode assets currently available and intended for active use:

- **Agents** (`C:\Users\chris\.config\opencode\agents\`):
  - `deep-research-agent`
  - `root-cause-analyst`
  - `system-architect`
  - `business-panel-experts`
- **Commands** (`C:\Users\chris\.config\opencode\command\`):
  - `/sc-research`
  - `/sc-product-brief`
  - `/sc-brainstorm`

Usage guidance:
- Use `/sc-research` for broad external research and source-ranked synthesis.
- Use `/sc-product-brief` when turning ideas into execution-ready briefs.
- Use `/sc-brainstorm` for structured ideation and prioritized options.
- Prefer `root-cause-analyst` for failure analysis, `system-architect` for architecture tradeoffs, and `business-panel-experts` for strategic decision framing.

**Note:** OpenCode global/tool registry content belongs in global `agents.md` appendices. Project-level OpenCode notes belong in this file (Section 0.2). Never move OpenCode-specific content into `CLAUDE.md` — that file is for Claude bootstrap only.

---

## 1. Verification, Backup, and Update Protocols

### 1.1 Mandatory Verification Protocols

- **NO_CLAIMS_WITHOUT_VERIFICATION**
  Never claim that a task is done without reproducible, file-grounded proof.

- **FILE_VERIFICATION** — For any path you reference in code review, docs, or analysis:
  1. **VERIFY_EXISTENCE** — Check that the file/directory actually exists.
  2. **CHECK_TIMESTAMP** — Confirm timestamps are consistent with the workflow described.
  3. **VERIFY_CONTENT** — Read and analyze file content before making assertions about behaviour.
  4. **USE_ABSOLUTE_PATHS** — When describing locations, use full paths rooted at `C:\idrive -carlo\Cloud-Drive_carloboul57@gmail.com\Cloud-Drive\Full\CARRER OPS 2.0\`.
  5. **NO ASSUMPTIONS** — Do not reference files or settings you have not actually opened.

### 1.2 Backup Protocol (Critical)

Before editing code, configuration, or key documentation:

1. **CREATE_BACKUP_DIR** — Under the repo root, create `backup/<reason>_<YYYYMMDD>/`.
2. **COPY_ALL_AFFECTED** — Copy every file you plan to modify into that directory.
3. **VERIFY_BACKUP** — Confirm backup files exist and have non-zero length before editing.
4. **CREATE REVERT_TRACKING** — Write `REVERT_TRACKING.md` mapping each file to its change scope, backup path, and validation status.

### 1.3 Update Protocol — Cascading Changes

When you change any code, path, or configuration:

1. **CASCADING_UPDATES**
   - Check all files that reference the modified symbol or path (use `rg` + LSP references).
   - Update mode files if behaviour changes.
2. **DOCUMENTATION_SYNC**
   - Update `AGENTS.md` when high-level workflow or structure changes.
   - Update `CLAUDE.md` and `CAREER_OPS_CONCISE_GUIDE.md` to keep human and tool guidance coherent.
   - Update relevant `docs/` pages if they have diverged from actual code paths.
3. **PATH_CONSISTENCY**
   - Verify that `config/profile.yml` and `config/workflow.yml` reflect any path changes.
   - Check that the dashboard still resolves the same output locations.

### 1.4 Atomic Save and Resume Semantics

The system is intentionally **file-grounded** and **resumable**:

- Resume pointers in `data/pipeline.md` and `data/applications.md` must only advance; do not reduce them manually.
- All critical writes to `data/`, `reports/`, and `output/` should use atomic patterns (temp file -> rename) where possible.
- When repairing or migrating state, always back up the original file under `backup/<reason>_<YYYYMMDD>/`.

### 1.5 Agreed Implementation Workflow Additions (Word-For-Word)

The following instruction text is intentionally preserved word-for-word from agreed outcomes:

- "Before any non-trivial implementation, produce a surgical plan for user review that names target files, minimum required fixes, explicit non-goals, edit order, validation order, and rollback scope."
- "Create `backup/<reason>_<YYYYMMDD>/REVERT_TRACKING.md` before edits; list each planned file, intended scope, planned validation, and exact restore source paths."
- "When notes, handoffs, memory, and code disagree, current code plus concrete artifacts/logs/outputs are the source of truth; stale handoffs must be marked superseded, not trusted."
- "After compaction or multi-session interruption, update `.sisyphus/notepads/handoff/session_handoff.md` with authoritative current state, superseded claims, completed work, open questions, next checks, and backup location."
- "For surgical passes, follow explicit step order: evidence gathering -> plan/review -> backup + revert tracker -> implementation -> targeted verification -> docs/memory updates only if verified and approved."
- "In plans and reports, separate minimum required fixes from supporting corrections and optional mitigations; do not present plausible mitigations as mandatory work."
- "Immediately after a compaction event or session resume, you MUST read the latest handoff to re-anchor context and explicitly ignore stale prior interpretations."
- "Create a `REVERT_TRACKING.md` in the backup directory for every implementation pass, mapping each file to its specific change scope, backup path, and validation status."
- "Execute implementation tasks in the exact order specified in the approved plan to maintain dependency integrity and prevent cascading failures."
- "Verify all claims using triangulation across code, logs, and raw run artifacts rather than relying on single-source assertions or heuristic previews."
- "Before editing, generate a surgical implementation plan for review that identifies the minimum necessary changes to address the root cause without over-scoping."
- "Perform verification (LSP, compilation, and targeted sanity checks) after each logical phase of implementation, not just at the end of the session."
- "When internal agent reports or prior handoffs conflict, the current codebase and raw run artifacts are the only authoritative tie-breakers."

---

## 2. Architecture Overview (Code-Grounded)

### 2.1 System Structure

Career-Ops 2.0 is a multi-agent job search system with three technology layers:

| Layer | Technology | Primary Files | Purpose |
|-------|-----------|---------------|---------|
| **Dashboard** | Go + Bubble Tea TUI | `dashboard/main.go`, `dashboard/internal/` | Real-time status viewer |
| **Workflow Engine** | Node.js + Playwright | `career-ops/*.mjs`, `modes/*.md` | Mode execution, PDF gen, portal scan |
| **Discovery Pipeline** | Python | `pipeline/run_pipeline.py`, `feed-fetcher/`, `jobspy-wrapper/`, `dedupe-merge/` | External job ingestion |

### 2.2 Primary Entry Points

**Dashboard (Go TUI):**
- `career-ops/dashboard/main.go` — Dashboard entry point
- Reads: `data/pipeline.md`, `data/external_jobs.json`, `data/queue-ranking.json`, `data/applications.md`
- Screens: Pipeline, Discovery, Progress, Workflow Status, Viewer, Help

**Workflow Scripts (Node.js):**
- `career-ops/scan.mjs` — Zero-token portal scanner (45+ companies)
- `career-ops/rank-queue.mjs` — Deterministic queue ranking (2026-04-24 redesign)
- `career-ops/import-external-jobs.mjs` — Imports discovery results to `data/pipeline.md`
- `career-ops/generate-pdf.mjs` — Playwright HTML-to-PDF (ATS-optimized)
- `career-ops/merge-tracker.mjs` — TSV tracker merge
- `career-ops/package.json` — 24 npm scripts

**Discovery Pipeline (Python):**
- `pipeline/run_pipeline.py` — Orchestrates feed-fetch -> JobSpy scrape -> dedupe-merge
- `feed-fetcher/fetcher.py` — Fetches from remote job feeds
- `jobspy-wrapper/scrape.py` — JobSpy scraping wrapper
- `dedupe-merge/merger.py` — Deduplication and merge logic

### 2.3 Mode System

The core of Career-Ops is the **mode** system — 16 markdown files under `career-ops/modes/` that define agent behaviour:

| Mode | File | Purpose |
|------|------|---------|
| `_shared.md` | System context | Archetypes, scoring A-F+G, data contract |
| `_profile.md` | User personalization | Christian Haddad profile layer |
| `oferta.md` | Single evaluation | 6-Block A-G evaluation (primary mode) |
| `auto-pipeline.md` | Full auto-pipeline | End-to-end: URL -> eval -> apply -> track |
| `pipeline.md` | URL inbox | Process pending URLs from `data/pipeline.md` |
| `scan.md` | Portal scanner | Configure and run `scan.mjs` |
| `batch.md` | Batch processing | Massive multi-offer processing |
| `apply.md` | Live form assistant | Real-time application form help |
| `pdf.md` | ATS CV generation | Playwright HTML-to-PDF with `generate-pdf.mjs` |
| `deep.md` | Company research | Deep-dive research on target companies |
| `tracker.md` | Application tracker | Status tracking via `data/applications.md` |
| `interview-prep.md` | Interview prep | STAR+R story bank and preparation |
| `followup.md` | Cadence tracker | Follow-up timing and outreach |
| `contacto.md` | LinkedIn outreach | Professional networking scripts |
| `patterns.md` | Rejection detector | Pattern analysis on application outcomes |
| `ofertas.md` | Multi-offer comparison | Side-by-side offer evaluation |

**Internationalization:** 5 language packs under `career-ops/modes/{de,fr,ja,pt,ru}/` — each mirrors the EN mode structure with localized vocabulary.

### 2.4 Data Contract

The authoritative data contract is in `career-ops/DATA_CONTRACT.md`. Key files:

- `career-ops/cv.md` — Candidate CV (Christian Haddad)
- `career-ops/config/profile.yml` — User identity, archetypes, targeting
- `career-ops/config/workflow.yml` — Ranking weights, workflow gates, thresholds
- `career-ops/data/pipeline.md` — URL queue inbox (Pendientes/Procesadas sections)
- `career-ops/data/applications.md` — Application tracker (TSV-compatible)
- `career-ops/data/external_jobs.json` — Discovery results ledger
- `career-ops/data/queue-ranking.json` — Ranking metadata sidecar
- `career-ops/reports/` — Evaluation reports (numbered, dated)
- `career-ops/output/` — Generated PDFs and HTML drafts

---

## 3. Configuration Management

### 3.1 User Profile (`config/profile.yml`)

Primary identity configuration:

- `identity` — Name, location, visa status, languages
- `targeting` — Role types, seniority, geo preferences, salary bands
- `archetypes` — 6 role archetypes (e.g., Solutions Engineer, TAM)
- `language` — Primary language, modes directory, activation method

**Rule:** Always read `config/profile.yml` before any evaluation or mode run. It drives archetype detection and scoring weights.

### 3.2 Workflow Configuration (`config/workflow.yml`)

Controls the evaluation and application pipeline:

- `ranking.weights` — Company, role, location, compensation, culture weights
- `workflow_gates` — Thresholds for auto-apply, deep-research, PDF generation
- `scoring` — A-F grade boundaries and G (gut feel) inclusion rules

### 3.3 Scanner Configuration (`portals.yml`)

Portal scanner configuration with 45+ companies:

- `portals` — List of Greenhouse/Ashby/Lever boards with URLs
- `title_filters` — Include/exclude regex patterns
- `scan_intervals` — Cooldown between scans

---

## 4. Evaluation Framework (6-Block A-F + G)

Reference: `career-ops/modes/_shared.md` and `career-ops/modes/oferta.md`

### 4.1 Scoring System

| Grade | Meaning | Threshold |
|-------|---------|-----------|
| A | Exceptional fit | 90-100 |
| B | Strong fit | 80-89 |
| C | Viable fit | 70-79 |
| D | Marginal fit | 60-69 |
| E | Poor fit | 50-59 |
| F | Reject | <50 |
| G | Gut feel override | Binary (yes/no) |

### 4.2 Six Evaluation Blocks

1. **Block A: Role Fit** — JD alignment with archetypes and experience
2. **Block B: Company Fit** — Stage, culture, growth trajectory
3. **Block C: Compensation** — Base, equity, benefits vs. requirements
4. **Block D: Location** — Remote, relocation, visa sponsorship
5. **Block E: Career Impact** — Learning, network, trajectory
6. **Block F: Risk Assessment** — Red flags, stability, execution risk
7. **Block G: Gut Feel** — Intuition override (independent of scores)

### 4.3 Evaluation Outputs

Each evaluation produces:
- `reports/###-<company>-<role>-<YYYYMMDD>.md` — Full report
- `output/<company>-<role>-<date>.pdf` — ATS-optimized PDF (if score >= B)
- `data/applications.md` — Tracker TSV entry appended

---

## 5. Dashboard Architecture

Reference: `career-ops/dashboard/`

### 5.1 Dashboard Screens

| Screen | File | Data Source |
|--------|------|-------------|
| Pipeline | `internal/screens/pipeline.go` | `data/pipeline.md` |
| Discovery | `internal/screens/discovery.go` | `data/external_jobs.json`, `data/queue-ranking.json` |
| Progress | `internal/screens/progress.go` | `data/applications.md` |
| Workflow Status | `internal/screens/workflow_status.go` | `reports/`, `output/` |
| Viewer | `internal/screens/viewer.go` | Report markdown files |
| Help | `internal/screens/help.go` | Static help text |

### 5.2 Dashboard Data Layer

- `internal/data/discovery.go` — Reads pipeline.md + external_jobs.json + queue-ranking.json
- `internal/data/workflow_status.go` — PDF/Deep/Batch/Apply status loaders
- `internal/model/` — Structs: PendingJob, ExternalJob, QueueRankingItem, WorkflowSection

### 5.3 Key Go Packages

- `github.com/charmbracelet/bubbletea` — TUI framework
- `github.com/charmbracelet/lipgloss` — Styling
- `github.com/charmbracelet/bubbles` — UI components

---

## 6. Browser Automation (Playwright)

### 6.1 Playwright Usage

Career-Ops uses Playwright for two purposes:

1. **PDF Generation** (`generate-pdf.mjs`) — Renders `cv-template.html` to ATS-optimized PDF
2. **Portal Scanning** — Not used directly; `scan.mjs` uses zero-token HTTP requests

### 6.2 PDF Generation Pipeline

- Template: `templates/cv-template.html`
- Script: `career-ops/generate-pdf.mjs`
- Output: `career-ops/output/cv-<name>-<company>-<date>.pdf`
- Dependencies: `playwright`, `js-yaml` (see `package.json`)

### 6.3 Running Node.js Scripts

All scripts are invoked via npm:

```bash
npm run scan          # Run portal scanner
npm run rank          # Run queue ranking
npm run pdf           # Generate PDF
npm run batch         # Run batch processing
npm run pipeline:verify  # Verify pipeline integrity
```

See `career-ops/package.json` for the full script list.

---

## 7. Coding Standards and Development Practices

### 7.1 Go (Dashboard)

- **Version** — Go 1.21+
- **Style** — `gofmt`, `go vet`
- **Structure** — Standard Go project layout under `dashboard/`
- **Testing** — `go test ./...`

### 7.2 Node.js (Workflow Scripts)

- **Version** — Node.js 18+
- **Style** — No enforced linter; follow existing patterns
- **Key pattern** — Scripts read YAML configs via `js-yaml`, write markdown/TSV/JSON outputs

### 7.3 Python (Discovery Pipeline)

- **Version** — Python 3.11+
- **Dependencies** — See `pipeline/requirements.txt`
- **Entry point** — `python pipeline/run_pipeline.py`

### 7.4 General Rules

- **Minimal blast radius** — Keep changes focused; follow update protocols above.
- **No committed secrets** — API keys and credentials in env vars or ignored files.
- **File-grounded** — All state in files, not memory. Dashboard reads directly from disk.

---

## 8. Testing and Quality Gates

### 8.1 Go Dashboard Tests

```bash
cd career-ops/dashboard
go test ./...
```

### 8.2 Node.js Scripts

No automated test suite. Verify by:
1. Running `npm run <script>` with `--dry-run` where supported
2. Checking output files exist and are well-formed
3. Validating `data/pipeline.md` and `data/applications.md` parse correctly

### 8.3 Python Pipeline

```bash
python pipeline/run_pipeline.py --dry-run
```

### 8.4 Manual Verification Checklist

After any change to modes, data contract, or scripts:
- [ ] `data/pipeline.md` parses without errors
- [ ] `data/applications.md` TSV rows are valid
- [ ] Dashboard displays all screens correctly
- [ ] `npm run scan` returns expected portal count
- [ ] `npm run rank` produces valid `queue-ranking.json`

---

## 9. Memory and Documentation Update Policy

### 9.1 When to Update Memory and Documentation

**Update ONLY after code changes are VERIFIED:**
- Tests pass or manual verification complete
- Code is stable (not during active development that may revert)

**Never update during:**
- Active debugging sessions
- Experimental feature development
- Before changes are committed and tested

### 9.2 Verification Gate

Before updating memory or documentation:

1. **Complete changes** -> Code is written and tested
2. **Run verification** -> `go test`, manual script test, or dashboard check
3. **User confirmation** -> Explicit "Update memory" approval
4. **Update documentation** -> Update relevant docs/*.md files
5. **Update Supermemory** -> Add new granular memories via supermemory(mode="add", ...)

### 9.3 Staging Area

Draft memory updates in `docs/_MEMORY_STAGING.md` before promoting to:
- Canonical documentation (docs/*.md)
- Supermemory entries (permanent knowledge)

---

## 10. Memory Retrieval Policy (Supermemory vs Serena MCP)

### 10.1 When to Query Supermemory

Query Supermemory **immediately after understanding the task**, before planning implementation:

| Query Type | Example | Why |
|------------|---------|-----|
| Architecture | `dashboard discovery model` | Get file structure and patterns |
| Error patterns | `pipeline parse error` | Find known fixes |
| Configuration | `profile.yml archetypes` | Check project settings |
| Policies | `mode evaluation rules` | Verify constraints |
| Workflows | `batch processing steps` | Understand flow |

**Supermemory contains**: Architecture, error-solutions, configs, policies, patterns.

### 10.2 When to Query Serena MCP

Query Serena MCP **only when you need historical context**:

| Query Type | Example | Why |
|------------|---------|-----|
| Root cause | `dashboard truth fix` | Full analysis from past sessions |
| Past implementations | `rank queue redesign` | See how similar work was done |
| Decision rationale | `workflow gates approval` | Understand why choices were made |
| Test results | `test run report` | Check prior outcomes |

**Serena MCP contains**: Session transcripts, root-cause analyses, historical context.

### 10.3 Execution Order

```
1. Parse user request
2. Query Supermemory -> Get architecture/patterns/policies
3. [If needed] Query Serena MCP -> Get historical context
4. Plan and implement
5. Verify
6. Update Supermemory (only after verification + approval)
```

### 10.4 Golden Rule

**"Use Supermemory for implementation. Use Serena MCP for context."**

Supermemory gives you the "what" and "how". Serena gives you the "why".

---

## 11. Graphify Knowledge Graph

This project has a graphify knowledge graph at `graphify-out/`.

### 11.1 Using the Graph

- **Report**: `graphify-out/GRAPH_REPORT.md` — God nodes, communities, surprising connections
- **Interactive HTML**: `graphify-out/graph.html` — Open in browser to explore 415 nodes, 623 edges, 39 communities
- **JSON**: `graphify-out/graph.json` — Queriable graph data

### 11.2 Rules

- Before answering architecture or codebase questions, read `graphify-out/GRAPH_REPORT.md` for god nodes and community structure.
- If `graphify-out/wiki/index.md` exists, navigate it instead of reading raw files.
- After modifying code files in this session, run `python3 -c "from graphify.watch import _rebuild_code; from pathlib import Path; _rebuild_code(Path('.'))"` to keep the graph current.

### 11.3 Maintenance

- Keep graph fresh with: `graphify hook install` (post-commit + post-checkout rebuild)
- Prefer querying graph outputs first (`GRAPH_REPORT.md`, `graphify query`) before broad grep/glob sweeps

---

## 12. Critical Behavioral Rules

### 12.1 Pipeline Integrity

- `data/pipeline.md` is the **canonical URL inbox**. Never edit it manually without understanding the Pendientes/Procesadas structure.
- `data/applications.md` is the **canonical tracker**. All mode outputs that create tracker entries must append to this file in valid TSV format.
- `reports/` and `output/` are **write-only for agents**. Humans read them; agents write them.

### 12.2 Mode Execution Rules

- **Single evaluation** (`/career-ops <JD text>`): Read grounding files first, output to files only, no chat posting.
- **Auto-pipeline** (`/career-ops --auto`): Orchestrates multiple modes; respects `workflow_gates` thresholds.
- **Batch** (`/career-ops --batch`): Processes multiple URLs; uses `batch/batch-prompt.md` as worker prompt.

### 12.3 No Git Operations During Execution

Do NOT use git commands for verification. No git operations of any kind during execution. If git becomes necessary, STOP and ask the user.

**When asked to revert changes:** Trace back your steps and revert edits based on previous steps/responses executed. Do NOT use `git checkout` or similar git commands.

---

## 13. Forbidden Operations

- No command-line in-place editors (`sed -i`, `perl -pi`, `ed`)
- No "auto-fix" scripts that reorder or rewrite large file sections
- No mass search-and-replace across repo without a manifest + manual snippet patches
- Never delete `data/pipeline.md`, `data/applications.md`, or `reports/` contents
- Never edit `modes/_shared.md` without explicit user approval (it is the system contract)

---

## 14. Secret Handling Policy

Credentials and API keys must use environment variables or ignored config files. Integration wiring (key names, env var names) is preserved; raw values are not in tracked files. If you find exposed credentials, remove them immediately and flag for rotation if still live.

---

## 15. Output Structure

```
career-ops/
├── data/
│   ├── pipeline.md              # URL inbox (Pendientes/Procesadas)
│   ├── applications.md          # Application tracker (TSV)
│   ├── external_jobs.json       # Discovery results ledger
│   └── queue-ranking.json       # Ranking metadata sidecar
├── reports/
│   ├── 001-datadog-...md        # Numbered evaluation reports
│   └── deep/                    # Deep research reports
├── output/
│   ├── cv-*-*.pdf               # Generated ATS PDFs
│   └── *.html                   # Draft HTML outputs
├── dashboard/
│   └── main.go                  # Go TUI entry point
└── graphify-out/
    ├── graph.html               # Interactive knowledge graph
    ├── graph.json               # Queriable graph data
    └── GRAPH_REPORT.md          # Graph audit report
```

---

## 16. Environment Variables

```bash
# Playwright / Browser
PLAYWRIGHT_BROWSERS_PATH=0

# Career-Ops Paths (auto-detected if not set)
CAREER_OPS_ROOT=./career-ops

# Dashboard
DASHBOARD_CONFIG=./career-ops/config/profile.yml

# Node.js scripts
NODE_ENV=production
```

---

## 17. Troubleshooting

### Dashboard Shows "---" for Missing Data

1. Verify data files exist:
   ```bash
   ls career-ops/data/pipeline.md
   ls career-ops/data/applications.md
   ls career-ops/data/external_jobs.json
   ```

2. Check file structure is valid markdown/TSV/JSON

3. Re-run discovery pipeline if `external_jobs.json` is stale:
   ```bash
   python pipeline/run_pipeline.py
   ```

### Playwright PDF Generation Fails

1. Ensure Playwright browsers are installed:
   ```bash
   npx playwright install chromium
   ```

2. Check `templates/cv-template.html` exists and is valid HTML

3. Verify output directory is writable:
   ```bash
   ls -la career-ops/output/
   ```

### Mode Evaluation Produces No Output

1. Check that grounding files were read (`cv.md`, `profile.yml`, `_profile.md`)
2. Verify `modes/oferta.md` is readable and not corrupted
3. Check `reports/` directory is writable
4. Confirm evaluation score met output threshold (PDF only generated for B+ scores)

---

## 18. References and Knowledge Base

- **High-level guidance**: `career-ops/CLAUDE.md`, `career-ops/AGENTS.md` (this file)
- **Concise guide**: `career-ops/CAREER_OPS_CONCISE_GUIDE.md`
- **Workflow playbook**: `career-ops/CAREER_OPS_WORKFLOW_PLAYBOOK.md`
- **Data contract**: `career-ops/DATA_CONTRACT.md`
- **Architecture**: `career-ops/docs/ARCHITECTURE.md`
- **Setup**: `career-ops/docs/SETUP.md`
- **Scripts reference**: `career-ops/docs/SCRIPTS.md`
- **Customization**: `career-ops/docs/CUSTOMIZATION.md`
- **Graphify report**: `graphify-out/GRAPH_REPORT.md`

When in doubt, treat `career-ops/CLAUDE.md`, this `AGENTS.md`, and `career-ops/DATA_CONTRACT.md` as the primary documentation sources and reconcile any older documents against the current code paths before relying on them.

---

## 19. MCP Server Integrations

### Zen MCP - Multi-Model Reasoning

When complex reasoning is needed:

- **chat**: General collaborative thinking
- **thinkdeep**: Multi-stage investigation
- **planner**: Step-by-step planning
- **consensus**: Multi-model consensus
- **codereview**: Expert code review
- **debug**: Root cause analysis
- **analyze**: Architectural assessment
- **refactor**: Refactoring analysis
- **tracer**: Execution flow tracing
- **docgen**: Documentation generation

### Context7 MCP - Library Documentation

1. `resolve-library-id` - Find Context7 library ID
2. `get-library-docs` - Retrieve focused documentation

### Playwright MCP - Browser Automation

- `navigate_page`, `click`, `fill`, `take_screenshot`, `evaluate_script`
- Used for PDF generation verification and portal scanning debugging

---

*Generated for Career-Ops 2.0. Last updated: 2026-04-25*
