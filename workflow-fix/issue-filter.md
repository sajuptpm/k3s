# Workflow Fix & Audit Documentation: `issue-filter.yaml`

## 1. Workflow Overview & Triggers
- **Workflow Name**: `Issue Filter`
- **Workflow File**: `.github/workflows/issue-filter.yaml`
- **Original Purpose**: Automatically filters incoming community issues, checks whether the author is an authorized maintainer, and auto-closes oversized untemplated issues to maintain issue tracker hygiene.
- **Trigger Events**:
  - `issues`: On `opened`
  - `workflow_dispatch`: Manual execution (Added for fork testing)
- **Job Dependency Graph**:
  - `close-oversized-issues`: Single job running on `ubuntu-24.04`.

---

## 2. Root Cause Analysis in Fork
In upstream K3s, `issue-filter.yaml` triggered exclusively on `issues: [opened]`. Because there are no open issues initially in a fork, manual testing was blocked until a `workflow_dispatch` trigger was added.

---

## 3. Detailed Code Changes & Rationale

### Added `workflow_dispatch` Trigger
```diff
 name: Issue Filter
 
 on:
   issues:
     types: [opened]
+  workflow_dispatch: {}
 
 permissions:
   contents: read
```

**Dynamic Collaborator Check Verification**:
The JavaScript step uses `github.rest.repos.getCollaboratorPermissionLevel({ owner: context.repo.owner, repo: context.repo.repo, ... })`, which automatically uses the fork owner's repository instead of hardcoding `k3s-io`.

---

## 4. Alternate Jobs & Feature Flags (If Applicable)
- **Applicable**: Not required.

---

## 5. Secrets & Variables Created / Required
| Name | Type | Purpose | How Generated / Format | Exact `gh` CLI Command |
| :--- | :--- | :--- | :--- | :--- |
| `GITHUB_TOKEN` | Built-in Secret | Issue inspection and closing | Injected automatically with `issues: write` | Implicit / Default |

---

## 6. Verification Proof
- **Trigger Verification**: Successfully dispatched via `gh workflow run issue-filter.yaml --ref workflow-fix/audit-all-workflows`.
- **Actionlint Status**: Passed 100% cleanly.
