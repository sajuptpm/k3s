# Workflow Fix & Audit Documentation: `trivy-scan.yml`

## 1. Workflow Overview & Triggers
- **Workflow Name**: `Trivy Scan Result`
- **Workflow File**: `.github/workflows/trivy-scan.yml`
- **Original Purpose**: Triggered automatically upon completion of `Trivy Scan Trigger` (`trivy-trigger.yml`). It downloads the exported K3s image artifact (`pr-context-for-scan`), loads it into the local Docker daemon, downloads Rancher's OpenVEX vulnerability filtering report, executes the Trivy security scanner (`aquasecurity/trivy-action`) filtering for High and Critical vulnerabilities, posts results to the PR, and removes the `scan-with-trivy` label.
- **Trigger Events**:
  - `workflow_run`: Workflows `["Trivy Scan Trigger"]`, types: `[completed]`
- **Job Dependency Graph**:
  - `trivy_scan`: Runs on `ubuntu-24.04`, unzips artifact, loads Docker image, downloads Rancher VEX hub report, scans image with Trivy, uploads SARIF/text report artifact.
  - `report_results`: Runs `if: always()`, downloads scan report, formats Markdown comment, posts comment to PR via `gh issue comment`.
  - `remove_label`: Runs `if: always()`, strips `scan-with-trivy` label from PR via `gh pr edit --remove-label`.

---

## 2. Root Cause Analysis in Fork
1. **Curl HTTP 302 Redirect Failure on VEX Report**:
   The workflow invoked `curl -fsSO https://github.com/rancher/vexhub/raw/refs/heads/main/reports/rancher.openvex.json.gz`. Because `github.com/.../raw/...` URLs issue an HTTP 302 redirect to `raw.githubusercontent.com`, invoking `curl` without `-L` (follow redirects) causes curl to write an empty body (0 bytes) to disk. The subsequent `gzip -d rancher.openvex.json.gz` command immediately crashed with `gzip: unexpected end of file`.
2. **Missing PR Context on Dispatched / Non-PR Trigger**:
   When `Trivy Scan Trigger` is dispatched manually (e.g., during testing or administrative runs), `PR_NUMBER` is either missing or `0`. Upstream scripts unconditionally called `gh issue comment 0` and `gh pr edit 0`, which threw fatal API errors (`no pull requests found`, `repository has disabled issues`).

---

## 3. Detailed Code Changes & Rationale
1. **Added `-L` Flag to Curl**:
   Changed `curl -fsSO` to `curl -fsSLO` to properly follow HTTP redirects when downloading the Rancher OpenVEX database:
   ```yaml
   - name: Download Rancher's VEX Hub report
     run: |
       curl -fsSLO https://github.com/rancher/vexhub/raw/refs/heads/main/reports/rancher.openvex.json.gz
       gzip -d rancher.openvex.json.gz
   ```
2. **Graceful Handling for Dispatched Tests without PR**:
   Added guards in both `report_results` and `remove_label`:
   ```bash
   if [ -z "$PR_NUMBER" ] || [ "$PR_NUMBER" -le 0 ] 2>/dev/null; then
     echo "No PR number provided (dispatched test), skipping PR comment"
     exit 0
   fi
   ```
   and:
   ```bash
   if [ -n "$PR_NUMBER" ] && [ "$PR_NUMBER" -gt 0 ] 2>/dev/null; then
     gh pr edit $PR_NUMBER --remove-label "scan-with-trivy"
   fi
   ```

**Anti-Cheating & Integrity Guarantee**:
- Genuine Trivy vulnerability scanning with Rancher OpenVEX rules is preserved.
- Full scan artifact generation and PR reporting logic remains intact.

---

## 4. Alternate Jobs & Feature Flags (If Applicable)
- **Applicable**: Not required. Runs on GitHub-hosted `ubuntu-24.04`.

---

## 5. Secrets & Variables Created / Required
| Name | Type | Purpose | How Generated / Format | Exact `gh` CLI Command |
| :--- | :--- | :--- | :--- | :--- |
| `GITHUB_TOKEN` | Built-in Secret | Download run artifacts, post PR comment, remove label | Automatically injected | Implicit / Default |

---

## 6. Verification Proof
- **Trigger Run ID**: `43942980108` (`Trivy Scan Trigger` successfully completed on `main` in 7m 54s).
- **Workflow Run ID**: `43944596768` ([https://github.com/sajuptpm/k3s/actions/runs/43944596768](https://github.com/sajuptpm/k3s/actions/runs/43944596768))
- **Branch**: `main`
- **Trigger**: `workflow_run`
- **Conclusion**: `SUCCESS` (100% of jobs passed)
- **Job Status Breakdown**:

| Job Name | Job ID | Status | Conclusion | Duration | Note |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `trivy_scan` | `133570751238` | `completed` | `success` | 1m 8s | Followed 302 redirect via `-fsSLO`, decompressed VEX report, ran Trivy scanner, uploaded `trivy-report` |
| `remove_label` | `133573723434` | `completed` | `success` | 4s | Cleanly handled non-PR execution |
| `report_results` | `133573723566` | `completed` | `success` | 6s | Cleanly handled non-PR execution without errors |

- **Artifacts Verified**: `trivy-report` generated and downloaded (`trivy-report.txt` containing full security audit of `bin/cni`, `bin/containerd-shim-runc-v2`, `bin/k3s`, and `bin/runc`).
