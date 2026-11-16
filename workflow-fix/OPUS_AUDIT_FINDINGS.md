# K3s GitHub Actions Workflow Audit & Engineering Findings

> **Audit Baseline Session**: Conducted with Claude Opus 4.6  
> **Repository**: `sajuptpm/k3s` (forked from `k3s-io/k3s`)  
> **Baseline Commit (`BASE_COMMIT`)**: `51d3b7043183cbd61381773e6345082bd4cf2280`  
> **Working Branch**: `workflow-fix/audit-all-workflows`  
> **Actionlint Version**: `v1.7.12` (all 20 workflows validated locally)  
> **Local Environment**: Windows 11 / PowerShell / Go / Python 3.13 / GitHub CLI (`gh`)  

---

## 1. Executive Summary & Environment Baseline

A comprehensive repository audit was conducted across all 20 GitHub Actions workflow files inside `.github/workflows/`. The baseline Git tree was confirmed clean at commit `51d3b7043183cbd61381773e6345082bd4cf2280`.

### Key Environment Identifiers
- **Authenticated Account**: `sajuptpm` (`GH_TOKEN` active)
- **Token Scopes**: `gist`, `repo`, `workflow` (Note: `read:org` missing, which impacts org membership queries in `trivy-trigger.yml`)
- **Fork Target**: `sajuptpm/k3s`
- **Initial Fork Workflow State**: GitHub automatically disabled scheduled/inbound workflows upon forking (`state: disabled_fork`). These were subsequently enabled via `gh workflow enable`.

---

## 2. Inventory & Classification Matrix

All 20 workflows were audited and categorized into 5 execution tiers based on dependencies, runtime duration, and risk profile:

| Tier | Category | Workflows Included | Focus Area |
| :--- | :--- | :--- | :--- |
| **Tier 1** | Simple / Event-Driven | `stale.yml`, `epic.yaml`, `issue-filter.yaml`, `actionlint.yaml` | Trivial runtime, issue/PR automation, adding `workflow_dispatch` |
| **Tier 2** | Security & Static Analysis | `codeql.yml`, `govulncheck.yml`, `scorecard.yml`, `trivy-trigger.yml`, `trivy-scan.yml` | CodeQL, SARIF, vulnerability scanning, org-permission dynamic adaptation |
| **Tier 3** | Core Build & Unit Testing | `unitcoverage.yaml`, `validate.yaml`, `build-k3s.yaml` | Foundation compilation and linter pipeline. `build-k3s.yaml` is the reusable build dependency for all downstream tests |
| **Tier 4** | Integration & E2E Testing | `airgap.yaml`, `install.yaml`, `integration.yaml`, `e2e.yaml`, `nightly-install.yaml` | Heavy integration tests (Vagrant/KVM, Docker, Ginkgo), matrix runners, multi-arch builds |
| **Tier 5** | Release & Automation | `release.yml`, `updatecli.yaml`, `updatecli_k8s.yaml` | Complex release packaging (multi-arch images, airgap tarballs, GitHub release, GHCR), external secrets & updatecli runs |

---

## 3. Detailed Audit Findings Per Workflow

### 3.1 `stale.yml` (`Stalebot`)
- **Triggers**: `schedule` (`cron: '0 20 * * *'`), `workflow_dispatch`
- **Runner**: `ubuntu-24.04`
- **Actions**: `actions/stale@v11.0.0`
- **Upstream Assumptions**: None. No hardcoded repository checks.
- **Status in Fork**: Initially in `disabled_fork` state; enabled via `gh workflow enable 419931077`.
- **Adaptations Needed**: None (already has dispatch trigger and uses standard runners).

### 3.2 `epic.yaml` (`Update epics`)
- **Triggers**: `issues` (`opened`, `closed`, `reopened`)
- **Runner**: `ubuntu-24.04`
- **Actions**: `cloudaper/epics-action@v1`
- **Secrets**: `GITHUB_TOKEN`
- **Upstream Assumptions**: None.
- **Adaptations Needed**: Add `workflow_dispatch: {}` so it can be verified manually.

### 3.3 `issue-filter.yaml` (`Issue Filter`)
- **Triggers**: `issues` (`opened`)
- **Runner**: `ubuntu-24.04`
- **Actions**: `actions/github-script@v9.0.0`
- **Upstream Assumptions**: Checks if the issue author has repo maintainer/admin permissions via `github.rest.repos.getCollaboratorPermissionLevel`. Dynamic and fork-safe.
- **Adaptations Needed**: Add `workflow_dispatch: {}` for manual verification.

