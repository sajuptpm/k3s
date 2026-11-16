#!/usr/bin/env python3
import os
os.chdir(r'e:\projects\k3s')
with open('.github/workflows/release.yml', 'r', encoding='utf-8', newline='') as f:
    data = f.read()

# Fix the bash parameter expansion which should be ${TAG#refs/tags/} not ${{TAG#refs/tags/}}
data = data.replace('${{TAG#refs/tags/}}', '${TAG#refs/tags/}')
data = data.replace('${{RELEASE_TAG#refs/tags/}}', '${RELEASE_TAG#refs/tags/}')
data = data.replace('${{TAG}}', '${TAG}')

with open('.github/workflows/release.yml', 'w', encoding='utf-8', newline='') as f:
    f.write(data)

print("Fixed bash parameter expansion in release.yml")
