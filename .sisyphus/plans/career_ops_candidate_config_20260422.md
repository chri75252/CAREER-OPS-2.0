# Career-Ops candidate profile + config pass

## Goal
- Build an evidence-backed candidate profile for Christian Haddad using the job-seeking chat archive, the older CV/cover-letter docx, current Career-Ops files, and current market-role research.
- Update Career-Ops so discovery and evaluation align with realistic high-pay remote roles, including AI-adjacent roles outside pure AI-native companies.

## Source-of-truth priority
1. `chats on job seeking.txt`
2. `cv+cover old -christian full.docx`
3. Current user-layer Career-Ops files (`career-ops/config/profile.yml`, `career-ops/modes/_profile.md`, `career-ops/cv.md`, `career-ops/portals.yml`, `config/pipeline.yaml`)
4. Current external market-role research gathered in this pass
5. Older memory/context only when it does not conflict with the sources above

## Target files
- `career-ops/config/profile.yml`
- `career-ops/modes/_profile.md`
- `career-ops/portals.yml`
- `config/pipeline.yaml`
- `career-ops/article-digest.md` (new, if needed for proof-point depth)
- `career-ops/docs/CHRISTIAN_CANDIDATE_PROFILE_20260422.md` (new evidence-backed profile/report)

## Minimum required fixes
1. Replace narrow AI-only target-role framing with a ranked set of realistic role families.
2. Add compensation, geography, and remote-search assumptions that match the evidence.
3. Expand title filters and search keywords toward implementation, solutions, operations, workflow, and AI-adjacent roles.
4. Expand tracked company targeting beyond the current small AI-native subset.
5. Add proof-point context so evaluation modes can frame the candidate credibly.

## Bounded change rule
- Only add role families, title filters, keywords, and companies that clearly align with the evidence-backed positioning.
- Avoid generic broadening toward pure software engineering, research, or unrelated operations roles.

## Explicit non-goals
- No system-layer changes to shared modes or scripts.
- No attempt to rewrite the whole CV for final applications.
- No fake claims or inflated AI-software-engineering positioning.
- No broad refactor of dashboard or pipeline code.

## Edit order
1. Create evidence-backed report file.
2. Update `career-ops/config/profile.yml`.
3. Update `career-ops/modes/_profile.md`.
4. Update `career-ops/portals.yml`.
5. Update `config/pipeline.yaml`.
6. Add `career-ops/article-digest.md` only if the proof points already in `career-ops/config/profile.yml` are too thin for downstream modes.

## Validation order
1. Re-read changed files for correctness and consistency.
2. Parse-check YAML files: `career-ops/config/profile.yml`, `career-ops/portals.yml`, `config/pipeline.yaml`.
3. Verify discovery config still uses valid existing schema patterns.
4. Do a before/after sanity check on primary keywords/title filters to confirm bounded scope.
5. Summarize assumptions and any remaining ambiguity for the user.

## Rollback scope
- Only files listed in Target files.
- Restore from `backup/career_ops_candidate_config_20260422/REVERT_TRACKING.md` and git/manual copies if needed.
