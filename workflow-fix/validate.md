# Workflow Fix & Audit Documentation: `validate.yaml`

## 1. Workflow Overview & Triggers
- **Workflow Name**: `Validate`
- **Workflow File**: `.github/workflows/validate.yaml`
- **Original Purpose**: Performs code validation, static analysis, formatting, and linting across both Linux and Windows environments using `golangci-lint` and `./scripts/validate`.
- **Trigger Events**:
  - `pull_request`: On changes to code files, scripts, and workflow configuration
  - `workflow_dispatch`: Manual on-demand execution
- **Job Dependency Graph**:
  - `validate`: Runs on `ubuntu-24.04`, cleans disk space, checks out code with computed fetch depth, sets Go version via `./scripts/version.sh`, sets up Go, runs `golangci-lint` for Linux, runs `golangci-lint` for Windows (`GOOS=windows`), and runs `./scripts/validate` for both targets.

---

## 2. Root Cause Analysis in Fork
1. **Missing `workflow_dispatch` Trigger on Default Branch**:
   Upstream lacked `workflow_dispatch`. GitHub Actions API rejects dispatching workflows that do not declare `workflow_dispatch` on the default branch (`main`).
2. **Pull Request Expression Evaluation Error on Manual Dispatch**:
   Upstream used `expr 1 + ${{ github.event.pull_request.commits }}` and `--new-from-merge-base ${{ github.event.pull_request.base.sha }}`. When triggered via events other than `pull_request` (or in testing context where PR context is null), expression evaluation produced invalid commands (`expr 1 + ` syntax error) and lint failures.

---

## 3. Detailed Code Changes & Rationale
1. **Added `workflow_dispatch` Trigger**:
   ```yaml
   on:
     pull_request:
       paths-ignore: ...
     workflow_dispatch: {}
   ```
2. **Conditional Checkout Depth**:
   ```bash
   if [ -n "${{ github.event.pull_request.commits }}" ]; then
     echo "GITHUB_CHECKOUT_FETCH_DEPTH=$( expr 1 + ${{ github.event.pull_request.commits }} )" >> "$GITHUB_ENV"
   else
     echo "GITHUB_CHECKOUT_FETCH_DEPTH=0" >> "$GITHUB_ENV"
   fi
   ```
   Ensures shallow fetch when PR commit count is available, or full history (`fetch-depth: 0`) when dispatched or PR count is null.
3. **Guarded Merge Base Lint Arguments**:
   ```yaml
   args: "${{ github.event_name == 'pull_request' && format('--new-from-merge-base {0}', github.event.pull_request.base.sha) || '' }}"
   ```
   and for Windows:
   ```yaml
   args: "${{ github.event_name == 'pull_request' && format('--new-from-merge-base {0} ./pkg/... ./cmd/...', github.event.pull_request.base.sha) || './pkg/... ./cmd/...' }}"
   ```

**Anti-Cheating & Integrity Guarantee**:
- Genuine `golangci-lint` execution on both Linux and Windows.
- Full `./scripts/validate` script execution is preserved.

---

## 4. Alternate Jobs & Feature Flags (If Applicable)
- **Applicable**: Not required. Runs on GitHub-hosted `ubuntu-24.04`.

---

## 5. Secrets & Variables Created / Required
| Name | Type | Purpose | How Generated / Format | Exact `gh` CLI Command |
| :--- | :--- | :--- | :--- | :--- |
| `GITHUB_TOKEN` | Built-in Secret | Git checkout and GitHub API calls | Automatically injected | Implicit / Default |

---

## 6. Verification Proof
- **Pull Request**: [#1](https://github.com/sajuptpm/k3s/pull/1)
- **Workflow Run ID**: `43930522865`
- **Direct Run URL**: [https://github.com/sajuptpm/k3s/actions/runs/43930522865](https://github.com/sajuptpm/k3s/actions/runs/43930522865)
- **Branch / Commit Tested**: `workflow-fix/audit-all-workflows` (`e01a4cd0d`)
- **Status**: Completed / Verified on PR #1
