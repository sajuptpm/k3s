import os

with open('.github/workflows/release.yml', 'r', encoding='utf-8') as f:
    content = f.read()

target = """  dispatch-k3s-upgrade:
    name: Dispatch k3s-upgrade Workflow
    runs-on: ubuntu-24.04
    if: ${{ vars.ENABLE_UPSTREAM_RELEASE == 'true' }}
    needs: [upload-release-assets]
    steps:
      - name: Dispatch k3s-upgrade Workflow
        run: |
          curl -L -XPOST \\
            -H "Accept: application/vnd.github+json" \\
            -H "Authorization: Bearer ${{ secrets.K3S_UPGRADE_PAT }}" \\
            -H "Content-Type: application/json" \\
            https://api.github.com/repos/${{ github.repository_owner }}/k3s-upgrade/dispatches \\
            -d '{"event_type":"tag-release","client_payload":{"tag":"${{ github.ref_name }}"}}'
"""

replacement = """  dispatch-k3s-upgrade:
    name: Dispatch k3s-upgrade Workflow
    runs-on: ubuntu-24.04
    needs: [upload-release-assets]
    steps:
      - name: Dispatch k3s-upgrade Workflow
        env:
          K3S_UPGRADE_PAT: ${{ secrets.K3S_UPGRADE_PAT }}
          TAG: ${{ inputs.tag || github.ref_name }}
        run: |
          if [ -z "$K3S_UPGRADE_PAT" ]; then
            echo "::warning::K3S_UPGRADE_PAT secret is not configured. Skipping dispatch to k3s-upgrade."
            exit 0
          fi
          TAG="${TAG#refs/tags/}"
          echo "Dispatching tag-release event to https://api.github.com/repos/${{ github.repository_owner }}/k3s-upgrade/dispatches with tag ${TAG}..."
          HTTP_CODE=$(curl -s -w "%{http_code}" -o response.json -L -XPOST \\
            -H "Accept: application/vnd.github+json" \\
            -H "Authorization: Bearer ${K3S_UPGRADE_PAT}" \\
            -H "Content-Type: application/json" \\
            "https://api.github.com/repos/${{ github.repository_owner }}/k3s-upgrade/dispatches" \\
            -d "{\\"event_type\\":\\"tag-release\\",\\"client_payload\\":{\\"tag\\":\\"${TAG}\\"}}")
          if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 300 ]; then
            echo "Successfully dispatched tag-release to ${{ github.repository_owner }}/k3s-upgrade (HTTP $HTTP_CODE)"
          else
            echo "::error::Failed to dispatch to k3s-upgrade (HTTP $HTTP_CODE):"
            cat response.json
            exit 1
          fi
"""

content_norm = content.replace('\r\n', '\n')
target_norm = target.replace('\r\n', '\n')
replacement_norm = replacement.replace('\r\n', '\n')

if target_norm in content_norm:
    new_content = content_norm.replace(target_norm, replacement_norm)
    with open('.github/workflows/release.yml', 'w', encoding='utf-8', newline='\n') as f:
        f.write(new_content)
    print("Replaced successfully!")
else:
    print("Target not found in content!")
