# CICDSecurity — DevSecOps Pipeline for Automated Vulnerability Detection

A GitHub Actions pipeline that enforces six layers of automated security scanning on every push and pull request, blocking merges when critical issues are found. Built as a hands-on implementation of a shift-left security procedure (`docs/failure-handling-procedure.md`).

## What this pipeline does

Every code change passes through security gates **before** it can reach `master`:

```
Developer: git push / Pull Request
                 │
                 ▼
        ┌─────────────────┐
        │ GitHub Actions  │
        └────────┬────────┘
                 │
   ┌─────────────┼───────────────┐   Stage 1 — source code (parallel)
   ▼             ▼               ▼
GitLeaks      Semgrep       OSV-Scanner
(secrets)     (SAST)        (dependencies)
   └─────────────┼───────────────┘
                 ▼  all pass?
          Docker image build
                 │
        ┌────────┴────────┐          Stage 2 — build artifact
        ▼                 ▼
      Trivy         Syft → SBOM
   (image scan)          │
                         ▼
                       Grype
                 (SBOM, reporting)
                 │
                 ▼
   All required checks pass → PR mergeable
   Any blocking check fails → merge BLOCKED
```

A failing check does not just mark the build red — a GitHub branch ruleset on `master` makes the status checks **required**, so the "Merge" button is physically disabled until every blocking stage is green.

## Tools and what each one catches

| Tool | Catches | Blocks merge? |
|---|---|---|
| [GitLeaks](https://github.com/gitleaks/gitleaks) | Hardcoded secrets, API keys, tokens — including in commit history | Yes |
| [Semgrep](https://semgrep.dev/) (`p/security-audit`) | Insecure code patterns (e.g. command injection, SQL injection) | Yes |
| [OSV-Scanner](https://github.com/google/osv-scanner) | Known CVEs in direct Python dependencies | Yes |
| [Trivy](https://trivy.dev/) | OS and package vulnerabilities inside the built Docker image | Yes (HIGH/CRITICAL with a fix available) |
| [Syft](https://github.com/anchore/syft) | Generates a CycloneDX SBOM (software bill of materials) | — (artifact only) |
| [Grype](https://github.com/anchore/grype) | Vulnerability scan against the built image | No — reporting layer (see EXC-003) |

## Repository structure

```
CICDSecurity/
├── app/
│   ├── app.py                   # demo Flask application
│   └── requirements.txt
├── Dockerfile
├── .github/workflows/
│   └── security-pipeline.yml    # the pipeline itself
├── docs/
│   ├── failure-handling-procedure.md
│   └── exceptions.md            # documented false positives / risk acceptances
└── README.md
```

## Running it locally

```bash
docker build -t cicd-demo .
docker run --rm -p 5001:5000 cicd-demo
curl http://localhost:5001/health
```

## Contribution workflow

`master` is protected. Direct pushes are rejected. All changes go through a Pull Request:

```bash
git checkout -b feature/your-change
# edit files
git add .
git commit -m "Describe the change"
git push origin feature/your-change
# open a PR on GitHub — merge is blocked until all required checks pass
```

## Exceptions and incidents

Not every finding gets silently fixed or silently ignored — each one is triaged and, where suppressed, documented with a reason and an owner. See [`docs/exceptions.md`](docs/exceptions.md) for the full log, including:

- **EXC-001** — Flask `host="0.0.0.0"` flagged by Semgrep: a documented false positive, since the app runs inside a Docker container where this binding is required and network isolation is handled by Docker itself.
- **EXC-002** — Trivy `ignore-unfixed`: dozens of HIGH-severity findings in the base OS image have no upstream fix yet; blocking on them would make the pipeline permanently red for no actionable reason.
- **EXC-003** — Grype set to non-blocking: Grype's `--only-fixed` filter proved unreliable (a [known upstream limitation](https://github.com/anchore/grype/issues/1431)), so it was kept as a secondary, SBOM-based reporting layer rather than a second blocking gate duplicating Trivy.

One real supply-chain incident was also encountered and documented during development: the `aquasecurity/trivy-action` repository suffered a tag-hijacking attack in March 2026 (GHSA-69fq-xp46-6x23), which broke the pinned action version used in this pipeline. The fix and the incident write-up are part of the commit history and `docs/exceptions.md`.

## What this project demonstrates

- Building a multi-stage CI/CD pipeline with parallel and sequential job dependencies
- Shift-left security: catching secrets, insecure code, and vulnerable dependencies before merge
- Container and supply-chain security: SBOM generation and vulnerability scanning
- Break-and-fix validation: every control was verified by deliberately triggering it, not assumed to work
- Risk triage and documented exception handling, including recognizing and responding to a real third-party supply-chain compromise
- Branch protection and PR-based development workflow