### 3.4 `actionlint.yaml` (`Lint Action Workflows`)
- **Triggers**: `pull_request` on `.github/workflows/*`
- **Runner**: `ubuntu-24.04`
- **Actions**: `raven-actions/actionlint@v2`
- **Notes**: Job ID has upstream typo `acitonlint:`.
- **Adaptations Needed**: Add `workflow_dispatch: {}`.

### 3.5 `codeql.yml` (`CodeQL Static Analysis`)
- **Triggers**: `schedule` (`cron: '0 4 * * 1'`), `workflow_dispatch: {}`
- **Runner**: `ubuntu-24.04`
- **Actions**: `github/codeql-action/init@v4`, `github/codeql-action/analyze@v4`
- **Upstream Assumptions**: None. Language matrix is `actions` (Go manual build step is commented out upstream).
- **Status in Fork**: Initially `disabled_fork`; enabled via `gh workflow enable 419931034`.

### 3.6 `govulncheck.yml` (`govulncheck`)
- **Triggers**: `push` on `go.sum`, `schedule`, `workflow_dispatch: {}`
- **Runner**: `ubuntu-24.04`
- **Actions**: `actions/checkout@v7.0.0`, `./.github/actions/setup-go`
- **Upstream Assumptions**: None.
- **Status in Fork**: Initially `disabled_fork`; enabled via `gh workflow enable 419931046`.

### 3.7 `scorecard.yml` (`Scorecard supply-chain security`)
- **Triggers**: `branch_protection_rule`, `schedule`, `push` (`main`)
- **Runner**: `ubuntu-24.04`
- **Actions**: `ossf/scorecard-action@v2.4.3`, `github/codeql-action/upload-sarif@v4`
- **Secrets**: `SCORECARD_TOKEN` (optional fine-grained PAT for branch protection check; upstream comment notes expiration in 2026).
- **Condition**: `if: github.event.repository.default_branch == github.ref_name || github.event_name == 'pull_request'`
- **Status in Fork**: Initially `disabled_fork`; enabled via `gh workflow enable 419931068`.
- **Adaptations Needed**: Add `workflow_dispatch: {}`. For public forks without `SCORECARD_TOKEN`, it runs with default `GITHUB_TOKEN`.

### 3.8 `trivy-trigger.yml` (`Trivy Scan Trigger`)
- **Triggers**: `pull_request` (`types: [labeled]`) with label `scan-with-trivy`
- **Runner**: `ubuntu-24.04`
- **CRITICAL HARDCODING**:
  ```javascript
  const org = 'k3s-io';
  // ...
  const result = await github.rest.orgs.checkMembershipForUser({
    org,
    username: actor,
  });
  ```
- **Architectural Blocker**: In a user fork (`sajuptpm/k3s`), checking membership in `k3s-io` will fail unless the user is an official `k3s-io` member. Furthermore, the token lacks `read:org`.
- **Fix**: Replace `const org = 'k3s-io';` with `const org = context.repo.owner;` and check collaborator write/admin status on `context.repo` rather than requiring org membership if `owner` is a personal account. Add `workflow_dispatch: {}`.

### 3.9 `trivy-scan.yml` (`Trivy Scan Result`)
- **Triggers**: `workflow_run` on `Trivy Scan Trigger` completion
- **Runner**: `ubuntu-24.04`
- **Actions**: `aquasecurity/trivy-action@v0.36.0`
- **Upstream References**:
  - Image reference `rancher/k3s:latest`
  - VEX Hub URL `https://github.com/rancher/vexhub/raw/refs/heads/main/reports/rancher.openvex.json.gz`
- **Adaptations Needed**: Works with image archive loaded from artifact. Add `workflow_dispatch` or ensure trigger chain works seamlessly.

### 3.10 `build-k3s.yaml` (Reusable Build Workflow)
- **Triggers**: `workflow_call` (inputs: `platforms`, `upload-image`, `upload-build`, `test-coverage`)
- **Runner Expression**:
  ```yaml
  runs-on: ${{ (!contains(inputs.platforms, 'amd64') && !contains(inputs.platforms, 'windows/') && !contains(inputs.platforms, 'riscv64') && (github.repository_owner == 'k3s-io' && 'cncf-ubuntu-16-64-arm' || 'ubuntu-24.04-arm')) 
    || (github.repository_owner == 'k3s-io' && 'cncf-ubuntu-16-64-x86' || 'ubuntu-24.04') }}
  ```
