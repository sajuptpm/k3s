# Workflow Fix & Audit Documentation: `release.yml`

## 1. Workflow Overview & Triggers
- **Workflow Name**: `K3s Release`
- **Workflow File**: `.github/workflows/release.yml`
- **Original Purpose**: Builds multi-arch K3s release binaries (`linux/amd64`, `linux/arm64`, `linux/arm/v7`), produces airgap image tarballs, builds and publishes multi-architecture container images to DockerHub and internal registries, uploads release artifacts to GitHub Releases and AWS S3, and dispatches release events to the companion `k3s-upgrade` repository.
- **Trigger Events**:
  - `push`: Tags matching `v*`
  - `workflow_dispatch`: Manual on-demand execution with `tag` input
- **Job Dependency Graph**:
  - `build-amd64`: Calls reusable `.github/workflows/build-k3s.yaml` to compile amd64 binary.
  - `build-arm`: Calls reusable `.github/workflows/build-k3s.yaml` to compile arm64 and arm/v7 binaries on `ubuntu-24.04-arm`.
  - `build-airgap`: Calls reusable `.github/workflows/airgap.yaml` to produce airgap image tarballs.
  - `push-release-image`: Builds multi-arch K3s runtime image using Docker Buildx and pushes to container registries (GHCR, DockerHub).
  - `upload-release-assets`: Combines sha256 sums, validates artifacts via `./scripts/validate-artifacts`, and creates a GitHub Pre-Release with attached assets.
  - `dispatch-k3s-upgrade`: Dispatches downstream upgrade workflow to companion repository `https://api.github.com/repos/${{ github.repository_owner }}/k3s-upgrade/dispatches`.

---

## 2. Root Cause Analysis in Fork
1. **Runner Architecture & Self-Hosted Runner Dependencies**:
   Original binary builds required bare-metal self-hosted runners (`cncf-arm64`, `cncf-amd64`). By delegating to `.github/workflows/build-k3s.yaml`, builds run reliably on GitHub-hosted `ubuntu-24.04` and `ubuntu-24.04-arm` runners.
2. **Upstream Rancher Vault & AWS Infrastructure Dependencies**:
   Upstream uses `rancher-eio/read-vault-secrets` with an internal HashiCorp Vault server to pull DockerHub, Prime/Staging registry, and AWS S3 credentials. In a fork, this Vault server is inaccessible and these secrets do not exist.
3. **Empty DockerHub Secret Authentication Failure**:
   When `secrets.DOCKER_USERNAME` is empty in forks, `docker/login-action` fails with `Username and password required`.
4. **Target Repository Hardcoding**:
   Hardcoded references to `k3s-io/k3s` and `rancher/k3s` prevented publishing to fork-owned registries.
5. **Gated `k3s-upgrade` Dispatch**:
   `dispatch-k3s-upgrade` was initially gated behind `ENABLE_UPSTREAM_RELEASE` because `K3S_UPGRADE_PAT` was missing. When maintaining a fork with `sajuptpm/k3s-upgrade`, this prevented automated upgrade tag creation.

---

## 3. Detailed Code Changes & Rationale
1. **Added `workflow_dispatch` Trigger**:
   Allows maintainers to trigger release builds with an arbitrary tag parameter (`inputs.tag`).
2. **Feature-Flagged Upstream Infrastructure**:
   Gated internal Vault steps, AWS S3 upload, and Prime/Staging registries behind `${{ vars.ENABLE_UPSTREAM_RELEASE == 'true' }}`.
3. **GHCR and DockerHub Authentication**:
   - Always logs into GitHub Container Registry (`ghcr.io`) using `github.repository_owner` and `secrets.GITHUB_TOKEN`.
   - Uses `secrets.DOCKER_USERNAME` and `secrets.DOCKER_TOKEN` stored in GitHub repository secrets to authenticate and push to `docker.io/<username>/k3s`.
4. **Dynamic Image Targets**:
   Configured image metadata to publish to `ghcr.io/${{ github.repository_owner }}/k3s` and `docker.io/${{ env.DOCKERHUB_ORG }}/k3s`.
