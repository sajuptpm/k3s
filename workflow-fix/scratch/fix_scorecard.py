#!/usr/bin/env python3
import os
os.chdir(r'e:\projects\k3s')
data = open('.github/workflows/scorecard.yml', 'r', encoding='utf-8', newline='').read()
# Add workflow_dispatch to the if condition
data = data.replace(
    "if: github.event.repository.default_branch == github.ref_name || github.event_name == 'pull_request'",
    "if: github.event.repository.default_branch == github.ref_name || github.event_name == 'pull_request' || github.event_name == 'workflow_dispatch'"
)
open('.github/workflows/scorecard.yml', 'w', encoding='utf-8', newline='').write(data)
print('Fixed scorecard.yml condition for dispatch')
