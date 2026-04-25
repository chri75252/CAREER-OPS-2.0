# Revert Tracking - Career-Ops candidate config pass - 2026-04-22

## Scope
- Build an evidence-backed candidate profile report and update Career-Ops personalization/discovery config for Christian Haddad.

## Planned files

| File | Change scope | Restore source | Validation |
|---|---|---|---|
| `career-ops/docs/CHRISTIAN_CANDIDATE_PROFILE_20260422.md` | New candidate profile/report | Delete file if reverting | Read file content |
| `career-ops/config/profile.yml` | Refresh target roles, narrative, compensation, location flexibility | `backup/career_ops_candidate_config_20260422/profile.yml.bak` | Read file content + YAML parse |
| `career-ops/modes/_profile.md` | Reframe role archetypes and adaptive positioning | `backup/career_ops_candidate_config_20260422/_profile.md.bak` | Read file content |
| `career-ops/portals.yml` | Expand title filters and tracked companies | `backup/career_ops_candidate_config_20260422/portals.yml.bak` | Read file content + YAML parse |
| `config/pipeline.yaml` | Expand role keywords and remote-targeted discovery | `backup/career_ops_candidate_config_20260422/pipeline.yaml.bak` | Read file content + YAML parse |
| `career-ops/article-digest.md` | New proof-point digest (optional) | Delete file if reverting | Read file content |

## Notes
- This pass must preserve user-layer customization rules from `career-ops/CLAUDE.md`.
- No system-layer files are in scope.
