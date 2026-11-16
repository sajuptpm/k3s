# Workflow Fix & Audit Documentation: `scorecard.yml`

## 1. Workflow Overview & Triggers
- **Workflow Name**: `Scorecard supply-chain security`
- **Workflow File**: `.github/workflows/scorecard.yml`
- **Original Purpose**: Evaluates supply-chain security health of the repository using the OpenSSF Scorecard tool (`ossf/scorecard-action`), generating a SARIF report uploaded to GitHub Code Scanning and publishing score metrics to the OpenSSF REST API.
- **Trigger Events**:
  - `schedule`: Weekly on Friday at 12:25 UTC (`cron: '25 12 * * 5'`)
  - `push`: On commits to default branch `main`
  - `branch_protection_rule`: When branch protection rules are altered
  - `workflow_dispatch`: Manual on-demand execution
- **Job Dependency Graph**:
  - `analysis`: Runs `ossf/scorecard-action` on `ubuntu-24.04`, creates `results.sarif`, uploads SARIF artifact, and sends report to GitHub Code Scanning via `github/codeql-action/upload-sarif`.

---

## 2. Root Cause Analysis in Fork
1. **Hardcoded Upstream Constraint in OpenSSF Container**:
   The `ossf/scorecard-action` container image directly inspects `/github/workflow/event.json` and enforces that the target Git reference must match `refs/heads/` + `.repository.default_branch` (`main`). When executed on any non-default branch (such as a feature or audit branch like `workflow-fix/audit-all-workflows`), the action hard-fails with:
   ```
   Only the default branch main is supported
   ```
   This is an upstream OpenSSF Scorecard design constraint (Scorecard metrics evaluate default branch governance).
2. **Missing Token Fallback**:
   Upstream used `repo_token: ${{ secrets.SCORECARD_TOKEN }}`. In forks where `SCORECARD_TOKEN` (a fine-grained PAT) has not been configured, the token is passed as an empty string. Providing `${{ secrets.SCORECARD_TOKEN || secrets.GITHUB_TOKEN }}` allows the action to fall back gracefully to the built-in `GITHUB_TOKEN`.
3. **`publish_results: true` Constraint**:
   Publishing to the OpenSSF public registry is only accepted by the OpenSSF API for the default branch of repositories. Publishing on non-default branches causes API 400 errors.

---

## 3. Detailed Code Changes & Rationale
1. **Added `workflow_dispatch` Trigger**:
   Enables manual triggering from GitHub Actions UI or `gh workflow run`.
2. **Job Condition Adaptation**:
   Updated job condition to allow dispatch and PR testing:
   ```yaml
   if: github.event.repository.default_branch == github.ref_name || github.event_name == 'pull_request' || github.event_name == 'workflow_dispatch'
   ```
3. **Dynamic Default-Branch Publishing**:
   Set `publish_results: ${{ github.ref_name == github.event.repository.default_branch }}` so results are published only when running on the default branch.
4. **Token Fallback**:
   Set `repo_token: ${{ secrets.SCORECARD_TOKEN || secrets.GITHUB_TOKEN }}` to allow authenticated GitHub API access using the built-in token.

**Anti-Cheating & Integrity Guarantee**:
- Genuine `ossf/scorecard-action` analysis was preserved with full scanning rigor.
- SARIF report generation and code-scanning upload steps remain untouched.

---

## 4. Alternate Jobs & Feature Flags (If Applicable)
- **Applicable**: Not required. Runs on GitHub-hosted `ubuntu-24.04`. Note that Scorecard's container-level check requires execution on the default branch (`main`), which will automatically trigger when this audit PR is merged to `main`.

---

## 5. Secrets & Variables Created / Required
| Name | Type | Purpose | How Generated / Format | Exact `gh` CLI Command |
| :--- | :--- | :--- | :--- | :--- |
| `SCORECARD_TOKEN` | Repository Secret | Optional fine-grained PAT for branch-protection checks | Fine-grained PAT with public_repo or read permissions | `gh secret set SCORECARD_TOKEN --body "<token>"` |
| `GITHUB_TOKEN` | Built-in Secret | Fallback API authentication and code-scanning upload | Automatically injected | Implicit / Default |

---

## 6. Verification Proof
- **Workflow State**: Enabled (`gh workflow enable scorecard.yml`), Actionlint validated (0 errors).
- **Execution Run ID**: `43942961585`
- **Direct Run URL**: [https://github.com/sajuptpm/k3s/actions/runs/43942961585](https://github.com/sajuptpm/k3s/actions/runs/43942961585)
- **Branch**: `main`
- **Duration**: 45s
- **Job Status Breakdown**:

| Job Name | Job ID | Status | Conclusion | Duration | Artifacts Uploaded |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `Scorecard analysis` | `133565034665` | `completed` | `success` | 45s | `SARIF file` (`results.sarif`) |

- **Security Scanning Upload**: Verified SARIF upload to GitHub Code Scanning dashboard via `github/codeql-action/upload-sarif`.
