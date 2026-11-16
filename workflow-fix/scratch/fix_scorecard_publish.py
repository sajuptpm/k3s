#!/usr/bin/env python3
import os
os.chdir(r'e:\projects\k3s')
with open('.github/workflows/scorecard.yml', 'r', encoding='utf-8', newline='') as f:
    data = f.read()

# Replace publish_results: true with conditional
data = data.replace(
    '          publish_results: true',
    "          publish_results: ${{ github.ref_name == github.event.repository.default_branch }}"
)

with open('.github/workflows/scorecard.yml', 'w', encoding='utf-8', newline='') as f:
    f.write(data)
print('Updated publish_results in scorecard.yml')
