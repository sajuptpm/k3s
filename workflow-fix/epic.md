# Workflow Fix & Audit Documentation: `epic.yaml`

## 1. Workflow Overview & Triggers
- **Workflow Name**: `Update epics`
- **Workflow File**: `.github/workflows/epic.yaml`
- **Original Purpose**: Automatically manages and tracks epic issues and their associated task lists using `cloudaper/epics-action@v1`.
- **Trigger Events**:
  - `issues`: On `opened`, `closed`, `reopened`
  - `workflow_dispatch`: Manual on-demand execution (Added for fork testing)
- **Job Dependency Graph**:
  - `epics`: Single job running on `ubuntu-24.04`.

---

## 2. Root Cause Analysis in Fork
In upstream K3s, `epic.yaml` only listened for issue lifecycle webhooks (`opened`, `closed`, `reopened`). In a newly created fork with no open issues or during CI testing, the workflow could not be dispatched or evaluated manually without opening dummy issues.

---

## 3. Detailed Code Changes & Rationale

### Added `workflow_dispatch` Trigger
Added `workflow_dispatch: {}` so maintainers can test the epics synchronization logic on demand.

```diff
 name: Update epics
 on:
   issues:
     types: [opened, closed, reopened]
+  workflow_dispatch: {}
 
 permissions:
   contents: read
```

---

## 4. Alternate Jobs & Feature Flags (If Applicable)
- **Applicable**: Not required. Operates using standard GitHub APIs.

---

## 5. Secrets & Variables Created / Required
| Name | Type | Purpose | How Generated / Format | Exact `gh` CLI Command |
| :--- | :--- | :--- | :--- | :--- |
| `GITHUB_TOKEN` | Built-in Secret | Issue inspection and label updating | Automatically injected with `issues: write` | Implicit / Default |

---

## 6. Verification Proof
- **Trigger Verification**: Successfully dispatched via `gh workflow run epic.yaml --ref workflow-fix/audit-all-workflows`.
- **Actionlint Status**: Passed 100% cleanly.
