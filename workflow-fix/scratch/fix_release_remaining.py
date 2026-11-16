#!/usr/bin/env python3
"""Fix remaining k3s-io references in release.yml."""
import os
os.chdir(r'e:\projects\k3s')

with open('.github/workflows/release.yml', 'r', encoding='utf-8', newline='') as f:
    data = f.read()

# Count remaining k3s-io references
import re
matches = [(i+1, line.rstrip()) for i, line in enumerate(data.split('\n')) if 'k3s-io' in line]
print(f"Found {len(matches)} remaining k3s-io references:")
for ln, line in matches:
    print(f"  L{ln}: {line}")

# Replace remaining upstream-only conditions with ENABLE_UPSTREAM_RELEASE flag
# Line 57: if: ${{ github.repository_owner == 'k3s-io' }}
# Line 66: if: ${{ !contains(github.ref_name, '-rc') && github.repository_owner == 'k3s-io' }}
# Line 74: if: github.repository_owner == 'k3s-io'
# Line 82: if: github.repository_owner == 'k3s-io'
# Line 90: if: github.repository_owner != 'k3s-io'
# Line 97: if: github.repository_owner == 'k3s-io'
# Line 105: if: ${{ !contains(github.ref_name, '-rc') && github.repository_owner == 'k3s-io' }}
# Line 139: if [ "${{ github.repository_owner }}" == "k3s-io" ]; then

# push-release-image job vault/login steps
data = data.replace(
    "        if: ${{ github.repository_owner == 'k3s-io' }}\r\n        with:\r\n          secrets: |\r\n            secret/data/github/repo/${{ github.repository }}/k3s-suse-registry-stg",
    "        if: ${{ vars.ENABLE_UPSTREAM_RELEASE == 'true' }}\r\n        with:\r\n          secrets: |\r\n            secret/data/github/repo/${{ github.repository }}/k3s-suse-registry-stg"
)

data = data.replace(
    "        if: ${{ !contains(github.ref_name, '-rc') && github.repository_owner == 'k3s-io' }}\r\n        with:\r\n          secrets: |\r\n            secret/data/github/repo/${{ github.repository }}/k3s-suse-registry/credentials",
    "        if: ${{ vars.ENABLE_UPSTREAM_RELEASE == 'true' && !contains(github.ref_name, '-rc') }}\r\n        with:\r\n          secrets: |\r\n            secret/data/github/repo/${{ github.repository }}/k3s-suse-registry/credentials"
)

data = data.replace(
    "        if: github.repository_owner == 'k3s-io'\r\n        uses: rancher-eio/read-vault-secrets",
    "        if: ${{ vars.ENABLE_UPSTREAM_RELEASE == 'true' }}\r\n        uses: rancher-eio/read-vault-secrets"
)

data = data.replace(
    "        if: github.repository_owner == 'k3s-io'\r\n        uses: docker/login-action",
    "        if: ${{ vars.ENABLE_UPSTREAM_RELEASE == 'true' }}\r\n        uses: docker/login-action"
)

data = data.replace(
    "        if: github.repository_owner != 'k3s-io'\r\n        uses: docker/login-action",
    "        if: ${{ vars.ENABLE_UPSTREAM_RELEASE != 'true' && secrets.DOCKER_USERNAME != '' }}\r\n        uses: docker/login-action"
)

data = data.replace(
    "      - name: Login to Staging Registry\r\n        if: github.repository_owner == 'k3s-io'",
    "      - name: Login to Staging Registry\r\n        if: ${{ vars.ENABLE_UPSTREAM_RELEASE == 'true' }}"
)

data = data.replace(
    "      - name: Login to Prime Registry\r\n        if: ${{ !contains(github.ref_name, '-rc') && github.repository_owner == 'k3s-io' }}",
    "      - name: Login to Prime Registry\r\n        if: ${{ vars.ENABLE_UPSTREAM_RELEASE == 'true' && !contains(github.ref_name, '-rc') }}"
)

# upload-release-assets job vault steps
data = data.replace(
    "      if: ${{ github.repository_owner == 'k3s-io' }}\r\n      with:\r\n        secrets: |\r\n          secret/data/github/repo/${{ github.repository }}/prime-artifacts-uploader",
    "      if: ${{ vars.ENABLE_UPSTREAM_RELEASE == 'true' }}\r\n      with:\r\n        secrets: |\r\n          secret/data/github/repo/${{ github.repository }}/prime-artifacts-uploader"
)

data = data.replace(
    "      if: ${{ contains(github.ref_name, '-rc') && github.repository_owner == 'k3s-io' }}",
    "      if: ${{ vars.ENABLE_UPSTREAM_RELEASE == 'true' && contains(github.ref_name, '-rc') }}"
)

data = data.replace(
    "      if: ${{ !contains(github.ref_name, '-rc') && github.repository_owner == 'k3s-io' }}\r\n      with:\r\n        secrets: |\r\n          secret/data/github/repo/${{ github.repository }}/k3s-suse-registry/credentials registry | REGISTRY",
    "      if: ${{ vars.ENABLE_UPSTREAM_RELEASE == 'true' && !contains(github.ref_name, '-rc') }}\r\n      with:\r\n        secrets: |\r\n          secret/data/github/repo/${{ github.repository }}/k3s-suse-registry/credentials registry | REGISTRY"
)

with open('.github/workflows/release.yml', 'w', encoding='utf-8', newline='') as f:
    f.write(data)

# Re-check
matches2 = [(i+1, line.rstrip()) for i, line in enumerate(data.split('\n')) if 'k3s-io' in line]
print(f"\nAfter fix: {len(matches2)} remaining k3s-io references:")
for ln, line in matches2:
    print(f"  L{ln}: {line}")

if len(matches2) == 0:
    print("\nAll k3s-io references replaced!")
else:
    # Check if remaining are in non-functional places (comments, etc.)
    for ln, line in matches2:
        if 'k3s-io' in line and '#' not in line.split('k3s-io')[0]:
            print(f"  WARNING: Active k3s-io ref at line {ln}")
