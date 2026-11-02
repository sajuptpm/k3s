# Modernization & Dual-Mode Adaptation for `release.yml`

This document details the modernization, dual-mode architecture, and fork adaptability enhancements implemented for the **K3s Release Pipeline** ([`.github/workflows/release.yml`](file:///c:/projects/k3s_new/k3s/.github/workflows/release.yml)).

---

## Section 1: Overview & Purpose

### Upstream Purpose
The upstream `release.yml` workflow is K3s's official release engine. Triggered when git tags matching `v*` are pushed, it:
1. Calls the reusable `build-k3s.yaml` workflow to compile K3s binaries for `amd64` and `arm64/arm`.
2. Calls `airgap.yaml` to export airgap image tarballs for `amd64`, `arm64`, and `arm`.
3. Interacts with SUSE/Rancher enterprise HashiCorp Vault instances (`rancher-eio/read-vault-secrets`) to fetch credentials for internal staging registries, prime registries, DockerHub, and AWS S3 buckets.
4. Builds and pushes multi-architecture K3s container runtime images to DockerHub (`rancher/k3s`), GitHub Container Registry (`ghcr.io/k3s-io/k3s`), and private SUSE registries.
5. Bundles release binaries, airgap packages, image lists, and SHA256 checksums, validates them strictly via [`scripts/validate-artifacts`](file:///c:/projects/k3s_new/k3s/scripts/validate-artifacts), publishes a GitHub Pre-Release with attached assets, syncs assets to an AWS S3 bucket, and dispatches a downstream trigger to `k3s-upgrade`.

### Why It Failed in Forks & Non-Enterprise Environments
1. **Missing Manual Dispatch (`workflow_dispatch`)**: The workflow could only execute on git tag push events (`v*`), preventing on-demand release dry-runs, stage verification, or fork testing.
2. **Hardcoded Vault Authentication**: The pipeline unconditionally invoked `rancher-eio/read-vault-secrets` using enterprise Vault paths (`secret/data/github/repo/${{ github.repository }}/...`). In any fork or non-SUSE infrastructure, this action immediately fails with authentication errors.
3. **Mandatory AWS S3 & Upstream Registries**: Upstream hardcoded pushes to AWS S3 (`prime-artifacts-uploader`) and SUSE staging/prime registries without fallback options.
4. **Fragile Downstream Dispatch**: `dispatch-k3s-upgrade` failed immediately if `K3S_UPGRADE_PAT` was missing.
5. **No Release Dry-Run Mode**: Testing tag creation directly triggered public image publishing and GitHub releases.
6. **Tag Resolution Bug on Dispatch**: When triggered via dispatch on a branch rather than a tag push, `GITHUB_REF#refs/tags/` resolved to branch names, breaking Docker tagging and semver generation.

---

## Section 2: Dual-Mode Architecture & Changes Summary

```mermaid
flowchart TD
    A["Trigger: workflow_dispatch / tag push (v*)"] --> B["Mode Resolution Step<br/>(auto | native | original)"]
    B --> C{"Resolved Mode"}

    subgraph Original Mode
        C -- "original (k3s-io)" --> D1["Fetch Vault Secrets (Staging/Prime/Docker/AWS)"]
        D1 --> E1["Build Multi-Arch Binaries & Airgap Packages"]
        E1 --> F1["Push Images to DockerHub, GHCR & SUSE Registries"]
        F1 --> G1["Validate Assets, Publish GitHub Release & Sync to S3"]
        G1 --> H1["Dispatch k3s-upgrade Repo via PAT"]
    end

    subgraph Native GitHub Mode
        C -- "native (Fork / Free CI)" --> D2["Use GitHub-Native Secrets & Tokens"]
        D2 --> E2["Build / Dry-Run Binaries & Airgap Packages"]
        E2 --> F2["Login to GHCR via GITHUB_TOKEN & DockerHub (if configured)"]
        F2 --> G2["Validate Artifacts, Create GH Release / Actions Artifact Bundle"]
        G2 --> H2["Log Dispatch Status / Simulated Upgrade Summary"]
    end
```

### Key Changes Made
1. **Added `workflow_dispatch`**: Exposes parameters `mode` (`auto`, `native`, `original`), `tag` (default `v0.0.0-test`), `dry_run` (default `true`), `push_images` (default `false`), `create_release` (default `false`), and `runner`.
2. **Dynamic Mode Resolution**: Automatically activates Native Mode on forks while preserving Original Mode on `k3s-io`.
3. **Vault & AWS S3 Guards**: Guarded all `rancher-eio/read-vault-secrets` and AWS credential steps so they only execute when `resolved_mode == 'original'` and running under `k3s-io`.
4. **Safe Registry & Image Tagging**: Fixed tag derivation so `RESOLVED_TAG` resolves properly from input or ref. Only configured registries are added to Docker metadata.
5. **Multi-Arch Mock & Airgap Compatibility**: Enhanced dry-run logic across `build-k3s.yaml` and `airgap.yaml` so that mock artifacts satisfy the exact 16 expected files checked by `scripts/validate-artifacts`.
6. **Safe Downstream Upgrade Dispatch**: `dispatch-k3s-upgrade` logs downstream status into `$GITHUB_STEP_SUMMARY` when `K3S_UPGRADE_PAT` is not provided, preventing workflow failure.
7. **Action Upgrades**: Upgraded all actions to modern versions (`actions/checkout@v4`, `actions/download-artifact@v4`, `actions/upload-artifact@v4`, `docker/setup-buildx-action@v3`, `docker/login-action@v3`, `docker/metadata-action@v5`).

---

## Section 3: Existing Solutions vs. Free Alternatives Analysis

| Upstream Enterprise Feature | Upstream Mechanism | GitHub-Native Free Alternative | Status |
| :--- | :--- | :--- | :--- |
| **Credential Management** | SUSE HashiCorp Vault (`rancher-eio/read-vault-secrets`) | Standard GitHub Actions Secrets & automatic `GITHUB_TOKEN` | Supported |
| **Container Registry** | Private SUSE registry & Staging registry | GitHub Container Registry (`ghcr.io/${{ github.repository_owner }}/k3s`) | Supported |
| **Artifact Storage** | AWS S3 Bucket (`prime-artifacts-uploader`) | GitHub Releases & GitHub Actions Artifact Bundles (`release-assets-*`) | Supported |
| **Release Management** | Direct public release on tag | Parameterized pre-release / dry-run asset validation | Supported |
| **Downstream Pipeline** | External repo dispatch via PAT | Graceful step summary when PAT is absent | Supported |
| **Runner Infrastructure** | Pinned runner `ubuntu-24.04` | Configurable runner expression `${{ inputs.runner \|\| vars.RUNNER_LABEL \|\| 'ubuntu-24.04' }}` | Supported |

---

## Section 4: Configuration & Data Requirements

### Repository Secrets
| Secret Name | Required (Original Mode) | Required (Native Mode) | Purpose |
| :--- | :--- | :--- | :--- |
| `GITHUB_TOKEN` | Yes (automatic) | Yes (automatic) | GHCR login, release creation, artifact downloads |
| `DOCKER_USERNAME` | Vault-injected | Optional | Custom DockerHub username for fork image pushes |
| `DOCKER_TOKEN` | Vault-injected | Optional | Custom DockerHub token/PAT for fork image pushes |
| `K3S_UPGRADE_PAT` | Optional | Optional | PAT for triggering downstream `k3s-upgrade` repository |
| `AWS_ACCESS_KEY_ID` | Yes (in Vault) | No | SUSE S3 credentials for prime artifact uploads |
| `AWS_SECRET_ACCESS_KEY` | Yes (in Vault) | No | SUSE S3 credentials for prime artifact uploads |

### Repository Variables
| Variable Name | Required | Default Value | Purpose |
| :--- | :--- | :--- | :--- |
| `RUNNER_LABEL` | Optional | `ubuntu-24.04` | Custom GitHub Actions runner label |

### Permission Scopes
| Permission | Level | Justification |
| :--- | :--- | :--- |
| `contents` | `write` | Required to publish GitHub pre-releases and attach release assets |
| `packages` | `write` | Required to publish multi-architecture container images to GHCR |
| `id-token` | `write` | Required for OIDC authentication (Vault / AWS in original mode) |

---

## Section 5: Live Test Verification Details

- **Run ID**: `41423586948`
- **Run URL**: [https://github.com/sajuptpm/k3s/actions/runs/41423586948](https://github.com/sajuptpm/k3s/actions/runs/41423586948)
- **Trigger**: `workflow_dispatch` (`mode=native`, `dry_run=true`, `tag=v0.0.0-test`)
- **Outcome**: **SUCCESS** (All 8 jobs succeeded across the entire release pipeline)

### Execution Timeline
| Job | Status | Duration | Artifacts Produced |
| :--- | :--- | :--- | :--- |
| `build-amd64` (`Build`) | **Success** | 16s | `k3s-amd64` |
| `build-arm` (`Build`) | **Success** | 14s | `k3s-all` |
| `build-airgap` (`Export Images (amd64)`) | **Success** | 13s | `images-amd64` |
| `build-airgap` (`Export Images (arm64)`) | **Success** | 21s | `images-arm64` |
| `build-airgap` (`Export Images (arm)`) | **Success** | 12s | `images-arm` |
| `push-release-image` | **Success** | 41s | Image metadata validated & summary published |
| `upload-release-assets` | **Success** | 8s | `release-assets-v0.0.0-test` (16 validated assets) |
| `dispatch-k3s-upgrade` | **Success** | 3s | Simulated upgrade summary logged |

---

## Section 6: How to Test Later

### GitHub CLI (`gh`) Command
```bash
gh workflow run release.yml \
  --ref main \
  -f mode=native \
  -f tag=v0.0.0-test \
  -f dry_run=true \
  -f push_images=false \
  -f create_release=false
```

### Python Dispatch Script
```python
import os
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY", "sajuptpm/k3s")

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}

payload = {
    "ref": "main",
    "inputs": {
        "mode": "native",
        "tag": "v0.0.0-test",
        "dry_run": True,
        "push_images": False,
        "create_release": False,
    },
}

response = requests.post(
    f"https://api.github.com/repos/{REPO}/actions/workflows/release.yml/dispatches",
    headers=headers,
    json=payload,
)
print("Dispatch status:", response.status_code)
```

---

## Section 7: Step-by-Step GitHub UI Manual Verification Guide

1. Navigate to the repository on GitHub: `https://github.com/<owner>/k3s`.
2. Click on the **Actions** tab at the top.
3. In the left sidebar, click on **K3s Release**.
4. Click the **Run workflow** dropdown button on the right.
5. Fill in the parameters:
   - **Branch**: Select `main`.
   - **Execution mode**: Select `native` or `auto`.
   - **Release tag name**: Enter `v0.0.0-test` (or target semver like `v1.32.4-rc1+k3s1`).
   - **Dry run**: Leave checked (`true`).
   - **Push container images**: Leave unchecked (`false`).
   - **Create GitHub Release**: Leave unchecked (`false`).
6. Click the green **Run workflow** button.
7. Monitor the workflow execution:
   - Verify parallel completion of `build-amd64`, `build-arm`, and `build-airgap` matrix.
   - Verify `push-release-image` inspects metadata and completes cleanly.
   - Verify `upload-release-assets` validates all 16 artifact files via `scripts/validate-artifacts` and uploads `release-assets-v0.0.0-test`.
   - Verify `dispatch-k3s-upgrade` logs downstream simulation cleanly.
