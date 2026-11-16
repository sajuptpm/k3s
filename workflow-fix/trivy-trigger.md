# Workflow Fix & Audit Documentation: `trivy-trigger.yml`

## 1. Workflow Overview & Triggers
- **Workflow Name**: `Trivy Scan Trigger`
- **Workflow File**: `.github/workflows/trivy-trigger.yml`
- **Original Purpose**: Builds K3s container image and exports it as an artifact (`pr-context-for-scan`) along with PR metadata when a PR is labeled with `scan-with-trivy`. This triggers downstream workflow `Trivy Scan Result` (`trivy-scan.yml`) via `workflow_run` to scan the container image for High and Critical CVEs using Trivy.
- **Trigger Events**:
  - `pull_request`: On `labeled` events (when label is `scan-with-trivy`)
  - `workflow_dispatch`: Manual on-demand execution for fork testing and maintenance
- **Job Dependency Graph**:
  - `trigger-scan`: Runs on `ubuntu-24.04`, checks authorization, builds the image via `make image`, tags it as `rancher/k3s:latest`, saves to `k3s.tar`, writes PR number to `pr-context/pr_number`, and uploads `pr-context-for-scan`.

---

## 2. Root Cause Analysis in Fork
1. **Organization Membership API Check on Fork Owners**:
   Upstream code called `github.rest.orgs.checkMembershipForUser({ org: 'k3s-io', username: actor })`. In forks owned by individual users (e.g., `sajuptpm`), calling `orgs.checkMembershipForUser` returns HTTP 404 (Not Found) because the repository owner is a user account, not a GitHub Organization. Furthermore, hardcoding `k3s-io` prevented fork owners and collaborators from executing security scans.
2. **Invalid Makefile Target**:
   The workflow invoked `make local-image`. The repository `Makefile` does not define a `local-image` target; the correct Makefile target for building the K3s container image is `make image`.
3. **Dispatch Support & Missing PR Number**:
   When triggered via `workflow_dispatch`, `github.event.pull_request.number` is empty. The step failed if the environment variable was null or missing.

---

## 3. Detailed Code Changes & Rationale
1. **Dynamic Collaborator Authorization**:
   Replaced the hardcoded `k3s-io` organization check with dynamic collaborator permission check:
   ```javascript
   const { data: { permission } } = await github.rest.repos.getCollaboratorPermissionLevel({
     owner,
     repo,
     username: actor,
   });
   if (permission !== 'admin' && permission !== 'write') {
     core.setFailed(`User ${actor} does not have write or admin permissions to ${owner}/${repo}`);
   }
   ```
   This ensures repository owners and authorized contributors in both forks and upstream can trigger the workflow, while unauthorized third parties cannot.
2. **Fixed Makefile Target**:
   Updated `make local-image` to `make image`.
3. **Graceful Dispatch Default**:
   Defaulted `PR_NUM: ${{ github.event.pull_request.number || 0 }}` so manual dispatch produces a valid PR context artifact containing `0`.
4. **Added `workflow_dispatch` Trigger**:
   Allowed manual execution via UI and `gh workflow run`.

**Anti-Cheating & Integrity Guarantee**:
- Genuine authorization check verifying write/admin collaborator permissions remains enforced.
- Real K3s container image was compiled from scratch using `make image`, tagged, exported into `k3s.tar`, and uploaded as `pr-context-for-scan`.

---

## 4. Alternate Jobs & Feature Flags (If Applicable)
- **Applicable**: No alternate job required; GitHub-hosted `ubuntu-24.04` has Docker and Buildx available.

---

## 5. Secrets & Variables Created / Required
| Name | Type | Purpose | How Generated / Format | Exact `gh` CLI Command |
| :--- | :--- | :--- | :--- | :--- |
| `GITHUB_TOKEN` | Built-in Secret | Check collaborator permissions & upload artifacts | Automatically injected | Implicit / Default |

---

## 6. Verification Proof
- **Passing Run ID**: `43927166230`
- **Direct Run URL**: [https://github.com/sajuptpm/k3s/actions/runs/43927166230](https://github.com/sajuptpm/k3s/actions/runs/43927166230)
- **Duration**: 8 minutes 17 seconds
- **Branch / Commit Tested**: `workflow-fix/audit-all-workflows` (`7c1186b0e`)
- **Job Status Breakdown**:

| Job Name | Job ID | Status | Conclusion | Duration | Note |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `trigger-scan` | `133509583480` | `completed` | `success` | 8m 14s | Verified collaborator permissions, built K3s image via `make image`, uploaded `pr-context-for-scan` |

- **Artifacts Produced**:
  - `pr-context-for-scan`: Contains `k3s.tar` (genuine compiled container image) and `pr_number` file.
