---
description: Career-Ops scan from repo parent root
---

Repo parent-root shim for the nested Career-Ops OpenCode command.

Authoritative execution path:

```bash
cd career-ops
npm run discover
```

This is intentionally routed to the unified discovery workflow, not the older mode-only scan prompt, so Results (`data/external_jobs.json`), Queue (`data/pipeline.md`), scan history, and ranking metadata (`data/queue-ranking.json`) stay synchronized.

For dry-run validation, use:

```bash
cd career-ops
npm run discover:dry-run
```
