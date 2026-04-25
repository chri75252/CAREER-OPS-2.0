Windows-oriented commands commonly used in this project:
- Parent root discovery run: `python pipeline/run_pipeline.py "AI engineer" "applied AI engineer" "solutions engineer"`
- Career-Ops scan/import from nested project: `npm run scan` then `npm run import:external`
- Career-Ops health check: `node verify-pipeline.mjs`
- Career-Ops broad test suite: `node test-all.mjs` or `node test-all.mjs --quick`
- Dashboard tests: `go test ./...` from `career-ops/dashboard`
- Dashboard build: `go build -o career-dashboard.exe .` from `career-ops/dashboard`
- Setup validation: `npm run doctor`
- Tracker maintenance: `npm run merge`, `npm run normalize`, `npm run dedup`
- Helpful shell basics on Windows here: `dir`, `type`, `python`, `node`, `npm.cmd`, `go`.