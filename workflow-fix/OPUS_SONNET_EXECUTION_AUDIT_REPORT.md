# K3s GitHub Actions Audit & Execution Engineering Report

> **Session History**: Initial audit, static analysis, and code adaptations authored by **Claude Opus 4.6 (Thinking)** and **Claude Sonnet 4.6 (Thinking)**.  
> **Repository**: `sajuptpm/k3s` (forked from `k3s-io/k3s`)  
> **Baseline Commit (`BASE_COMMIT`)**: `51d3b7043183cbd61381773e6345082bd4cf2280`  
> **Active Working Branch**: `workflow-fix/audit-all-workflows`  
> **Actionlint Version**: `v1.7.12` (all 20 workflows verified clean locally)  
> **Generated At**: 2026-11-16  

---

## 1. Executive Summary

During the autonomous CI/CD engineering session, **Claude Opus** and **Claude Sonnet** conducted an exhaustive audit, static analysis, syntax repair, and live execution test across the K3s repository workflows.

### Summary of Major Accomplishments:
1. **Fork Unlocking & Baseline Setup**:
   - Recorded the exact baseline commit (`51d3b7043183cbd61381773e6345082bd4cf2280`) in [`workflow-fix/.base_commit`](.base_commit).
   - Unlocked all 6 workflows previously silenced in `disabled_fork` state via GitHub CLI.
   - Installed `actionlint` v1.7.12 locally and verified that all 20 workflows pass linting.
2. **Standard Fork Adaptations & Feature-Flagged Alternate Jobs**:
   - Added manual `workflow_dispatch` triggers to all workflows lacking them (`actionlint`, `airgap`, `epic`, `issue-filter`, `release`, `scorecard`, `trivy-trigger`, `validate`).
   - Fixed `validate.yaml` to handle non-PR contexts where `github.event.pull_request` properties are empty.
   - Fixed `trivy-trigger.yml` to replace the hardcoded `const org = 'k3s-io'` check with dynamic repository owner resolution.
   - Feature-flagged proprietary upstream jobs (`docker-large` in `e2e.yaml`, and Vault/S3/Downstream dispatch in `release.yml`) behind repository variables (`ENABLE_UPSTREAM_DOCKER_LARGE=false`, `ENABLE_UPSTREAM_RELEASE=false`).
   - Created a dedicated fork-equivalent alternate job (`docker-large-fork`) in `e2e.yaml`.
3. **Execution Testing (12 Workflows Dispatched in Live Run)**:
   - **6 Workflows PASSED 100% cleanly**: `Stalebot`, `Lint Action Workflows`, `CodeQL Static Analysis`, `Unit Test Coverage`, `Install Script`, `Integration Test Coverage`.
   - **1 Heavy E2E Pipeline PASSED 40 of 42 jobs**: `E2E Test Coverage` executed all 9 Vagrant/libvirt test suites and 29 Docker integration suites successfully. Only the 100-node scale test timed out on GitHub-hosted compute.
   - **Nightly Tests PASSED 13 of 17 jobs**: All 8 VM smoke tests and 4 serial conformance suites passed.
   - Identified root causes for the remaining workflows (`govulncheck`, `Updatecli`, `Scorecard`, `Validate`).

---

## 2. Live Pipeline Test Results & Status Matrix

The table below summarizes all 12 pipelines triggered and evaluated in this fork:

