# Security Exceptions Registry

This file documents every case where a security scanner's finding was suppressed, filtered, or treated as non-blocking rather than fixed outright. Each entry follows the exception-handling procedure in `failure-handling-procedure.md`: a documented reason, an owner, and a review condition.

---

## EXC-001: Flask `host="0.0.0.0"` (Semgrep)

- **Tool / Rule:** Semgrep — `python.flask.security.audit.app-run-param-config.avoid_app_run_with_bad_host`
- **File:** `app/app.py`
- **Finding:** Running a Flask app with `host="0.0.0.0"` can expose the server publicly.
- **Reason for suppression:** The application runs inside a Docker container. Binding to `0.0.0.0` is required for the container's exposed port (`EXPOSE 5000` + `docker run -p`) to reach the app at all — binding to `127.0.0.1` would make the app unreachable from outside the container. Network-level isolation is provided by Docker itself, not by the app's bind address.
- **Resolution:** Suppressed with an inline `# nosemgrep: <rule-id>` comment on the matched line.
- **Duration:** Permanent, as long as the app is deployed containerized.
- **Owner:** Ramziddin Farmonov
- **Date:** 2026-10-03

---

## EXC-002: Trivy `ignore-unfixed` (container OS vulnerabilities)

- **Tool:** Trivy (container image scan)
- **Finding:** 45 HIGH-severity vulnerabilities in the `python:3.12-slim` (Debian 13) base image, 44 of which had no `Fixed Version` listed.
- **Reason for suppression:** Debian had not yet published a patched package for these CVEs at scan time. Blocking the pipeline on vulnerabilities with no available fix would make the pipeline permanently red with no actionable remediation.
- **Resolution:** `ignore-unfixed: true` set on the Trivy step. The one vulnerability that did have a fix (`libpcre2-8-0`, CVE-2026-103111) was resolved by adding `apt-get update && apt-get upgrade -y` to the Dockerfile.
- **Duration:** Reviewed monthly — base image updates may resolve some of these upstream.
- **Owner:** Ramziddin Farmonov
- **Date:** 2026-10-03

---

## EXC-003: Grype set to non-blocking (reporting layer only)

- **Tool:** Grype (`anchore/scan-action`)
- **Finding:** Grype's `only-fixed: true` filter did not reliably exclude unfixed vulnerabilities, regardless of whether it scanned the SBOM or the image directly — a known upstream limitation ([anchore/grype#1431](https://github.com/anchore/grype/issues/1431)): the filter depends on a "fix state" field in the vulnerability database that is often incomplete.
- **Reason for suppression:** Trivy already reliably blocks on HIGH/CRITICAL vulnerabilities with an available fix (`ignore-unfixed: true`, see EXC-002). Making Grype block on the same image with an unreliable filter would either duplicate Trivy's gate or produce false blocks on unfixable issues, adding noise without added protection.
- **Resolution:** `fail-build: false` set on the Grype step. It still scans and reports findings (visible in the job log and the generated SBOM artifact); it just doesn't fail the pipeline.
- **Duration:** Revisit if/when `anchore/grype#1431` is resolved upstream, or if Trivy coverage is ever removed.
- **Owner:** Ramziddin Farmonov
- **Date:** 2026-10-03

---

## Related: Supply-chain incident (not an exception, but relevant context)

On 2026-03-19, the `aquasecurity/trivy-action` GitHub repository suffered a tag-hijacking attack (GHSA-69fq-xp46-6x23): 76 historical tags, including `0.28.0`, were overwritten with malicious code before Aqua Security remediated it by deleting all compromised tags. This broke the pinned version used in this pipeline (the tag no longer existed) rather than exposing the pipeline to the malicious code itself. The fix was to re-pin to `0.35.0`, a version released after remediation and confirmed clean.

**Lesson applied:** third-party GitHub Actions should be pinned to an exact version (ideally a commit SHA) rather than a floating tag like `latest` or `master`, and pinned versions should be periodically reviewed for upstream security advisories.