- **Finding**: The runner expression already includes an inline ternary fallback to `ubuntu-24.04` and `ubuntu-24.04-arm` when `github.repository_owner != 'k3s-io'`.
- **Consideration**: GitHub-hosted `ubuntu-24.04` has limited disk space (~14 GB free by default). Full K3s compilation with multi-arch or heavy assets can exhaust disk. Disk cleanup steps or platform constraints are essential.

### 3.11 `validate.yaml` (`Validate`)
- **Triggers**: `pull_request`
- **Runner**: `ubuntu-24.04`
- **Upstream Assumptions**:
  - `echo "GITHUB_CHECKOUT_FETCH_DEPTH=$( expr 1 + ${{ github.event.pull_request.commits }} )"` -> fails on `workflow_dispatch` (empty value results in syntax error in `expr 1 + `).
  - `--new-from-merge-base ${{ github.event.pull_request.base.sha }}` -> fails on `workflow_dispatch` because `github.event.pull_request.base.sha` is empty.
- **Fix**: Check if `github.event_name == 'pull_request'`. If not, default fetch-depth to full (`0`) or `1`, and omit `--new-from-merge-base` when not triggered by PR.

### 3.12 `unitcoverage.yaml` (`Unit Test Coverage`)
- **Triggers**: `push`, `pull_request`, `workflow_dispatch: {}`
- **Runners**: `ubuntu-24.04` (Linux, mods), `windows-2022` (Windows)
- **Secrets**: `CODECOV_TOKEN` (optional for public repos on Codecov, but uploading might fail or warn if token is unset).
- **Jobs**: `test-unit-linux`, `test-unit-windows`, `test-mods`.

### 3.13 `airgap.yaml` (`Airgap Image Tarballs`)
- **Triggers**: `pull_request`, `workflow_call: {}`
- **Runner**: `ubuntu-24.04` (matrix: `arch: [amd64, arm64, arm]`)
- **Tools**: Docker containerd snapshotter, `pigz`, `zstd`.
- **Adaptations Needed**: Add `workflow_dispatch: {}` to allow standalone execution and testing.

### 3.14 `integration.yaml` (`Integration Test Coverage`)
- **Triggers**: `push`, `pull_request`, `workflow_dispatch: {}`
- **Jobs**: `build`, `build-windows`, `itest` (matrix of 12 integration suites), `itest-windows`
- **Runners**: `ubuntu-24.04`, `windows-2022`
- **Secrets**: `CODECOV_TOKEN`

### 3.15 `e2e.yaml` (`E2E Test Coverage`)
- **Triggers**: `push`, `pull_request`, `workflow_dispatch: {}`
- **Jobs**:
  - `build`, `build-arm64`
  - `e2e` (Vagrant/libvirt suite: startup, s3, embeddedmirror, privateregistry, wasm, externalip, rootless, multus, btrfs)
  - `docker-go` (matrix of 18 test suites across amd64 and arm64)
  - `docker-large` (scale test)
- **CRITICAL UPSTREAM GATE & RUNNER**:
  ```yaml
  docker-large:
    runs-on: cncf-ubuntu-32-128-x86
    if: github.repository_owner == 'k3s-io'
  ```
- **Alternate Job Strategy**:
  - Feature flag original job: `if: ${{ vars.ENABLE_UPSTREAM_DOCKER_LARGE == 'true' }}`
  - Create fork-equivalent job: `docker-large-fork` running on standard `ubuntu-24.04` when `vars.ENABLE_UPSTREAM_DOCKER_LARGE != 'true'`.

### 3.16 `install.yaml` (`Install Script`)
- **Triggers**: `push`, `pull_request`, `workflow_dispatch: {}`
- **Jobs**: `build`, `docker-go` (selinux), `test` (Vagrant smoke test matrix on centos-9, alma-10, rocky-9, fedora, opensuse-leap, ubuntu-2404).

### 3.17 `nightly-install.yaml` (`Nightly Tests`)
- **Triggers**: `schedule`, `workflow_dispatch: {}`
- **Jobs**: `install-test`, `build`, `conf-test`
- **Runner in Conformance**:
  ```yaml
  runs-on: ${{ github.repository_owner == 'k3s-io' && matrix.suite == 'parallel' && 'cncf-ubuntu-8-32-x86' || 'ubuntu-24.04' }}
  ```
  Falls back cleanly to `ubuntu-24.04` for forks.

