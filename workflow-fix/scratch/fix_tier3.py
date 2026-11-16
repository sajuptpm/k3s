#!/usr/bin/env python3
"""Fix validate.yaml lint args and build-k3s.yaml runner selection."""
import os

os.chdir(os.path.join(os.path.dirname(__file__), '..', '..'))

def read_file(path):
    with open(path, 'r', newline='') as f:
        return f.read()

def write_file(path, data):
    with open(path, 'w', newline='') as f:
        f.write(data)

# === validate.yaml: fix lint args for non-PR dispatch ===
data = read_file('.github/workflows/validate.yaml')
# Both golangci-lint steps reference pull_request.base.sha which is empty on dispatch
# Replace args with conditional
old_args1 = '          args: "--new-from-merge-base ${{ github.event.pull_request.base.sha }}"'
new_args1 = '          args: "${{ github.event_name == \'pull_request\' && format(\'--new-from-merge-base {0}\', github.event.pull_request.base.sha) || \'\' }}"'
data = data.replace(old_args1, new_args1)

old_args2 = '          args: "--new-from-merge-base ${{ github.event.pull_request.base.sha }} ./pkg/... ./cmd/..."'
new_args2 = '          args: "${{ github.event_name == \'pull_request\' && format(\'--new-from-merge-base {0} ./pkg/... ./cmd/...\', github.event.pull_request.base.sha) || \'./pkg/... ./cmd/...\' }}"'
data = data.replace(old_args2, new_args2)

write_file('.github/workflows/validate.yaml', data)
print("Fixed validate.yaml lint args for dispatch context")

# === build-k3s.yaml: runner already handles forks correctly ===
# The existing expression already falls back to 'ubuntu-24.04' / 'ubuntu-24.04-arm' for non-k3s-io
# Let's verify:
data = read_file('.github/workflows/build-k3s.yaml')
if "github.repository_owner == 'k3s-io' && 'cncf-ubuntu-16-64-x86' || 'ubuntu-24.04'" in data:
    print("build-k3s.yaml: Runner selection already correctly falls back to ubuntu-24.04 for forks")
else:
    print("WARNING: build-k3s.yaml runner expression needs investigation")

# === e2e.yaml: docker-large job is gated on k3s-io, needs fork alternate ===
data = read_file('.github/workflows/e2e.yaml')
le = '\r\n' if '\r\n' in data else '\n'

# The docker-large job needs a fork-equivalent alternate
# The original is gated with: if: github.repository_owner == 'k3s-io'
# We'll change it to use a variable flag and add a fork-equivalent
old_docker_large_if = "    if: github.repository_owner == 'k3s-io'"
new_docker_large_if = "    if: ${{ vars.ENABLE_UPSTREAM_DOCKER_LARGE == 'true' }}"
data = data.replace(old_docker_large_if, new_docker_large_if)
write_file('.github/workflows/e2e.yaml', data)
print("Fixed e2e.yaml docker-large job gating")

# Add fork-equivalent docker-large job at the end
fork_job = f'''
  docker-large-fork:
    needs: build
    name: Docker Large (Fork)
    timeout-minutes: 45
    runs-on: ubuntu-24.04
    if: ${{{{ vars.ENABLE_UPSTREAM_DOCKER_LARGE != 'true' }}}}
    steps:
    - name: Remove Unnecessary Tools
      working-directory: /
      run: |
        sudo rm -rf \\
          /home/linuxbrew \\
          /home/packer \\
          /opt/az \\
          /opt/microsoft \\
          /usr/lib/firefox \\
          /usr/lib/google-cloud-sdk \\
          /usr/local/julia* \\
          /usr/local/share/boost \\
          /usr/local/share/chromium \\
          /usr/local/share/powershell \\
          /usr/share/az* \\
          /usr/share/dotnet \\
          /usr/share/miniconda \\
          /usr/share/swift
        df -khl
    - name: Checkout
      uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7.0.0
    - name: Install Go
      uses: ./.github/actions/setup-go
    - name: Set up Docker
      uses: docker/setup-docker-action@77e84dbf09b47d1e29270283c22f16145aa85ca1 # v5.4.0
      with:
        version: type=image,tag=29
        set-host: true
    - name: "Download K3s image"
      uses: actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c # v8
      with:
        name: k3s-amd64
        path: ./dist/artifacts
    - name: Load and set K3s image
      run: |
        chmod +x ./dist/artifacts/k3s
        docker image load -i ./dist/artifacts/k3s-image.tar
        IMAGE_TAG=$(docker image ls --format '{{{{.Repository}}}}:{{{{.Tag}}}}' | grep 'rancher/k3s')
        echo "K3S_IMAGE=$IMAGE_TAG" >> $GITHUB_ENV
    - name: Run scale test
      run: |
        go install github.com/onsi/ginkgo/v2/ginkgo@$(. ./scripts/version.sh; get-module-version github.com/onsi/ginkgo/v2)
        ginkgo run -v -timeout=40m ./tests/docker/scale/ -- -ci -k3sImage=$K3S_IMAGE
'''

data = read_file('.github/workflows/e2e.yaml')
data = data.rstrip() + le + fork_job
write_file('.github/workflows/e2e.yaml', data)
print("Added docker-large-fork job to e2e.yaml")

# === nightly-install.yaml: runner already handles forks correctly ===
data = read_file('.github/workflows/nightly-install.yaml')
if "github.repository_owner == 'k3s-io' && matrix.suite == 'parallel' && 'cncf-ubuntu-8-32-x86' || 'ubuntu-24.04'" in data:
    print("nightly-install.yaml: Runner already correctly falls back to ubuntu-24.04 for forks")

print("\nTier 3 patches complete!")
