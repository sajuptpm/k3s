#!/usr/bin/env python3
import os
os.chdir(r'e:\projects\k3s')
with open('.github/workflows/trivy-trigger.yml', 'r', encoding='utf-8', newline='') as f:
    data = f.read()

data = data.replace('make local-image', 'make image')

with open('.github/workflows/trivy-trigger.yml', 'w', encoding='utf-8', newline='') as f:
    f.write(data)

print("Updated trivy-trigger.yml to use make image")
