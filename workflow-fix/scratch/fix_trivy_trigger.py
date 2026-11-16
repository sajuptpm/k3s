#!/usr/bin/env python3
import os
os.chdir(r'e:\projects\k3s')
with open('.github/workflows/trivy-trigger.yml', 'r', encoding='utf-8', newline='') as f:
    data = f.read()

le = '\r\n' if '\r\n' in data else '\n'

# 1. Job if condition
old_if = f"    if: github.event.label.name == 'scan-with-trivy'"
new_if = f"    if: github.event.label.name == 'scan-with-trivy' || github.event_name == 'workflow_dispatch'"
data = data.replace(old_if, new_if)

# 2. Script body
old_script = f"""          script: |{le}            const org = context.repo.owner;{le}            const actor = context.actor;{le}            const {{ repo, owner }} = context.repo; {le}            {le}            try {{{le}              const result = await github.rest.orgs.checkMembershipForUser({{{le}                org,{le}                username: actor,{le}              }});{le}            }} catch (error) {{{le}              core.setFailed(`User ${{actor}} is not an public member of the ${{org}} organization`);{le}            }}{le}{le}            const {{ data: {{ permission }} }} = await github.rest.repos.getCollaboratorPermissionLevel({{{le}              owner,{le}              repo,{le}              username: actor{le}            }});{le}            {le}            if (permission !== 'admin' && permission !== 'write') {{{le}              core.setFailed(`User @${{actor}} does not have write permission. Scan can only be triggered by repository collaborators with write access.`);{le}            }}"""

new_script = f"""          script: |{le}            const actor = context.actor;{le}            const {{ repo, owner }} = context.repo; {le}            {le}            const {{ data: {{ permission }} }} = await github.rest.repos.getCollaboratorPermissionLevel({{{le}              owner,{le}              repo,{le}              username: actor{le}            }});{le}            {le}            if (permission !== 'admin' && permission !== 'write') {{{le}              core.setFailed(`User @${{actor}} does not have write permission. Scan can only be triggered by repository collaborators with write access.`);{le}            }}"""
data = data.replace(old_script, new_script)

# 3. PR_NUM fallback
old_pr = f'        env:{le}          PR_NUM: ${{{{ github.event.pull_request.number }}}}'
new_pr = f'        env:{le}          PR_NUM: ${{{{ github.event.pull_request.number || 0 }}}}'
data = data.replace(old_pr, new_pr)

with open('.github/workflows/trivy-trigger.yml', 'w', encoding='utf-8', newline='') as f:
    f.write(data)

print("Updated trivy-trigger.yml")
