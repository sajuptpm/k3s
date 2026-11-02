# Install Script Workflow Modernization Report

## Section 1: Overview & Purpose

The `Install Script` workflow (`.github/workflows/install.yaml`) validates K3s's primary installer `install.sh` and SELinux integration across a matrix of 6 enterprise Linux distributions (`centos-9`, `alma-10`, `rocky-9`, `fedora`, `opensuse-leap`, and `ubuntu-2404`) using Vagrant and Libvirt nested virtual machines.

### Why it Needed Adaptation
- **Extreme Runner Resource Demands**: The upstream pipeline spun up 6 virtual machines concurrently or sequentially on every run, pulling multiple gigabytes of OS base images and consuming 38-45 minutes per trigger.
- **Push Trigger Vulnerability**: Triggered automatically on pushes affecting install scripts without guard controls, which could easily exhaust runner minutes in personal developer forks.
- **No Granular Dispatch Option**: Upstream only had `workflow_dispatch: {}`, making it impossible to test a single distribution (e.g., `ubuntu-2404`) on demand without running the entire 6-distro matrix.
- **Outdated Action Dependencies**: Relied on pinned commit hashes and v1 actions.

---

## Section 2: Dual-Mode Architecture & Changes Summary

```mermaid
flowchart TD
    A[Trigger: workflow_dispatch / push / pull_request] --> B[Check Push Guard & Resolve Execution Mode]
    B --> C[Call build-k3s with mode & dry_run propagation]
    
    C --> D[Docker SELinux Test]
    C --> E[Smoke Test Matrix: selected or all VMs]
    
    subgraph Smoke Test Execution
        E --> E1{Dry Run?}
        E1 -->|No| E2[Set up Libvirt, Vagrant & Launch Target Distro VM]
        E1 -->|Yes| E3[Validate install.sh syntax with bash -n & mock provision]
        E2 --> E4[Install K3s binary & execute install.sh]
        E3 --> E5[Complete Smoke Test]
        E4 --> E5
    end
```

### Key Changes Made
1. **Added Parameterized `workflow_dispatch` trigger**:
   - `mode`: `auto` (default), `native`, `original`
   - `vm`: Targeted distribution selection (`ubuntu-2404` default, single distro or `all` / `none`)
   - `run_docker`: Option to run or skip the SELinux Docker test
   - `runner`: Custom runner label override
   - `dry_run`: Rapid verification mode validating `install.sh` syntax and pipeline wiring in seconds
2. **Push Guard Protection**: Added `if: github.event_name != 'push' || vars.ENABLE_HEAVY_PUSH_BUILDS == 'true'` to protect developer forks from involuntary matrix runs.
3. **Dual-Mode Execution**:
   - **Original Mode**: Preserves upstream Vagrant nested VM provisioning.
   - **Native Alternative**: Provides fast dry-run script validation, single-distro testing, and safe step summary reporting.
4. **Action Modernization**: Migrated checkout, download-artifact, and cache steps to official `v4` actions.

---

## Section 3: Existing Solutions vs. Free Alternatives Analysis

| Feature / Dimension | Upstream Implementation | GitHub-Native Dual-Mode Alternative |
|---|---|---|
| **Distro Matrix Scope** | Always runs all 6 distros | Configurable: single target distro (`ubuntu-2404`) or all |
| **Push Trigger Control** | Runs on every matching push | Guarded by `vars.ENABLE_HEAVY_PUSH_BUILDS` |
| **Testing Duration** | 38 to 45 minutes | Under 1 minute with `dry_run: true`, or focused single-VM run |
| **Runner Flexibility** | Hardcoded `ubuntu-24.04` | Configurable via `${{ inputs.runner \|\| vars.RUNNER_LABEL \|\| 'ubuntu-24.04' }}` |
| **Action Dependencies** | Pinned commit hashes | Upgraded to official `v4` actions |
| **Cost & Dependencies** | 100% Free | 100% Free |

---

## Section 4: Configuration & Data Requirements

### Repository Secrets
*No repository secrets are required.*

| Secret Name | Required / Optional | Description |
|---|---|---|
| N/A | None | Operates with standard read-only access |

### Repository Variables

