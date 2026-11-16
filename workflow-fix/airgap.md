# Workflow Fix & Audit Documentation: `airgap.yaml`

## 1. Workflow Overview & Triggers
- **Workflow Name**: `Airgap Image Tarballs`
- **Workflow File**: `.github/workflows/airgap.yaml`
- **Original Purpose**: Packages and exports offline airgap container image tarballs across multiple architectures (`amd64`, `arm64`, `arm`) using Docker with the containerd snapshotter, compress them using `pigz`/`zstd`, and uploads them as build artifacts.
- **Trigger Events**:
  - `pull_request`: On changes to airgap packaging scripts
  - `workflow_call`: Called as a reusable workflow by `release.yml`
  - `workflow_dispatch`: Manual on-demand execution (Added for fork testing)
- **Job Dependency Graph**:
  - `build-airgap`: Matrix of 3 architecture jobs (`amd64`, `arm64`, `arm`) running on `ubuntu-24.04`.

---

## 2. Root Cause Analysis in Fork
In upstream K3s, `airgap.yaml` lacked `workflow_dispatch: {}`. Because it was only triggered via `pull_request` on specific paths or via `workflow_call` from the tag-triggered release workflow, it could not be tested or executed independently in a fork.

---

## 3. Detailed Code Changes & Rationale

### Added `workflow_dispatch` Trigger
```diff
 name: Airgap Image Tarballs
 on:
   pull_request:
     paths:
       - "scripts/package-airgap"
       - "scripts/airgap/image-list.txt"
       - ".github/workflows/airgap.yaml"
   workflow_call: {}
+  workflow_dispatch: {}
```

**Anti-Cheating & Integrity Guarantee**:
- Docker was configured with containerd snapshotter.
- `pigz` and `zstd` dependencies were installed.
- Real airgap image tarballs for `amd64`, `arm64`, and `arm` were generated and uploaded as GitHub Actions artifacts.

---

## 4. Alternate Jobs & Feature Flags (If Applicable)
- **Applicable**: Not required. Operates on standard `ubuntu-24.04` runners using Docker multiarch emulation.

---

## 5. Secrets & Variables Created / Required
| Name | Type | Purpose | How Generated / Format | Exact `gh` CLI Command |
| :--- | :--- | :--- | :--- | :--- |
| `GITHUB_TOKEN` | Built-in Secret | Checkout and artifact uploading | Automatically injected | Implicit / Default |

---

## 6. Verification Proof
- **Passing Run ID**: `43924631244`
- **Direct Run URL**: [https://github.com/sajuptpm/k3s/actions/runs/43924631244](https://github.com/sajuptpm/k3s/actions/runs/43924631244)
- **Duration**: 2 minutes 11 seconds
- **Branch / Commit Tested**: `workflow-fix/audit-all-workflows` (`fffbc4cbf`)
- **Job Status Breakdown**:

| Job Name | Job ID | Status | Conclusion | Duration | Note |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `Export Images (amd64)` | `133500716936` | `completed` | `success` | 2m 10s | Built and uploaded `images-amd64` artifact |
| `Export Images (arm64)` | `133500717002` | `completed` | `success` | 1m 47s | Built and uploaded `images-arm64` artifact |
| `Export Images (arm)` | `133500716356` | `completed` | `success` | 1m 48s | Built and uploaded `images-arm` artifact |
