#!/usr/bin/env python3
"""Apply remaining workflow patches (Tier 3-5)."""
import os, sys

os.chdir(r'e:\projects\k3s')

def read_file(path):
    with open(path, 'r', encoding='utf-8', newline='') as f:
        return f.read()

def write_file(path, data):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(data)

def patch(filepath, old, new, label=""):
    data = read_file(filepath)
    # Try LF first, then CRLF
    if old in data:
        data = data.replace(old, new)
    else:
        old_crlf = old.replace('\n', '\r\n')
        new_crlf = new.replace('\n', '\r\n')
        if old_crlf in data:
            data = data.replace(old_crlf, new_crlf)
        else:
            print(f"  FAILED: {label} in {filepath}")
            return False
    write_file(filepath, data)
    print(f"  OK: {label} in {filepath}")
    return True

# ============================================================
# 1. airgap.yaml - add workflow_dispatch
# ============================================================
print("=== airgap.yaml ===")
patch('.github/workflows/airgap.yaml',
    '  workflow_call: {}\n',
    '  workflow_call: {}\n  workflow_dispatch: {}\n',
    'Add workflow_dispatch')

# ============================================================
# 2. release.yml - comprehensive fork adaptation
# ============================================================
print("=== release.yml ===")
data = read_file('.github/workflows/release.yml')
le = '\r\n' if '\r\n' in data else '\n'

# 2a. Add workflow_dispatch trigger
old_trigger = f'on:{le}  push:{le}    tags:{le}    - "v*"'
new_trigger = f'on:{le}  push:{le}    tags:{le}    - "v*"{le}  workflow_dispatch:{le}    inputs:{le}      tag:{le}        description: "Release tag (e.g. v1.32.4+k3s1). Required for manual dispatch."{le}        required: true{le}        type: string'
data = data.replace(old_trigger, new_trigger)
print("  OK: Added workflow_dispatch to release.yml")

# 2b. Feature-flag Vault secrets steps (staging, prime, dockerhub-vault, aws)
# Gate all rancher-eio/read-vault-secrets steps behind ENABLE_UPSTREAM_RELEASE
vault_steps = [
    ("Read registry secrets (staging)", "51"),
    ("Read registry secrets (prime)", "60"),
    ("Read Vault secrets", "68"),
    ("Read Prime artifacts secrets", "192"),
    ("Read registry secrets (staging)", "201"),  # second occurrence in upload-release-assets
    ("Read registry secrets (prime)", "208"),
]
# Replace all vault step conditions from 'k3s-io' check to variable flag
data = data.replace(
    f"      if: ${{{{ github.repository_owner == 'k3s-io' }}}}{le}      with:{le}        secrets: |{le}            secret/data/github/repo/${{{{ github.repository }}}}/k3s-suse-registry-stg",
    f"      if: ${{{{ vars.ENABLE_UPSTREAM_RELEASE == 'true' }}}}{le}      with:{le}        secrets: |{le}            secret/data/github/repo/${{{{ github.repository }}}}/k3s-suse-registry-stg"
)
data = data.replace(
    f"      if: ${{{{ !contains(github.ref_name, '-rc') && github.repository_owner == 'k3s-io' }}}}{le}      with:{le}        secrets: |{le}            secret/data/github/repo/${{{{ github.repository }}}}/k3s-suse-registry/",
    f"      if: ${{{{ vars.ENABLE_UPSTREAM_RELEASE == 'true' && !contains(github.ref_name, '-rc') }}}}{le}      with:{le}        secrets: |{le}            secret/data/github/repo/${{{{ github.repository }}}}/k3s-suse-registry/"
)

# Gate DockerHub Vault login on ENABLE_UPSTREAM_RELEASE
data = data.replace(
    f"      if: github.repository_owner == 'k3s-io'{le}      uses: rancher-eio/read-vault-secrets",
    f"      if: ${{{{ vars.ENABLE_UPSTREAM_RELEASE == 'true' }}}}{le}      uses: rancher-eio/read-vault-secrets"
)
data = data.replace(
    f"      if: github.repository_owner == 'k3s-io'{le}      uses: docker/login-action",
    f"      if: ${{{{ vars.ENABLE_UPSTREAM_RELEASE == 'true' }}}}{le}      uses: docker/login-action"
)

# The fork DockerHub login - gate it on having the secrets
data = data.replace(
    f"      if: github.repository_owner != 'k3s-io'{le}      uses: docker/login-action",
    f"      if: ${{{{ vars.ENABLE_UPSTREAM_RELEASE != 'true' && secrets.DOCKER_USERNAME != '' }}}}{le}      uses: docker/login-action"
)

# Staging/Prime registry logins
data = data.replace(
    f"    - name: Login to Staging Registry{le}      if: github.repository_owner == 'k3s-io'",
    f"    - name: Login to Staging Registry{le}      if: ${{{{ vars.ENABLE_UPSTREAM_RELEASE == 'true' }}}}"
)
data = data.replace(
    f"    - name: Login to Prime Registry{le}      if: ${{{{ !contains(github.ref_name, '-rc') && github.repository_owner == 'k3s-io' }}}}",
    f"    - name: Login to Prime Registry{le}      if: ${{{{ vars.ENABLE_UPSTREAM_RELEASE == 'true' && !contains(github.ref_name, '-rc') }}}}"
)