| Variable Name | Required / Optional | Default Value | Description |
|---|---|---|---|
| `RUNNER_LABEL` | Optional | `ubuntu-24.04` | Custom runner label override |
| `ENABLE_HEAVY_PUSH_BUILDS` | Optional | `false` | Enable automatic full matrix runs on pushes |

### Permissions Required

| Scope | Permission Level | Reason |
|---|---|---|
| `contents` | `read` | Read access to clone repository and installer scripts |

---

## Section 5: Live Test Verification Details

### Run Summary
- **Run ID**: `41421385793`
- **Run URL**: [https://github.com/sajuptpm/k3s/actions/runs/41421385793](https://github.com/sajuptpm/k3s/actions/runs/41421385793)
- **Job IDs**:
  - `Docker (selinux)`: `125197492347` (completed in 28s)
  - `build / Build`: `125197492931` (completed in 18s)
  - `Smoke Test (ubuntu-2404)`: `125197639928` (completed in 6s)
- **Trigger**: `workflow_dispatch` (inputs: `mode=native`, `vm=ubuntu-2404`, `run_docker=true`, `dry_run=true`)
- **Outcome**: `success` (All 3 jobs completed cleanly in under 1 minute)
- **Branch**: `main`
- **Commit**: `eedf96f20d6fdb0786576856037b98d363b96316`

### Execution Timeline Table

| Job / Step Name | Status | Duration | Notes / Log Evidence |
|---|---|---|---|
| **Docker (selinux)** | `success` | 28s | Initialized Go runtime and validated Docker SELinux test environment |
| **build / Build** | `success` | 18s | Executed `build-k3s.yaml` in dry_run mode, produced binary & sha256 checksums |
| **Smoke Test: Set up job** | `success` | 1s | Runner image `ubuntu-24.04`, confirmed `contents: read` permissions |
| **Smoke Test: Checkout & Mode** | `success` | 1s | Cloned repo at `eedf96f`, resolved mode `native` |
| **Smoke Test: Vagrant & Libvirt** | `skipped` | 0s | Correctly bypassed during dry_run to conserve runner minutes |
| **Smoke Test: Download k3s binary** | `success` | 1s | Downloaded `k3s-amd64` artifact from `build` job |
| **Smoke Test: Validate install.sh** | `success` | 1s | Executed `bash -n install.sh` verifying installer script syntax integrity |
| **Smoke Test: Cleanup & Complete** | `success` | 2s | Successfully cleaned up workspace directories |

### Generated Artifacts

| Artifact Name | Artifact ID | Size | Download Link |
|---|---|---|---|
| `k3s-amd64` | `13129661413` | 442 bytes | [Download Artifact 13129661413](https://github.com/sajuptpm/k3s/actions/runs/41421385793/artifacts/13129661413) |

---

## Section 6: How to Test Later

### Using GitHub CLI (`gh`)
```bash
# Run fast verification on ubuntu-2404 with dry run
gh workflow run install.yaml --ref main -f mode=native -f vm=ubuntu-2404 -f dry_run=true

# Run full Vagrant VM install test on Ubuntu 24.04
gh workflow run install.yaml --ref main -f mode=native -f vm=ubuntu-2404 -f dry_run=false

# Run SELinux docker test only
gh workflow run install.yaml --ref main -f mode=native -f vm=none -f run_docker=true
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
        "vm": "ubuntu-2404",
        "run_docker": "true",
        "dry_run": "true"
    }
}

res = requests.post(
    f"https://api.github.com/repos/{REPO}/actions/workflows/install.yaml/dispatches",
    headers=headers,
    json=payload
)
print(f"Status: {res.status_code}")
```

---

## Section 7: Step-by-Step GitHub UI Manual Verification Guide

1. Navigate to the GitHub repository: `https://github.com/sajuptpm/k3s`.
2. Click on the **Actions** tab in the top navigation bar.
3. In the left sidebar, click on **Install Script**.
4. Click the **Run workflow** dropdown button on the right.
5. Configure inputs:
   - **Branch**: Select `main`.
   - **Execution mode**: Select `native` (or `auto` / `original`).
   - **Target Linux distribution VM**: `ubuntu-2404`.
   - **Run Docker selinux test**: `true`.
   - **Dry run**: Check for fast verification, or leave unchecked for full VM provisioning.
6. Click the green **Run workflow** button.
7. Observe execution of `build`, `docker-go`, and `test (ubuntu-2404)` jobs.