### 3.18 `release.yml` (`K3s Release`)
- **Triggers**: `push` on tags `v*`
- **CRITICAL DEPENDENCIES & UPSTREAM ASSUMPTIONS**:
  - Vault reader (`rancher-eio/read-vault-secrets@v3`) across 6 steps:
    - Staging registry credentials
    - Prime registry credentials
    - DockerHub Rancher credentials
    - Prime artifacts S3 uploader credentials
  - Hardcoded repository check: `github.repository_owner == 'k3s-io'`
  - DockerHub org: `DOCKERHUB_ORG=rancher`
  - AWS S3 bucket: `PRIME_ARTIFACTS_BUCKET_NAME`
  - Downstream dispatch: `https://api.github.com/repos/${{ github.repository_owner }}/k3s-upgrade/dispatches` with `secrets.K3S_UPGRADE_PAT`
- **Fork Alternate Strategy**:
  - Provide `workflow_dispatch` trigger with input parameters (`tag`, `dry_run`).
  - Flag upstream S3 upload, Prime registry, and `k3s-upgrade` dispatch behind `vars.ENABLE_UPSTREAM_RELEASE == 'true'`.
  - In fork mode (`vars.ENABLE_UPSTREAM_RELEASE != 'true'`), publish multi-arch images exclusively to GitHub Container Registry (`ghcr.io/${{ github.repository_owner }}/k3s`), generate GitHub Release assets with checksums directly on the fork, and gracefully bypass proprietary Vault and S3 dependencies.

### 3.19 `updatecli.yaml` (`Updatecli: Dependency Management`)
- **Triggers**: `schedule`, `workflow_dispatch`
- **Jobs**: `cleanup-branches`, `updatecli`
- **Condition**: `if: github.ref == 'refs/heads/main'`
- **Target Matrix**: `main`, `release-1.37`, `release-1.36`, `release-1.35`, `release-1.34`
- **Status in Fork**: Initially `disabled_fork`; enabled via `gh workflow enable 419931097`.
- **Adaptation Needed**: In fork on feature branches, remove or relax the `github.ref == 'refs/heads/main'` guard when manually triggered via `workflow_dispatch`.

### 3.20 `updatecli_k8s.yaml` (`Updatecli: k3s-io/kubernetes Dependency and Go Bumps`)
- **Triggers**: `workflow_dispatch`
- **Jobs**: `updatecli`
- **Condition**: `if: github.ref == 'refs/heads/main'`
- **Target Matrix**: Same branch list as `updatecli.yaml`.
- **Adaptation Needed**: Allow execution when triggered from non-main branches (e.g. `github.ref == 'refs/heads/main' || github.event_name == 'workflow_dispatch'`).

---

## 4. Key Architectural Discoveries

1. **Windows CRLF Line Endings**: All workflow files in the workspace use Windows `CRLF` (`\r\n`). In-place text replacements and string matching must account for CRLF or preserve original line endings to prevent mangling YAML indentation.
2. **Reusable Workflow Hierarchy**: `build-k3s.yaml` is the root dependency for:
   - `release.yml`
   - `e2e.yaml`
   - `integration.yaml`
   - `install.yaml`
   - `nightly-install.yaml`
   Any change to `build-k3s.yaml` directly affects 5 downstream test and release pipelines.
3. **Runner Architecture**:
   - Upstream K3s utilizes CNCF-sponsored bare-metal runners (`cncf-ubuntu-16-64-x86`, `cncf-ubuntu-16-64-arm`, `cncf-ubuntu-32-128-x86`, `cncf-ubuntu-8-32-x86`).
   - The expressions in `build-k3s.yaml` and `nightly-install.yaml` already contain ternary fallbacks to standard GitHub-hosted runners (`ubuntu-24.04`, `ubuntu-24.04-arm`).
   - `e2e.yaml` has `docker-large` strictly hardcoded to `cncf-ubuntu-32-128-x86` with `if: github.repository_owner == 'k3s-io'`. An alternate job `docker-large-fork` running on standard runners is required.
4. **Secret Boundaries & Vault Replacement**:
   - `release.yml` uses Vault secrets for DockerHub, AWS S3, and internal SUSE registries. For forks, standard GitHub Actions repository secrets (`DOCKER_USERNAME`, `DOCKER_TOKEN`, `GITHUB_TOKEN`) and GitHub Releases/GHCR provide 100% equivalent release artifacts without proprietary infrastructure.

---

## 5. Next Steps for Implementation

1. Finalize and push patches for Tier 1 & Tier 2 workflows (`epic.yaml`, `issue-filter.yaml`, `actionlint.yaml`, `scorecard.yml`, `trivy-trigger.yml`, `trivy-scan.yml`).
2. Run validation and dispatch tests sequentially.
3. Apply Tier 3 adaptations (`validate.yaml`, `build-k3s.yaml`, `unitcoverage.yaml`).
4. Generate `.diff` and per-workflow `.md` documentation inside `workflow-fix/`.
