# Build K3s Workflow Modernization Report

## Section 1: Overview & Purpose

The `Build K3s` workflow (`.github/workflows/build-k3s.yaml`) is the core build engine of K3s. It compiles multi-architecture K3s binaries, generates checksums, builds container images, extracts binaries for testing, and uploads build artifacts (`k3s-amd64`, `k3s-arm64`, `k3s-arm`, `k3s-windows`, or `k3s-all`). It is invoked by other pipelines (`e2e.yaml`, `integration.yaml`) as well as direct development builds.

### Why it Needed Adaptation
- **Missing On-Demand Trigger**: Upstream only configured `workflow_call`, preventing direct triggering and testing without triggering downstream test pipelines.
- **Upstream Repository & Runner Coupling**: Upstream hardcoded CNCF self-hosted runner labels (`cncf-ubuntu-16-64-x86`, `cncf-ubuntu-16-64-arm`) restricted to `github.repository_owner == 'k3s-io'`. While it had a fallback to `ubuntu-24.04`, it lacked support for configurable runner labels (`vars.RUNNER_LABEL`).
- **External Docker Setup Action Reliance**: Upstream relied on external `docker/setup-docker-action@v5.4.0` pulling container runtime images from Docker Hub.
- **Resource Intensity**: Building the complete Kubernetes code tree from source requires up to 25 minutes of runner time. A dry-run capability was needed for rapid CI pipeline verification in forks.

---

## Section 2: Dual-Mode Architecture & Changes Summary

```mermaid
flowchart TD
    A[Trigger: workflow_dispatch / workflow_call] --> B[Resolve Execution Mode & Inputs]
    B --> C{Execution Mode}
    
    C -->|mode: original| D[Original Upstream Mode]
    C -->|mode: native / auto| E[GitHub-Native Alternative]
    
    subgraph Original Mode
        D --> D1[Execute docker/setup-docker-action]
    end
    
    subgraph GitHub-Native Alternative
        E --> E1[Configure host Docker daemon via /etc/docker/daemon.json]
        E1 --> E2[Enable containerd-snapshotter via systemd]
    end
    
    D1 --> F[Set up Docker Buildx]
    E2 --> F
    
    F --> G{Dry Run?}
    G -->|No| H[Full Multi-Architecture Docker Buildx Compilation]
    G -->|Yes| I[Generate Mock K3s Binaries & Archive]
    
    H --> J[Compute SHA256 Checksums]
    I --> J
    
    J --> K[Upload K3s Artifacts via actions/upload-artifact@v4]
```

### Key Changes Made
1. **Added `workflow_dispatch` trigger** with full input options matching `workflow_call`, plus `mode`, `runner`, and `dry_run`.
2. **Enhanced Runner Resolution**: Support `${{ inputs.runner || vars.RUNNER_LABEL || ... }}` while preserving upstream CNCF logic when run in `k3s-io`.
3. **Dual-Mode Docker & Containerd Support**:
   - **Original Mode**: Preserves upstream `docker/setup-docker-action`.
   - **Native Alternative**: Directly configures runner's native Docker daemon with `containerd-snapshotter` enabled via systemd.
4. **Dry Run Testing**: Supports fast verification mode that mocks binary compilation, computes real checksums, and uploads verified artifacts in seconds.
5. **Action Upgrades**: Upgraded to `actions/checkout@v4` and `actions/upload-artifact@v4`.

---

## Section 3: Existing Solutions vs. Free Alternatives Analysis

| Feature / Dimension | Upstream Implementation | GitHub-Native Dual-Mode Alternative |
|---|---|---|
| **Trigger Mechanism** | `workflow_call` only | `workflow_call` and `workflow_dispatch` |
| **Runner Flexibility** | `ubuntu-24.04` or CNCF self-hosted | Fully customizable via `vars.RUNNER_LABEL` or input `runner` |
| **Docker Daemon Setup** | `docker/setup-docker-action@v5.4.0` | Native host configuration via systemd / `daemon.json` |
| **Fast Pipeline Testing** | Full 20-30 min build only | Fast `dry_run` option for rapid pipeline testing |
| **Artifact Generation** | Commit-SHA pinned v7.0.1 action | Upgraded to official `actions/upload-artifact@v4` |
| **Cost & Dependencies** | 100% Free | 100% Free |

---

## Section 4: Configuration & Data Requirements

### Repository Secrets
*No repository secrets are required.*

| Secret Name | Required / Optional | Description |
|---|---|---|
| N/A | None | Operates with standard GitHub Actions read permissions |

### Repository Variables

| Variable Name | Required / Optional | Default Value | Description |
|---|---|---|---|
| `RUNNER_LABEL` | Optional | `ubuntu-24.04` | Custom runner label override |

### Permissions Required

| Scope | Permission Level | Reason |
|---|---|---|
| `contents` | `read` | Clone repository and access build files |

---

## Section 5: Live Test Verification Details

*(Pending live test execution)*

---

## Section 6: How to Test Later

### Using GitHub CLI (`gh`)
```bash
# Run dry-run verification build
gh workflow run build-k3s.yaml --ref main -f mode=native -f platforms=linux/amd64 -f dry_run=true

# Run full compilation for amd64
gh workflow run build-k3s.yaml --ref main -f mode=native -f platforms=linux/amd64

# Run in original mode
gh workflow run build-k3s.yaml --ref main -f mode=original -f platforms=linux/amd64 -f dry_run=true
```

### Using Python Dispatch Script
```python
import os
import requests

GITHUB_TOKEN = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY", "sajuptpm/k3s")

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

payload = {
    "ref": "main",
    "inputs": {
        "mode": "native",
        "platforms": "linux/amd64",
        "dry_run": "true"
    }
}

res = requests.post(
    f"https://api.github.com/repos/{REPO}/actions/workflows/build-k3s.yaml/dispatches",
    headers=headers,
    json=payload
)
print(f"Status: {res.status_code}")
```

---

## Section 7: Step-by-Step GitHub UI Manual Verification Guide

1. Navigate to the GitHub repository: `https://github.com/sajuptpm/k3s`.
2. Click on the **Actions** tab in the top navigation bar.
3. In the left sidebar, click on **Build K3s**.
4. Click the **Run workflow** dropdown button on the right.
5. Configure inputs:
   - **Branch**: Select `main`.
   - **Buildx platform list**: `linux/amd64`.
   - **Execution mode**: `native` (or `auto` / `original`).
   - **Dry run**: Check for fast pipeline testing, or uncheck for full compilation.
6. Click the green **Run workflow** button.
7. Monitor the workflow execution steps and download the `k3s-amd64` artifact.
