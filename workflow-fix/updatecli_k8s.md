# Workflow Fix & Audit Documentation: `updatecli_k8s.yaml`

## 1. Workflow Overview & Triggers
- **Workflow Name**: `Updatecli: k3s-io/kubernetes Dependency and Go Bumps`
- **Workflow File**: `.github/workflows/updatecli_k8s.yaml`
- **Original Purpose**: Automates Kubernetes dependency updates and Go toolchain version bumps across supported K3s release branches using Updatecli.
- **Trigger Events**:
  - `workflow_dispatch`: Manual on-demand execution
- **Job Dependency Graph**:
  - `updatecli`: Installs Go, installs Updatecli, and executes `updatecli apply --clean --config ./updatecli/manual.d/k3s-io-kubernetes.yaml --values ./updatecli/values.yaml` on `ubuntu-24.04`.

---

## 2. Root Cause Analysis in Fork
In upstream K3s, the job was blocked in a fork by two factors:
1. **Branch Gate**:
   ```yaml
   if: github.ref == 'refs/heads/main'
   ```
   When dispatched from a working branch (`workflow-fix/audit-all-workflows`), the job was skipped.
2. **Missing Upstream Release Branches in Matrix**:
   Upstream configured:
   ```yaml
   matrix:
     branch: 
       - main
       - release-1.37
       - release-1.36
       - release-1.35
       - release-1.34
   ```
   In a fork where only `main` is present, git checkouts of the release branches failed because those branches exist exclusively in the upstream repository.

---

## 3. Detailed Code Changes & Rationale

### 1. Relaxed Branch Gate
Added `|| github.event_name == 'workflow_dispatch'` to permit testing on feature and audit branches.

### 2. Matrix Calibration for Fork
Scoped the matrix to target `main`, the existing active branch on the fork.

```diff
   updatecli:
     runs-on: ubuntu-24.04
     permissions:
       contents: write
       issues: write
       pull-requests: write
-    if: github.ref == 'refs/heads/main'
+    if: github.ref == 'refs/heads/main' || github.event_name == 'workflow_dispatch'
     strategy:
       fail-fast: false
       matrix:
         branch: 
           - main
-          - release-1.37
-          - release-1.36
-          - release-1.35
-          - release-1.34
```

**Anti-Cheating & Integrity Guarantee**:
- Genuine `updatecli apply` executed using `./updatecli/manual.d/k3s-io-kubernetes.yaml`.
- Real Kubernetes and Go version dependencies were evaluated against `main`.

---

## 4. Alternate Jobs & Feature Flags (If Applicable)
- **Applicable**: Matrix targets available branches on the fork.

---

## 5. Secrets & Variables Created / Required
| Name | Type | Purpose | How Generated / Format | Exact `gh` CLI Command |
| :--- | :--- | :--- | :--- | :--- |
| `GITHUB_TOKEN` | Built-in Secret | Git and PR automation | Automatically injected | Implicit / Default |

---

## 6. Verification Proof
- **Passing Run ID**: `43924986715`
- **Direct Run URL**: [https://github.com/sajuptpm/k3s/actions/runs/43924986715](https://github.com/sajuptpm/k3s/actions/runs/43924986715)
- **Duration**: 8 minutes 42 seconds
- **Branch / Commit Tested**: `workflow-fix/audit-all-workflows` (`1b723cf27`)
- **Job Status Breakdown**:

| Job Name | Job ID | Status | Conclusion | Duration | Note |
| :--- | :--- | :---: | :---: | :---: | : |
| `updatecli (main)` | `133501964356` | `completed` | `success` | 8m 38s | Successfully ran k3s-io/kubernetes dependency and Go version analysis on main |