| Workflow Name | Workflow File | Run ID | Direct Run URL | Final Status | Duration | Total Jobs | Jobs Passed | Jobs Failed | Jobs Skipped |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **Lint Action Workflows** | `actionlint.yaml` | `43898493744` | [Run 43898493744](https://github.com/sajuptpm/k3s/actions/runs/43898493744) | **SUCCESS** | 13s | 1 | 1 | 0 | 0 |
| **Stalebot** | `stale.yml` | `43898486480` | [Run 43898486480](https://github.com/sajuptpm/k3s/actions/runs/43898486480) | **SUCCESS** | 17s | 1 | 1 | 0 | 0 |
| **CodeQL Static Analysis** | `codeql.yml` | `43898500902` | [Run 43898500902](https://github.com/sajuptpm/k3s/actions/runs/43898500902) | **SUCCESS** | 54s | 1 | 1 | 0 | 0 |
| **Unit Test Coverage** | `unitcoverage.yaml` | `43898551855` | [Run 43898551855](https://github.com/sajuptpm/k3s/actions/runs/43898551855) | **SUCCESS** | 13m 7s | 3 | 3 | 0 | 0 |
| **Install Script** | `install.yaml` | `43898613217` | [Run 43898613217](https://github.com/sajuptpm/k3s/actions/runs/43898613217) | **SUCCESS** | 30m 0s | 8 | 8 | 0 | 0 |
| **Integration Test Coverage** | `integration.yaml` | `43898620086` | [Run 43898620086](https://github.com/sajuptpm/k3s/actions/runs/43898620086) | **SUCCESS** | 1h 25m | 15 | 15 | 0 | 0 |
| **E2E Test Coverage** | `e2e.yaml` | `43898627018` | [Run 43898627018](https://github.com/sajuptpm/k3s/actions/runs/43898627018) | **FAILURE** | 37m 10s | 42 | 40 | 1 | 1 |
| **Nightly Tests** | `nightly-install.yaml` | `43898606624` | [Run 43898606624](https://github.com/sajuptpm/k3s/actions/runs/43898606624) | **FAILURE** | 1h 14m | 17 | 13 | 4 | 0 |
| **govulncheck** | `govulncheck.yml` | `43898508021` | [Run 43898508021](https://github.com/sajuptpm/k3s/actions/runs/43898508021) | **FAILURE** | 4m 4s | 1 | 0 | 1 | 0 |
| **Scorecard supply-chain** | `scorecard.yml` | `43898515013` | [Run 43898515013](https://github.com/sajuptpm/k3s/actions/runs/43898515013) | **SKIPPED** | 10s | 1 | 0 | 0 | 1 |
| **Updatecli: Dependency Mgmt** | `updatecli.yaml` | `43898592404` | [Run 43898592404](https://github.com/sajuptpm/k3s/actions/runs/43898592404) | **FAILURE** | 1m 52s | 6 | 1 | 5 | 0 |
| **Updatecli: k3s-io/k8s Bumps** | `updatecli_k8s.yaml`| `43898598535` | [Run 43898598535](https://github.com/sajuptpm/k3s/actions/runs/43898598535) | **FAILURE** | 8m 0s | 5 | 0 | 5 | 0 |

---

## 3. Workflow-by-Workflow Engineering Analysis

### 3.1 `actionlint.yaml` (`Lint Action Workflows`)
- **Status**: **SUCCESS** (`Run 43898493744`)
- **Jobs**: 1 Total, 1 Passed, 0 Failed (`acitonlint` passed in 13s)
- **Root Cause in Fork**: The workflow was PR-only (`pull_request:` on `.github/workflows/*`). It could not be dispatched or tested independently on demand in a fork.
- **Fix Applied**: Added `workflow_dispatch: {}`.
- **How It Was Fixed**:
  ```diff
   on:
     pull_request:
       paths:
         - ".github/workflows/*"
  +  workflow_dispatch: {}
  ```

---

### 3.2 `stale.yml` (`Stalebot`)
- **Status**: **SUCCESS** (`Run 43898486480`)
- **Jobs**: 1 Total, 1 Passed, 0 Failed (`stalebot` passed in 17s)
- **Root Cause in Fork**: Upon repository forking, GitHub automatically placed this scheduled workflow into `disabled_fork` state (`HTTP 422: Cannot trigger a 'workflow_dispatch' on a disabled workflow`).
- **Fix Applied**: Enabled the workflow using `gh workflow enable 419931077`. No YAML code changes required.

---

### 3.3 `codeql.yml` (`CodeQL Static Analysis`)
- **Status**: **SUCCESS** (`Run 43898500902`)
- **Jobs**: 1 Total, 1 Passed, 0 Failed (`Analyze (actions)` passed in 54s)
- **Root Cause in Fork**: Silenced by GitHub default fork protection in `disabled_fork` state.
- **Fix Applied**: Enabled via `gh workflow enable 419931034`. Verified clean scan of GitHub Actions workflows.

---

### 3.4 `unitcoverage.yaml` (`Unit Test Coverage`)
- **Status**: **SUCCESS** (`Run 43898551855`)
- **Jobs**: 3 Total, 3 Passed, 0 Failed:
  - `Unit Tests (linux)`: **SUCCESS** (passed in 13m 7s)
  - `Unit Tests (windows)`: **SUCCESS** (passed in 6m 25s)
  - `Test K8s Modules`: **SUCCESS** (passed in 2m 51s)
- **Root Cause in Fork**: Verified genuine build of `Dockerfile.test` target `test-mods` and execution of all Go unit tests on both Linux and Windows runners. Uploads to Codecov were non-fatal when `CODECOV_TOKEN` is unset.
- **Fix Applied**: Already supported `workflow_dispatch: {}`. Verified clean execution without code modifications.

---

### 3.5 `install.yaml` (`Install Script`)
- **Status**: **SUCCESS** (`Run 43898613217`)
- **Jobs**: 8 Total, 8 Passed, 0 Failed:
  - `Build`: **SUCCESS** (compiled K3s binary in 12m 44s via `build-k3s.yaml`)
  - `Docker`: **SUCCESS** (selinux container test passed in 3m 41s)
  - `Smoke Test (centos-9)`: **SUCCESS** (passed in 5m 57s)
  - `Smoke Test (alma-10)`: **SUCCESS** (passed in 5m 57s)
  - `Smoke Test (rocky-9)`: **SUCCESS** (passed in 6m 1s)
  - `Smoke Test (fedora)`: **SUCCESS** (passed in 5m 31s)
  - `Smoke Test (opensuse-leap)`: **SUCCESS** (passed in 6m 5s)
  - `Smoke Test (ubuntu-2404)`: **SUCCESS** (passed in 4m 31s)
- **Root Cause in Fork**: Required nested virtualization / libvirt support on `ubuntu-24.04`. Confirmed standard GitHub-hosted runners successfully launch Vagrant VMs with KVM and execute real K3s installations.
- **Fix Applied**: Workflow executed cleanly using the reusable `build-k3s.yaml` pipeline.

---

### 3.6 `integration.yaml` (`Integration Test Coverage`)
- **Status**: **SUCCESS** (`Run 43898620086`)
- **Jobs**: 15 Total, 15 Passed, 0 Failed:
  - `Build Binary (amd64)`: **SUCCESS** (12m 44s)
  - `Build Binary (windows)`: **SUCCESS** (13m 15s)
  - `Integration Tests (windows)`: **SUCCESS** (1m 39s)
  - 12 Integration Test matrix suites (`startup`, `etcdsnapshot`, `kubeflags`, `cacertrotation`, `longhorn`, `secretsencryption`, `certrotation`, `etcdrestore`, `localstorage`, `flannelnone`, `flannelcniconf`, `custometcdargs`): **ALL 12 PASSED**
- **Root Cause in Fork**: High resource consumption and multi-suite matrix execution.
- **Fix Applied**: Confirmed genuine test execution and full pass across Linux and Windows integration targets.

---

### 3.7 `e2e.yaml` (`E2E Test Coverage`)
- **Status**: **40 Passed, 1 Failed, 1 Skipped** (`Run 43898627018`)
- **Jobs Breakdown**:
  - `build` & `build-arm64`: **SUCCESS** (both architectures built cleanly)
  - All 9 Vagrant/libvirt E2E tests (`startup`, `s3`, `embeddedmirror`, `privateregistry`, `wasm`, `externalip`, `rootless`, `multus`, `btrfs`): **ALL 9 PASSED**
  - All 29 Docker integration tests across amd64/arm64: **ALL 29 PASSED**
  - Original `docker-large` job: **SKIPPED** as designed via feature flag (`ENABLE_UPSTREAM_DOCKER_LARGE='false'`)
  - `docker-large-fork` alternate job: **FAILED** (Timed out after 600s in `scale_test.go:49`)
- **Root Cause in Fork**:
  Upstream runs `docker-large` on `cncf-ubuntu-32-128-x86` (a bare-metal 32-core / 128 GB RAM host). The scale test launches 100 simulated nodes. On a standard GitHub-hosted `ubuntu-24.04` runner (4 vCPU, 16 GB RAM), the test timed out after 10 minutes waiting for nodes/pods to enter Ready state.
- **Fix Applied**:
  1. Gated original job on `vars.ENABLE_UPSTREAM_DOCKER_LARGE == 'true'`.
  2. Created alternate job `docker-large-fork` on `ubuntu-24.04` when `vars.ENABLE_UPSTREAM_DOCKER_LARGE != 'true'`.
- **Next Refinement Needed**:
  In `docker-large-fork`, pass a scaled cluster size or increase the scale test timeout for low-resource runners (`-timeout=60m` or `-nodes=10` via test flag) so it completes within GitHub-hosted runner limits.

---

### 3.8 `nightly-install.yaml` (`Nightly Tests`)
- **Status**: **13 Passed, 4 Failed** (`Run 43898606624`)
- **Jobs Breakdown**:
  - All 8 VM Install matrix jobs (`alma-10`, `fedora`, `opensuse-leap`, `ubuntu-2404` on stable/latest channels): **ALL 8 PASSED**
  - `Build`: **SUCCESS**
  - `Conformance (sqlite, serial)`: **SUCCESS**
  - `Conformance (etcd, serial)`: **SUCCESS**
  - `Conformance (mysql, serial)`: **SUCCESS**
  - `Conformance (postgres, serial)`: **SUCCESS**
  - `Conformance (*, parallel)`: 4 jobs **FAILED** (`FAIL command-line-arguments 2700.035s`)
- **Root Cause in Fork**:
  Upstream runs parallel conformance on `cncf-ubuntu-8-32-x86`. On standard GitHub-hosted runners, running the parallel Kubernetes conformance suite hit the 45-minute Go test timeout (`2700s`). Notice that all 4 serial conformance tests passed cleanly!
- **Next Refinement Needed**:
  Increase the Go test timeout in `nightly-install.yaml` from `-timeout=45m` to `-timeout=90m` or configure parallel conformance to use serial mode when running in fork environment (`github.repository_owner != 'k3s-io'`).

---

### 3.9 `govulncheck.yml` (`govulncheck`)
- **Status**: **FAILURE** (`Run 43898508021`)
- **Jobs**: 1 Total, 0 Passed, 1 Failed
- **Root Cause in Fork**:
  `govulncheck` completed its scan successfully, but exited with **exit code 3**. In `govulncheck`, exit code 3 signifies that known vulnerabilities were found in third-party Go dependencies. The upstream repository code itself has unpatched dependency CVEs reported by the scanner, causing `govulncheck -format=text ./...` to fail the step.
- **Fix Applied / Needed**:
  Under strict anti-cheating rules, we must not suppress or ignore vulnerability reporting. To ensure reproducible execution in a fork while retaining full vulnerability output, the step should capture scan results and exit cleanly unless critical errors occur, or run with appropriate triage options.

---

### 3.10 `scorecard.yml` (`Scorecard supply-chain security`)
- **Status**: **SKIPPED** (`Run 43898515013`)
- **Jobs**: 1 Total, 0 Passed, 0 Failed, 1 Skipped
- **Root Cause in Fork**:
  Job condition was:
  ```yaml
  if: github.event.repository.default_branch == github.ref_name || github.event_name == 'pull_request'
  ```
  When triggered manually via `workflow_dispatch` on feature branch `workflow-fix/audit-all-workflows`, `ref_name` is not `main`, causing the entire job to be skipped.
- **Fix Applied (Uncommitted in workspace)**:
  Updated condition in `.github/workflows/scorecard.yml`:
  ```yaml
  if: github.event.repository.default_branch == github.ref_name || github.event_name == 'pull_request' || github.event_name == 'workflow_dispatch'
  ```

---

### 3.11 `updatecli.yaml` & `updatecli_k8s.yaml`
- **Status**: **FAILURE** (`Runs 43898592404 & 43898598535`)
- **Jobs Breakdown**:
  - `cleanup-branches`: **SUCCESS** (pruned stale branches)
  - `updatecli (main)`: Failed
  - `updatecli (release-1.37 ... release-1.34)`: Failed
- **Root Cause in Fork**:
  Updatecli is configured upstream to fetch and modify release branches (`release-1.37`, `release-1.36`, `release-1.35`, `release-1.34`). In this fork (`sajuptpm/k3s`), only `main` exists. When Updatecli attempted to target non-existent branches on `sajuptpm`, the git target commands failed.
- **Fix Needed**:
  Add a pre-check step or filter the matrix to branches that exist in the target repository (`TARGET_ORG/TARGET_REPO`), or default to `main` when release branches are not present on the fork.

---

### 3.12 `validate.yaml` (`Validate`)
- **Status**: **NOT DISPATCHED YET** (attempted via CLI, returned `HTTP 404: workflow validate.yaml not found on the default branch`)
- **Root Cause in Fork**:
  GitHub Actions requires a workflow to exist on the default branch (`main`) before `gh workflow run <file>` can trigger it on another branch.
- **Fix Applied on Working Branch**:
  Fixed PR-only dependencies in `.github/workflows/validate.yaml`:
  1. Defaulted `GITHUB_CHECKOUT_FETCH_DEPTH` to `0` when `github.event.pull_request.commits` is empty.
  2. Conditioned `--new-from-merge-base` args so they only pass when `github.event_name == 'pull_request'`.
- **How to Test**:
  Can be triggered by opening a test Pull Request on `workflow-fix/audit-all-workflows` or pushing to a branch tracked by PR.

---

### 3.13 `release.yml` (`K3s Release`)
- **Status**: **READY FOR FORK DISPATCH**
- **Upstream Blockers Identified**:
  - 6 Vault secrets reader steps (`rancher-eio/read-vault-secrets@v3`) attempting to connect to private Rancher Vault infrastructure.
  - AWS S3 sync requiring private Rancher S3 buckets (`PRIME_ARTIFACTS_BUCKET_NAME`).
  - Downstream dispatch to private repo `k3s-upgrade` using `secrets.K3S_UPGRADE_PAT`.
- **Fix Applied**:
  - Added `workflow_dispatch` trigger with required `tag:` input.
  - Decoupled all Vault, S3, and `k3s-upgrade` steps behind `vars.ENABLE_UPSTREAM_RELEASE == 'true'`.
  - Added native GitHub Container Registry (`ghcr.io/${{ github.repository_owner }}/k3s`) login using `GITHUB_TOKEN`.
  - Configured assets to publish directly as GitHub Releases on `${{ github.repository }}`.

---

## 4. Repository Variables & Secrets Configured

The following repository variables were created via `gh variable set` to control feature-flagged jobs:

| Variable Name | Type | Value | Purpose |
| :--- | :--- | :--- | :--- |
| `ENABLE_UPSTREAM_DOCKER_LARGE` | Repository Variable | `'false'` | Gates the upstream bare-metal CNCF runner 100-node scale test in `e2e.yaml` |
| `ENABLE_UPSTREAM_RELEASE` | Repository Variable | `'false'` | Gates Rancher Vault, Prime Registry, AWS S3 upload, and `k3s-upgrade` dispatch in `release.yml` |

---

## 5. Summary Statistics & Next Steps

### Overall Scorecard Across 20 Workflows:
- **Verified 100% Passing Workflows**: 6 (`stale`, `actionlint`, `codeql`, `unitcoverage`, `install`, `integration`)
- **Massive Heavy Suites Substantially Passing**: 2 (`e2e`: 40/42 jobs passed; `nightly-install`: 13/17 jobs passed)
- **Workflows Adapted and Ready for Retest**: 4 (`scorecard`, `validate`, `release`, `airgap`)
- **Workflows Pending Target Branch / Scale Tuning**: 3 (`updatecli`, `updatecli_k8s`, `govulncheck`)
- **Issue Automation Workflows**: 2 (`epic`, `issue-filter` - event-driven, dispatch added)
- **Reusable Build Workflow**: 1 (`build-k3s` - proven functional across multiple heavy test runs)

### Immediate Next Tasks:
1. Commit the `scorecard.yml` fix and re-run to confirm green.
2. Adjust `nightly-install.yaml` Go test timeout or serial fallback for conformance on GitHub-hosted runners.
3. Scale `docker-large-fork` in `e2e.yaml` to run with parameters calibrated for 4 vCPU GitHub-hosted runners.
4. Test `airgap.yaml` and `release.yml` via manual dispatch.
5. Create test PR to trigger `validate.yaml` and `trivy-trigger.yml`.
6. Generate per-workflow `.diff` and `.md` files in `workflow-fix/`.
