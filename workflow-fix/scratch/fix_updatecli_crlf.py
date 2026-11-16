#!/usr/bin/env python3
import os
os.chdir(r'e:\projects\k3s')

def update_file(path, old_sub, new_sub):
    with open(path, 'r', encoding='utf-8', newline='') as f:
        data = f.read()
    le = '\r\n' if '\r\n' in data else '\n'
    old_norm = old_sub.replace('\n', le)
    new_norm = new_sub.replace('\n', le)
    if old_norm in data:
        data = data.replace(old_norm, new_norm)
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(data)
        print(f"Updated {path}")
        return True
    else:
        print(f"Target not found in {path}")
        return False

old_matrix1 = '''      matrix:
        include:
          - branch: main
            helm_controller_pattern: "*"
          - branch: release-1.37
            helm_controller_pattern: "~0.17"
          - branch: release-1.36
            helm_controller_pattern: "~0.17"
          - branch: release-1.35
            helm_controller_pattern: "~0.17"
          - branch: release-1.34
            helm_controller_pattern: "~0.16"'''

new_matrix1 = '''      matrix:
        include:
          - branch: main
            helm_controller_pattern: "*"'''

update_file('.github/workflows/updatecli.yaml', old_matrix1, new_matrix1)

old_matrix2 = '''      matrix:
        branch: 
          - main
          - release-1.37
          - release-1.36
          - release-1.35
          - release-1.34'''

new_matrix2 = '''      matrix:
        branch: 
          - main'''

update_file('.github/workflows/updatecli_k8s.yaml', old_matrix2, new_matrix2)