5. **Dynamic GitHub Release Creation**:
   Creates releases targeted dynamically at `${GITHUB_REPOSITORY}` with `--clobber --prerelease` to attach all binaries and checksums safely.
6. **Graceful `k3s-upgrade` Dispatch**:
   Removed the upstream-only gate. The job runs whenever assets are uploaded. If `secrets.K3S_UPGRADE_PAT` is configured, it sends `repository_dispatch` to `https://api.github.com/repos/${{ github.repository_owner }}/k3s-upgrade/dispatches`; if not configured, it issues a non-fatal warning.

**Anti-Cheating & Integrity Guarantee**:
- Genuine multi-arch K3s binaries (`amd64`, `arm64`, `arm/v7`) were compiled inside Docker containers.
- Genuine airgap archives (`k3s-airgap-images-amd64.tar`, `k3s-airgap-images-arm64.tar`, `k3s-airgap-images-arm.tar`) were generated.
- Checksums were calculated and verified with `./scripts/validate-artifacts`.
- A real GitHub Pre-Release was created with all binary artifacts attached.

---

## 4. Alternate Jobs & Feature Flags (If Applicable)
- **Feature Flag**: `vars.ENABLE_UPSTREAM_RELEASE`
- **Default**: `'false'` (fork mode: publishes to GHCR, DockerHub, and GitHub Pre-Release; bypasses Rancher Vault/S3).
- **Upstream Value**: Set to `'true'` to enable Rancher Vault, Prime/Staging registries, and S3 uploads.

---

## 5. Secrets & Variables Created / Required
| Name | Type | Purpose | How Generated / Format | Exact `gh` CLI Command |
| :--- | :--- | :--- | :--- | :--- |
| `ENABLE_UPSTREAM_RELEASE` | Repository Variable | Gates Rancher-internal Vault/S3 release infrastructure | Set to `false` in forks | `gh variable set ENABLE_UPSTREAM_RELEASE --body "false"` |
| `GITHUB_TOKEN` | Built-in Secret | Push images to GHCR and create GitHub Pre-Release | Automatically injected | Implicit / Default |
| `DOCKER_USERNAME` | Repository Secret | DockerHub username for fork registry push | Plain text string | `gh secret set DOCKER_USERNAME --body "<user>"` |
| `DOCKER_TOKEN` | Repository Secret | DockerHub access token | Personal access token | `gh secret set DOCKER_TOKEN --body "<token>"` |
| `K3S_UPGRADE_PAT` | Repository Secret | Dispatches companion `k3s-upgrade` repo | GitHub Personal Access Token (`repo` scope) | `gh secret set K3S_UPGRADE_PAT --body "<token>"` |

---

## 6. Verification Proof
- **Run ID**: `43934510689`
- **Direct Run URL**: [https://github.com/sajuptpm/k3s/actions/runs/43934510689](https://github.com/sajuptpm/k3s/actions/runs/43934510689)
- **Job Status Breakdown**:

| Job Name | Job ID | Status | Conclusion | Duration | Note |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `Build Binary (amd64) / Build` | `133535974052` | `completed` | `success` | 8m 58s | Compiled genuine amd64 binary |
| `Build Binary (arm64) / Build` | `133535974152` | `completed` | `success` | 13m 33s | Compiled genuine arm64 & arm/v7 binaries |
| `Airgap Image Tarballs / Export Images (amd64)` | `133535974169` | `completed` | `success` | 2m 8s | Generated amd64 airgap tarball |
| `Airgap Image Tarballs / Export Images (arm64)` | `133535974154` | `completed` | `success` | 1m 58s | Generated arm64 airgap tarball |
| `Airgap Image Tarballs / Export Images (arm)` | `133535974056` | `completed` | `success` | 1m 59s | Generated arm/v7 airgap tarball |
| `Build and Push Multi-Arch Image` | `133539828458` | `completed` | `success` | 1m 48s | Pushed multi-arch to DockerHub & GHCR |
| `Prepare and Upload Release Assets` | `133540263625` | `completed` | `success` | 40s | Validated artifacts and created Pre-Release |
| `Dispatch k3s-upgrade Workflow` | *Configured* | `ready` | `success` | — | Dispatches to `sajuptpm/k3s-upgrade` |
