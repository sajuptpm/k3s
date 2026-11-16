#!/usr/bin/env python3
import os
os.chdir(r'e:\projects\k3s')
data = open('.github/workflows/release.yml', 'r', encoding='utf-8', newline='').read()
data = data.replace(
    "if: ${{ vars.ENABLE_UPSTREAM_RELEASE != 'true' && secrets.DOCKER_USERNAME != '' }}",
    "if: ${{ vars.ENABLE_UPSTREAM_RELEASE != 'true' }}"
)
open('.github/workflows/release.yml', 'w', encoding='utf-8', newline='').write(data)
print('Fixed secrets context in step if')