# Set DockerHub Org - use github.repository_owner for forks
data = data.replace(
    f'    if [ "${{{{ github.repository_owner }}}}" == "k3s-io" ]; then{le}            echo "DOCKERHUB_ORG=rancher" >> $GITHUB_ENV{le}          else{le}            echo "DOCKERHUB_ORG=${{{{ secrets.DOCKER_USERNAME }}}}" >> $GITHUB_ENV',
    f'    if [ "${{{{ github.repository_owner }}}}" == "k3s-io" ]; then{le}            echo "DOCKERHUB_ORG=rancher" >> $GITHUB_ENV{le}          elif [ -n "${{{{ secrets.DOCKER_USERNAME }}}}" ]; then{le}            echo "DOCKERHUB_ORG=${{{{ secrets.DOCKER_USERNAME }}}}" >> $GITHUB_ENV{le}          else{le}            echo "DOCKERHUB_ORG=${{{{ github.repository_owner }}}}" >> $GITHUB_ENV'
)

# Staging/Prime registry image metadata - gate on ENABLE_UPSTREAM_RELEASE
data = data.replace(
    f"name=${{{{ env.REGISTRY }}}}/rancher/k3s,enable=${{{{ !contains(github.ref_name, '-rc') && github.repository_owner == 'k3s-io' }}}}",
    f"name=${{{{ env.REGISTRY }}}}/rancher/k3s,enable=${{{{ vars.ENABLE_UPSTREAM_RELEASE == 'true' && !contains(github.ref_name, '-rc') }}}}"
)
data = data.replace(
    f"name=${{{{ env.STAGING_REGISTRY }}}}/rancher/k3s,enable=${{{{ github.repository_owner == 'k3s-io' }}}}",
    f"name=${{{{ env.STAGING_REGISTRY }}}}/rancher/k3s,enable=${{{{ vars.ENABLE_UPSTREAM_RELEASE == 'true' }}}}"
)

# AWS credentials & S3 upload - gate on ENABLE_UPSTREAM_RELEASE
data = data.replace(
    f"      if: ${{{{ github.repository_owner == 'k3s-io' }}}}{le}      with:{le}        secrets: |{le}            secret/data/github/repo/${{{{ github.repository }}}}/prime-artifacts-uploader",
    f"      if: ${{{{ vars.ENABLE_UPSTREAM_RELEASE == 'true' }}}}{le}      with:{le}        secrets: |{le}            secret/data/github/repo/${{{{ github.repository }}}}/prime-artifacts-uploader"
)
data = data.replace(
    f"    - name: Configure AWS Credentials (s3){le}      uses: aws-actions/configure-aws-credentials@ec61189d14ec14c8efccab744f656cffd0e33f37 # v6{le}      if: ${{{{ github.repository_owner == 'k3s-io' }}}}",
    f"    - name: Configure AWS Credentials (s3){le}      uses: aws-actions/configure-aws-credentials@ec61189d14ec14c8efccab744f656cffd0e33f37 # v6{le}      if: ${{{{ vars.ENABLE_UPSTREAM_RELEASE == 'true' }}}}"
)
data = data.replace(
    f"    - name: Update Image Registry for Prime/Staging{le}      if: ${{{{ github.repository_owner == 'k3s-io' }}}}",
    f"    - name: Update Image Registry for Prime/Staging{le}      if: ${{{{ vars.ENABLE_UPSTREAM_RELEASE == 'true' }}}}"
)
data = data.replace(
    f"    - name: Upload Assets to S3{le}      if: ${{{{ github.repository_owner == 'k3s-io' }}}}",
    f"    - name: Upload Assets to S3{le}      if: ${{{{ vars.ENABLE_UPSTREAM_RELEASE == 'true' }}}}"
)

# k3s-upgrade dispatch - feature flag
data = data.replace(
    f"  dispatch-k3s-upgrade:{le}    name: Dispatch k3s-upgrade Workflow{le}    runs-on: ubuntu-24.04{le}    needs: [upload-release-assets]",
    f"  dispatch-k3s-upgrade:{le}    name: Dispatch k3s-upgrade Workflow{le}    runs-on: ubuntu-24.04{le}    if: ${{{{ vars.ENABLE_UPSTREAM_RELEASE == 'true' }}}}{le}    needs: [upload-release-assets]"
)

write_file('.github/workflows/release.yml', data)
print("  OK: All release.yml fork adaptations applied")

# ============================================================
# 3. updatecli.yaml - relax main-branch guard for dispatch
# ============================================================
print("=== updatecli.yaml ===")
patch('.github/workflows/updatecli.yaml',
    "    if: github.ref == 'refs/heads/main'\n    strategy:",
    "    if: github.ref == 'refs/heads/main' || github.event_name == 'workflow_dispatch'\n    strategy:",
    "Relax main-branch guard for dispatch")

# ============================================================
# 4. updatecli_k8s.yaml - relax main-branch guard for dispatch
# ============================================================
print("=== updatecli_k8s.yaml ===")
patch('.github/workflows/updatecli_k8s.yaml',
    "    if: github.ref == 'refs/heads/main'\n    strategy:",
    "    if: github.ref == 'refs/heads/main' || github.event_name == 'workflow_dispatch'\n    strategy:",
    "Relax main-branch guard for dispatch")

print("\n=== All remaining patches complete! ===")
