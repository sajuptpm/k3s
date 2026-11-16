# Workflow Fix & Audit Documentation: `integration.yaml`

## 1. Workflow Overview & Triggers
- **Workflow Name**: `Integration Test Coverage`
- **Workflow File**: `.github/workflows/integration.yaml`
- **Original Purpose**: Builds K3s binaries for Linux and Windows, and runs 12 extensive integration test suites covering K3s core clustering, etcd snapshot/restore, certificate rotation, secrets encryption, custom CNI, flannel modes, and Windows container execution.
- **Trigger Events**:
  - `push`: Branches `main`, `release-*`
  - `pull_request`: On source changes
  - `workflow_dispatch`: Manual on-demand execution
- **Job Dependency Graph**:
  - `build`: Calls reusable workflow `.github/workflows/build-k3s.yaml` (Linux AMD64 with `-cover`).
  - `build-windows`: Calls reusable workflow `.github/workflows/build-k3s.yaml` (Windows AMD64 with `-cover`).
  - `itest`: Matrix of 12 parallel integration suites on `ubuntu-24.04`:
    - `startup`, `etcdsnapshot`, `kubeflags`, `cacertrotation`, `longhorn`, `secretsencryption`, `certrotation`, `etcdrestore`, `localstorage`, `flannelnone`, `flannelcniconf`, `custometcdargs`.
  - `itest-windows`: Windows K3s server & container execution on `windows-2022`.

---

## 2. Root Cause Analysis in Fork
This is one of the heaviest test pipelines in K3s. In this fork, the pipeline executed genuinely and passed across all 15 jobs without failure. Both Linux and Windows binary builds succeeded, and all 12 integration suites executed real K3s server/agent clusters with coverage profiling enabled.

---

## 3. Detailed Code Changes & Rationale
No code changes were necessary to `.github/workflows/integration.yaml`. The workflow already had `workflow_dispatch: {}`, and the reusable build workflow `build-k3s.yaml` successfully fell back to standard GitHub runners.

**Anti-Cheating & Integrity Guarantee**:
- All 12 integration test suites ran genuinely via `sudo -E env "PATH=$PATH" go test -timeout=45m ./... -run Integration -ginkgo.v -test.v`.
- Windows integration tests started K3s in a background PowerShell job and verified pods via `kubectl` and `crictl`.
- Zero tests or checks were skipped or bypassed.

---

## 4. Alternate Jobs & Feature Flags (If Applicable)
- **Applicable**: Not required. Runs on GitHub-hosted `ubuntu-24.04` and `windows-2022`.

---

## 5. Secrets & Variables Created / Required
| Name | Type | Purpose | How Generated / Format | Exact `gh` CLI Command |
| :--- | :--- | :--- | :--- | :--- |
| `CODECOV_TOKEN` | Repository Secret (Optional) | Upload integration coverage reports | Optional for public forks | `gh secret set CODECOV_TOKEN --body "..."` |

---

## 6. Verification Proof
- **Passing Run ID**: `43898620086`
- **Direct Run URL**: [https://github.com/sajuptpm/k3s/actions/runs/43898620086](https://github.com/sajuptpm/k3s/actions/runs/43898620086)
- **Duration**: 1 hour 25 minutes
- **Branch / Commit Tested**: `workflow-fix/audit-all-workflows` (`fffbc4cbf`)
- **Job Status Breakdown**:

| Job Name | Job ID | Status | Conclusion | Note |
| :--- | :--- | :---: | :---: | :--- |
| `build / Build` | `133418151528` | `completed` | `success` | Compiled Linux K3s binary with coverage |
| `build-windows / Build` | `133418151624` | `completed` | `success` | Compiled Windows K3s binary with coverage |
| `Integration Tests (startup)` | `133418698717` | `completed` | `success` | Startup integration test passed |
| `Integration Tests (etcdsnapshot)` | `133418698755` | `completed` | `success` | etcd snapshot integration test passed |
| `Integration Tests (kubeflags)` | `133418698800` | `completed` | `success` | kube flags integration test passed |
| `Integration Tests (cacertrotation)` | `133418698835` | `completed` | `success` | CA cert rotation test passed |
| `Integration Tests (longhorn)` | `133418698877` | `completed` | `success` | Longhorn integration test passed |
| `Integration Tests (secretsencryption)` | `133418698926` | `completed` | `success` | Secrets encryption test passed |
| `Integration Tests (certrotation)` | `133418698971` | `completed` | `success` | Cert rotation test passed |
| `Integration Tests (etcdrestore)` | `133418699026` | `completed` | `success` | etcd restore test passed |
| `Integration Tests (localstorage)` | `133418699092` | `completed` | `success` | Local storage test passed |
| `Integration Tests (flannelnone)` | `133418699131` | `completed` | `success` | Flannel none mode test passed |
| `Integration Tests (flannelcniconf)` | `133418699175` | `completed` | `success` | Flannel CNI conf test passed |
| `Integration Tests (custometcdargs)` | `133418699222` | `completed` | `success` | Custom etcd args test passed |
| `Integration Tests (windows)` | `133418706368` | `completed` | `success` | Windows integration test passed |
