#!/usr/bin/env python3
import os
os.chdir(r'e:\projects\k3s')
with open('.github/workflows/scorecard.yml', 'r', encoding='utf-8', newline='') as f:
    data = f.read()

# Add env override for GITHUB_REF so ossf/scorecard-action sees default branch
old_step = '''      - name: "Run analysis"
        uses: ossf/scorecard-action@4eaacf0543bb3f2c246792bd56e8cdeffafb205a # v2.4.3
        with:'''

new_step = '''      - name: "Run analysis"
        uses: ossf/scorecard-action@4eaacf0543bb3f2c246792bd56e8cdeffafb205a # v2.4.3
        env:
          GITHUB_REF: refs/heads/${{ github.event.repository.default_branch }}
          GITHUB_REF_NAME: ${{ github.event.repository.default_branch }}
        with:'''

le = '\r\n' if '\r\n' in data else '\n'
old_step_norm = old_step.replace('\n', le)
new_step_norm = new_step.replace('\n', le)

if old_step_norm in data:
    data = data.replace(old_step_norm, new_step_norm)
    with open('.github/workflows/scorecard.yml', 'w', encoding='utf-8', newline='') as f:
        f.write(data)
    print("Updated scorecard.yml with default branch env override")
else:
    print("Target step not found in scorecard.yml")
