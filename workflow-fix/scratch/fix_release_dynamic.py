#!/usr/bin/env python3
import os
os.chdir(r'e:\projects\k3s')
with open('.github/workflows/release.yml', 'r', encoding='utf-8', newline='') as f:
    data = f.read()

le = '\r\n' if '\r\n' in data else '\n'

# 1. tag_config
old_tc = f'      - name: Configure image tags{le}        id: tag_config{le}        run: |{le}          TAG=${{GITHUB_REF#refs/tags/}}'
new_tc = f'      - name: Configure image tags{le}        id: tag_config{le}        run: |{le}          TAG="${{{{ inputs.tag || github.ref_name }}}}"{le}          TAG="${{{{TAG#refs/tags/}}}}"'
data = data.replace(old_tc, new_tc)

# 2. Set DockerHub Org & Extract Docker metadata
old_dho = f'      - name: Set DockerHub Org{le}        run: |{le}          if [ "${{{{ github.repository_owner }}}}" == "k3s-io" ]; then{le}            echo "DOCKERHUB_ORG=rancher" >> $GITHUB_ENV{le}          elif [ -n "${{{{ secrets.DOCKER_USERNAME }}}}" ]; then{le}            echo "DOCKERHUB_ORG=${{{{ secrets.DOCKER_USERNAME }}}}" >> $GITHUB_ENV{le}          else{le}            echo "DOCKERHUB_ORG=${{{{ github.repository_owner }}}}" >> $GITHUB_ENV{le}          fi{le}{le}      - name: Extract Docker metadata{le}        id: meta{le}        uses: docker/metadata-action@dc802804100637a589fabce1cb79ff13a1411302 # v6{le}        with:{le}          images: |{le}            ghcr.io/${{{{ github.repository_owner }}}}/k3s{le}            docker.io/${{{{ env.DOCKERHUB_ORG }}}}/k3s'

new_dho = f'      - name: Set DockerHub Org{le}        run: |{le}          if [ "${{{{ github.repository_owner }}}}" == "k3s-io" ]; then{le}            echo "DOCKERHUB_ORG=rancher" >> $GITHUB_ENV{le}            echo "ENABLE_DOCKERHUB=true" >> $GITHUB_ENV{le}          elif [ -n "${{{{ secrets.DOCKER_USERNAME }}}}" ]; then{le}            echo "DOCKERHUB_ORG=${{{{ secrets.DOCKER_USERNAME }}}}" >> $GITHUB_ENV{le}            echo "ENABLE_DOCKERHUB=true" >> $GITHUB_ENV{le}          else{le}            echo "DOCKERHUB_ORG=${{{{ github.repository_owner }}}}" >> $GITHUB_ENV{le}            echo "ENABLE_DOCKERHUB=false" >> $GITHUB_ENV{le}          fi{le}{le}      - name: Extract Docker metadata{le}        id: meta{le}        uses: docker/metadata-action@dc802804100637a589fabce1cb79ff13a1411302 # v6{le}        with:{le}          images: |{le}            ghcr.io/${{{{ github.repository_owner }}}}/k3s{le}            name=docker.io/${{{{ env.DOCKERHUB_ORG }}}}/k3s,enable=${{{{ env.ENABLE_DOCKERHUB == \'true\' }}}}'
data = data.replace(old_dho, new_dho)

# 3. Build-args TAG
old_ba = f'          build-args: |{le}            TAG=${{{{ github.ref_name }}}}'
new_ba = f'          build-args: |{le}            TAG=${{{{ inputs.tag || github.ref_name }}}}'
data = data.replace(old_ba, new_ba)

# 4. Create Pre-Release
old_rel = f'    - name: Create Pre-Release with Assets{le}      env:{le}        GH_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}{le}      run: gh release create -R "${{{{GITHUB_REPOSITORY}}}}" --prerelease --generate-notes "${{{{GITHUB_REF_NAME}}}}" "${{{{GITHUB_WORKSPACE}}}}"/dist/artifacts/k3s* "${{{{GITHUB_WORKSPACE}}}}"/dist/artifacts/sha256sum*'
new_rel = f'    - name: Create Pre-Release with Assets{le}      env:{le}        GH_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}{le}        RELEASE_TAG: ${{{{ inputs.tag || github.ref_name }}}}{le}      run: |{le}        TAG="${{{{RELEASE_TAG#refs/tags/}}}}"{le}        gh release create -R "${{{{GITHUB_REPOSITORY}}}}" --prerelease --generate-notes "${{{{TAG}}}}" "${{{{GITHUB_WORKSPACE}}}}"/dist/artifacts/k3s* "${{{{GITHUB_WORKSPACE}}}}"/dist/artifacts/sha256sum*'
data = data.replace(old_rel, new_rel)

with open('.github/workflows/release.yml', 'w', encoding='utf-8', newline='') as f:
    f.write(data)

print("Updated release.yml for dynamic tag and GHCR handling")
