# Workflow Fix & Audit Documentation: `stale.yml`

## 1. Workflow Overview & Triggers
- **Workflow Name**: `Stalebot`
- **Workflow File**: `.github/workflows/stale.yml`
- **Original Purpose**: Automatically identifies, marks, and closes stale community issues that have had no activity for 45 days, while exempting pull requests and milestone/assignee-tagged issues.
- **Trigger Events**:
  - `schedule`: Daily at 20:00 UTC (`0 20 * * *`)
  - `workflow_dispatch`: Manual on-demand execution
- **Job Dependency Graph**:
  - `stalebot` (Runs independently on `ubuntu-24.04`)

---

## 2. Root Cause Analysis in Fork
When attempting to trigger `stale.yml` in this fork (`sajuptpm/k3s`), GitHub rejected the dispatch command:
```
HTTP 422: Cannot trigger a 'workflow_dispatch' on a disabled workflow (https://api.github.com/repos/sajuptpm/k3s/actions/workflows/419931077/dispatches)
```
**Architectural Reason**:
By default, GitHub automatically silences all scheduled workflows on newly created forks to prevent unexpected automated actions from running against upstream forks (`state: disabled_fork`).

---

## 3. Detailed Code Changes & Rationale
No code modifications to `.github/workflows/stale.yml` were necessary. The workflow already included `workflow_dispatch:` and used standard GitHub-hosted runner `ubuntu-24.04` with official `actions/stale@v11.0.0`.

To enable genuine execution in the fork, the workflow was enabled via GitHub CLI:
```bash
gh workflow enable 419931077
```

---

## 4. Alternate Jobs & Feature Flags (If Applicable)
- **Applicable**: No alternate jobs needed. The workflow executes natively using standard GitHub APIs.

---

## 5. Secrets & Variables Created / Required
| Name | Type | Purpose | How Generated / Format | Exact `gh` CLI Command |
| :--- | :--- | :--- | :--- | :--- |
| `GITHUB_TOKEN` | Built-in Secret | Issue tagging and commenting | Injected automatically by GitHub Actions | Implicit / Default |

---

## 6. Verification Proof
- **Passing Run ID**: `43898486480`
- **Direct Run URL**: [https://github.com/sajuptpm/k3s/actions/runs/43898486480](https://github.com/sajuptpm/k3s/actions/runs/43898486480)
- **Duration**: 17 seconds
- **Branch / Commit Tested**: `workflow-fix/audit-all-workflows` (`fffbc4cbf`)
- **Job Status Breakdown**:

| Job Name | Job ID | Status | Conclusion | Note |
| :--- | :--- | :---: | :---: | :--- |
| `stalebot` | `133417743513` | `completed` | `success` | Genuinely evaluated issues against stale rules |
