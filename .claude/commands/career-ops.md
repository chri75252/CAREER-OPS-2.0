---
description: Career-Ops router from repo parent root
argument-hint: [JD text | URL | subcommand]
---

You are running Career-Ops from the repo parent root.

The actual Career-Ops router lives in the nested subproject skill below. Read it and execute it as if Claude had been launched from the `career-ops/` directory.

Arguments for this invocation:

`$ARGUMENTS`

Nested router source:

@career-ops/.claude/skills/career-ops/SKILL.md

Additional nested project instructions:

@career-ops/CLAUDE.md
@career-ops/AGENTS.md

Execution requirements:

1. Apply the nested router instructions to `$ARGUMENTS`.
2. Load any referenced `modes/*` files from the nested `career-ops/` project.
3. Write outputs to the nested `career-ops/` paths exactly as the mode files require.
4. Do not just explain the workflow; execute it.
5. The working project for all file reads/writes is `career-ops/` under the current repo root.
