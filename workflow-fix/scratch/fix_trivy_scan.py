#!/usr/bin/env python3
import os
os.chdir(r'e:\projects\k3s')
with open('.github/workflows/trivy-scan.yml', 'r', encoding='utf-8', newline='') as f:
    data = f.read()

le = '\r\n' if '\r\n' in data else '\n'

# 1. Add Trivy Report to PR check
old_post = f"""          if [[ "$SCAN_RESULT" == "failure" ]]; then{le}            gh issue comment $PR_NUMBER -b ":x: Trivy scan action failed, check logs :x:"{le}            exit 0{le}          fi"""

new_post = f"""          if [ -z "$PR_NUMBER" ] || [ "$PR_NUMBER" -le 0 ] 2>/dev/null; then{le}            echo "No PR number provided (dispatched test), skipping PR comment"{le}            exit 0{le}          fi{le}          if [[ "$SCAN_RESULT" == "failure" ]]; then{le}            gh issue comment $PR_NUMBER -b ":x: Trivy scan action failed, check logs :x:"{le}            exit 0{le}          fi"""

data = data.replace(old_post, new_post)

# 2. Remove label check
old_rem = f"""        run: |{le}          gh pr edit $PR_NUMBER --remove-label "scan-with-trivy\""""
new_rem = f"""        run: |{le}          if [ -n "$PR_NUMBER" ] && [ "$PR_NUMBER" -gt 0 ] 2>/dev/null; then{le}            gh pr edit $PR_NUMBER --remove-label "scan-with-trivy"{le}          fi"""

data = data.replace(old_rem, new_rem)

with open('.github/workflows/trivy-scan.yml', 'w', encoding='utf-8', newline='') as f:
    f.write(data)

print("Updated trivy-scan.yml")
