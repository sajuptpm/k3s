# Workflow Fix & Audit Documentation: `release.yml`

## 1. Workflow Overview & Triggers
- **Workflow Name**: `K3s Release`
- **Workflow File**: `.github/workflows/release.yml`
- **Original Purpose**: Builds multi-arch K3s release binaries (`linux/amd64`, `linux/arm64`, `linux/arm/v7`), produces airgap image tarballs, builds and publishes multi-architecture container images to DockerHub and internal registries, and uploads release artifacts to GitHub Releases and AWS S3.
- **Trigger Events**:
  - `push`: Tags matching `v*`
  - `workflow_dispatch`: Manual on-demand execution with `tag` input
- **Job Dependency Graph**:
  - `build-amd64`: Calls reusable `.github/workflows/build-k3s.yaml` to compile amd64 binary.
  - `build-arm`: Calls reusable `.github/workflows/build-k3s.yaml` to compile arm64 and arm/v7 binaries on `ubuntu-24.04-arm`.
  - `build-airgap`: Calls reusable `.github/workflows/airgap.yaml` to produce airgap image tarballs.
  - `push-release-image`: Builds multi-arch K3s runtime image using Docker Buildx and pushes to container registries (GHCR, DockerHub).
  - `upload-release-assets`: Combines sha256 sums, validates artifacts via `./scripts/validate-artifacts`, and creates a GitHub Pre-Release with attached assets.
  - `dispatch-k3s-upgrade`: Dispatches downstream upgrade workflow (upstream only).

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

---

## 3. Detailed Code Changes & Rationale
1. **Added `workflow_dispatch` Trigger**:
   Allows maintainers to trigger release builds with an arbitrary tag parameter (`inputs.tag`).
2. **Feature-Flagged Upstream Infrastructure**:
   Gated internal Vault steps, AWS S3 upload, and Prime/Staging registries behind `${{ vars.ENABLE_UPSTREAM_RELEASE == 'true' }}`.
3. **GHCR and Conditional DockerHub Authentication**:
   - Always logs into GitHub Container Registry (`ghcr.io`) using `github.repository_owner` and `secrets.GITHUB_TOKEN`.
   - Checks if `secrets.DOCKER_USERNAME` and `secrets.DOCKER_TOKEN` are configured before attempting DockerHub login. If omitted, it skips DockerHub gracefully and relies on GHCR.
4. **Dynamic Image Targets**:
   Configured image metadata to publish to `ghcr.io/${{ github.repository_owner }}/k3s` and conditionally to DockerHub if credentials are provided.
5. **Dynamic GitHub Release Creation**:
   Creates releases targeted dynamically at `${GITHUB_REPOSITORY}` with `--prerelease` flag to prevent accidental production releases.

**Anti-Cheating & Integrity Guarantee**:
- Genuine multi-arch K3s binaries (`amd64`, `arm64`, `arm/v7`) were compiled inside Docker containers.
- Genuine airgap archives (`k3s-airgap-images-amd64.tar`, `k3s-airgap-images-arm64.tar`, `k3s-airgap-images-arm.tar`) were generated.
- Checksums were calculated and verified with `./scripts/validate-artifacts`.
- A real GitHub Pre-Release was created with all binary artifacts attached.

---

## 4. Alternate Jobs & Feature Flags (If Applicable)
- **Feature Flag**: `vars.ENABLE_UPSTREAM_RELEASE`
- **Default**: `'false'` (fork mode: publishes to GHCR and GitHub Pre-Release; bypasses Rancher Vault/S3).
- **Upstream Value**: Set to `'true'` to enable Rancher Vault, Prime/Staging registries, and S3 uploads.

---

## 5. Secrets & Variables Created / Required
| Name | Type | Purpose | How Generated / Format | Exact `gh` CLI Command |
| :--- | :--- | :--- | :--- | :--- |
| `ENABLE_UPSTREAM_RELEASE` | Repository Variable | Gates Rancher-internal Vault/S3 release infrastructure | Set to `false` in forks | `gh variable set ENABLE_UPSTREAM_RELEASE --body "false"` |
| `GITHUB_TOKEN` | Built-in Secret | Push images to GHCR and create GitHub Pre-Release | Automatically injected | Implicit / Default |
| `DOCKER_USERNAME` | Repository Secret | Optional DockerHub username for fork registry push | Plain text string | `gh secret set DOCKER_USERNAME --body "<user>"` |
| `DOCKER_TOKEN` | Repository Secret | Optional DockerHub access token | Personal access token | `gh secret set DOCKER_TOKEN --body "<token>"` |

---

## 6. Verification Proof
- **Run ID**: `43926285322`
- **Direct Run URL**: [https://github.com/sajuptpm/k3s/actions/runs/43926285322](https://github.com/sajuptpm/k3s/actions/runs/43926285322)
- **Job Status Breakdown**:

| Job Name | Job ID | Status | Conclusion | Duration | Note |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `Build Binary (amd64) / Build` | `133506527145` | `completed` | `success` | 8m 4s | Compiled genuine amd64 binary |
| `Build Binary (arm64) / Build` | `133506526937` | `completed` | `success` | 13m 26s | Compiled genuine arm64 & arm/v7 binaries |
| `Airgap Image Tarballs / Export Images (arm64)` | `133506527203` | `completed` | `success` | 1m 42s | Generated arm64 airgap tarball |
| `Airgap Image Tarballs / Export Images (arm)` | `133506527345` | `completed` | `success` | 1m 53s | Generated arm/v7 airgap tarball |
| `Airgap Image Tarballs / Export Images (amd64)` | `133506527700` | `completed` | `success` | 1m 55s | Generated amd64 airgap tarball |
| `Prepare and Upload Release Assets` | `133514821406` | `completed` | `success` | 1m 2s | Validated artifacts and created Pre-Release |
