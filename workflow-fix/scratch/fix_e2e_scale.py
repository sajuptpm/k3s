#!/usr/bin/env python3
import os
os.chdir(r'e:\projects\k3s')
with open('.github/workflows/e2e.yaml', 'r', encoding='utf-8', newline='') as f:
    data = f.read()

old_cmd = 'ginkgo run -v -timeout=40m ./tests/docker/scale/ -- -ci -k3sImage=$K3S_IMAGE'
new_cmd = 'ginkgo run -v -timeout=40m ./tests/docker/scale/ -- -ci -k3sImage=$K3S_IMAGE -serverCount=1 -agentCount=2 -namespaceCount=2 -deploymentsPerNamespace=2 -replicasPerDeployment=2'

if old_cmd in data:
    data = data.replace(old_cmd, new_cmd)
    with open('.github/workflows/e2e.yaml', 'w', encoding='utf-8', newline='') as f:
        f.write(data)
    print('Updated e2e.yaml scale flags for fork compute')
else:
    print('Target not found in e2e.yaml')
