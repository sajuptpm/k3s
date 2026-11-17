# Universal Master Prompt: Fork Workflow Audit, Adaptation, Testing, and Verification for Any GitHub Project

> **Compatibility**: 100% Universal and Language-Agnostic. Applies to Go, Rust, Python, Node.js/TypeScript, Java/JVM, C/C++, Kubernetes-native, Microservices, and Web projects.
> **How to Use**: Copy and paste the prompt block below into any AI agent (Claude Code, Antigravity, OpenCode, VSCode Copilot, Cursor, etc.) when onboarding ANY newly forked GitHub repository.

---

```markdown
# MISSION: Universal Fork CI/CD Workflow Audit, Adaptation, Verification, and Documentation

You are tasked with auditing, adapting, testing, and thoroughly documenting ALL GitHub Actions CI/CD workflows in this forked repository so that 100% of workflows execute genuinely, cleanly, and reproducibly in a personal or organizational fork.

---

## 1. ABSOLUTE CONSTRAINTS & ANTI-CHEATING POLICY (STRICT ENFORCEMENT)

1. **Zero Cheating / No Test Skipping**:
   - You MUST NOT disable tests using `if: false`, commenting out steps, deleting test files, or removing assertions.
   - You MUST NOT add blanket `continue-on-error: true` to suppress failing test steps.
   - All tests (unit, integration, e2e), linters, binary builds, container image packaging, and security scans MUST execute genuinely and generate real artifacts.
2. **Preserve Baseline Integrity**:
   - At Step 0, capture the base commit:
     ```bash
     git rev-parse HEAD > workflow-fix/.base_commit
     ```
   - Store this baseline commit as `$BASE_COMMIT`.
   - ALL diff deliverables (`workflow-fix/<name>.diff`) MUST be generated strictly and cumulatively against this exact `$BASE_COMMIT` using:
     ```bash
     git diff --output=workflow-fix/<name>.diff $BASE_COMMIT..HEAD -- .github/workflows/<file>
     ```
   - Every patch must apply cleanly against `$BASE_COMMIT`:
     ```bash
     git apply --check --allow-empty workflow-fix/<name>.diff
     ```
3. **Credentials & Secrets Security**:
   - NEVER hardcode credentials, passwords, or personal access tokens into git commits, workflow YAML files, or scripts.
   - Sensitive credentials (Docker tokens, GitHub PATs, AWS/GCP keys, package registry tokens) MUST be stored via GitHub Secrets:
     ```bash
     echo "<TOKEN>" | gh secret set <SECRET_NAME> --repo <OWNER>/<REPO>
     ```
   - Non-sensitive feature toggles and flags MUST be set via GitHub Variables:
     ```bash
     gh variable set <VAR_NAME> --body "false" --repo <OWNER>/<REPO>
     ```
4. **Actionlint Static Validation**:
   - Every single modified workflow file MUST pass actionlint with 0 errors before triggering:
     ```bash
     actionlint .github/workflows/<file>
     ```

---

## 2. UNIVERSAL FORK FAILURE PATTERNS & BATTLE-TESTED FIXES

Across any GitHub project (Go, Python, Node, Rust, Java, etc.), forked workflows commonly fail for the same architectural reasons. Apply these battle-tested patterns:

### A. Upstream Organization Gates
- **Symptom**: `if: github.repository_owner == 'upstream-org'` or `if: github.repository == 'upstream-org/repo'` causes entire jobs or steps to be skipped in forks.
- **Fix**: Replace hardcoded organization checks with repository variables or dynamic context:
  ```yaml
  # Allow fork maintainers to control corporate infrastructure via variable:
  if: ${{ vars.ENABLE_UPSTREAM_RELEASE == 'true' }}
  ```
  Or target the current fork owner dynamically:
  ```yaml
  image: ghcr.io/${{ github.repository_owner }}/my-app
  ```

### B. Self-Hosted & Enterprise Runner Dependencies
- **Symptom**: Jobs configured with `runs-on: [self-hosted, linux, bare-metal]` or custom organization fleet labels remain queued indefinitely in forks.
- **Fix**: Provide a dual-path architecture:
  1. Keep upstream job for upstream fleets behind `if: ${{ vars.ENABLE_UPSTREAM_RUNNERS == 'true' }}`.
  2. Create a fork-adapted job targeting GitHub-hosted standard runners (`ubuntu-24.04`, `ubuntu-24.04-arm`, `windows-latest`, `macos-latest`) with `if: ${{ vars.ENABLE_UPSTREAM_RUNNERS != 'true' }}`.
  3. If tests are resource-intensive, calibrate concurrency (e.g. run suites serially or calibrate scale test parameters) so they succeed reliably within standard GitHub runner limits.

### C. Missing Upstream Secrets & Registries
- **Symptom**: Steps crash because upstream secrets (Vault AppRoles, AWS S3 keys, SonarQube tokens, commercial package registries) do not exist in the fork.
- **Fix**:
  1. Gate proprietary third-party publishing/mirroring steps behind `vars.ENABLE_UPSTREAM_*`.
  2. Implement graceful authentication fallbacks (e.g., publish to GitHub Container Registry `ghcr.io` via built-in `GITHUB_TOKEN` by default; authenticate to DockerHub/PyPI/npm only if the user provides the repository secrets).

### D. GitHub Actions `workflow_run` Default Branch Enforcement
- **Symptom**: Downstream workflows triggered by `on: workflow_run` execute outdated or broken code despite committing fixes on a feature branch.
- **Root Cause**: GitHub Actions specification strictly mandates that workflows triggered by `workflow_run` ALWAYS execute using the YAML file on the **repository's default branch (`main` or `master`)**.
- **Fix**: Merge the PR into `main` so the fixed workflow definition is present on `main` before testing `workflow_run` triggers.

### E. Container Actions Reading `/github/workflow/event.json` (e.g., OpenSSF Scorecard)
- **Symptom**: Container actions fail with `Only the default branch is supported`.
- **Root Cause**: The container directly parses `/github/workflow/event.json`. If `event.ref` is not `refs/heads/<default_branch>`, it aborts. Environment variables cannot spoof this.
- **Fix**: Run and verify default-branch-restricted actions directly on `main` after merging the PR.

### F. Shell & Tool Exit Code Differentiations
- **Symptom**: Diagnostic or security scanners (e.g., `govulncheck`, audit tools) return a non-zero exit code (e.g. code 3) when known dependency vulnerabilities exist, failing CI even when the tool executed properly.
- **Fix**: Distinguish between informational finding exit codes and fatal tool crash codes (code 1 or 2):
  ```bash
  EXIT_CODE=0
  tool_binary ./... || EXIT_CODE=$?
  if [ "$EXIT_CODE" -eq 3 ]; then
    echo "Vulnerabilities detected; report displayed above."
    exit 0
  elif [ "$EXIT_CODE" -ne 0 ]; then
    echo "Tool crashed with exit code $EXIT_CODE"
    exit $EXIT_CODE
  fi
  ```

### G. Dispatching Companion Repositories
- **Symptom**: Upstream releases trigger companion repositories via repository dispatches (`curl -XPOST .../dispatches`) using hardcoded paths and missing PATs.
- **Fix**: Target companion repos dynamically:
  ```bash
  https://api.github.com/repos/${{ github.repository_owner }}/<companion-repo>/dispatches
  ```
  Check if the personal access token (`${{ secrets.COMPANION_PAT }}`) is set; if unset, output a clear `::warning::` without failing the core release.

### H. Windows / Cross-Platform PowerShell Encoding
- **Symptom**: Windows PowerShell redirection (`>`) emits UTF-16LE or corrupts UTF-8 symbols, causing `git apply` to fail with patch corruption.
- **Fix**: Always use Git's built-in binary-safe output flag:
  ```bash
  git diff --output=workflow-fix/<name>.diff $BASE_COMMIT..HEAD -- <file>
  ```

---

## 3. THREE-TIER EXECUTION STRATEGY

Divide the repository's workflows into three distinct tiers and execute systematically:

```
┌───────────────────────────────────────────────────────────┐
│ Tier 1: Static, Linters, Security Scanners & Unit Tests   │
│ (Actionlint, Linters, CodeQL, Stalebot, Fast Unit Suites) │
└─────────────────────────────┬─────────────────────────────┘
                              ▼
┌───────────────────────────────────────────────────────────┐
│ Tier 2: Core Build & Integration Pipelines               │
│ (Reusable Builds, Integration Tests, VM/OS Smoke Tests)   │
└─────────────────────────────┬─────────────────────────────┘
                              ▼
┌───────────────────────────────────────────────────────────┐
│ Tier 3: Packaging, Multi-Arch Release & Security Audits   │
│ (Releases, Multi-Arch Images, Trivy, Scorecard, Bots)     │
└───────────────────────────────────────────────────────────┘
```

### Phase 1: Baseline & Inventory
1. Pin `$BASE_COMMIT = $(git rev-parse HEAD)` in `workflow-fix/.base_commit`.
2. List all workflows: `gh workflow list -a`.
3. Enable all workflows that GitHub disabled automatically: `gh workflow enable <id-or-name>`.
4. Create audit branch: `git checkout -b workflow-fix/audit-all-workflows`.
5. Open PR early against `main` to track check status.

### Phase 2: Tiered Pipeline Verification
- **Execute Tier 1**: Add `workflow_dispatch` where missing, fix shallow checkout depths, verify actionlint, trigger runs, and document passing run IDs.
- **Execute Tier 2**: Adapt runners to GitHub-hosted instances, calibrate test parallelism/resources if runners face memory pressure, verify builds and uploads.
- **Execute Tier 3**:
  - Gated proprietary third-party infrastructure with repository variables.
  - Setup container publishing to GHCR and/or DockerHub with repository secrets.
  - Verify release asset generation, checksum calculation, and release tagging.

### Phase 3: Merging PR & Verifying Default-Branch Workflows
1. Verify all diffs apply cleanly against `$BASE_COMMIT`:
   ```bash
   git apply --check --allow-empty workflow-fix/*.diff
   ```
2. Merge the audited PR into `main` (`gh pr merge --merge`).
3. Switch local to `main` and pull latest: `git checkout main && git pull origin main`.
4. Trigger and verify workflows that mandate default branch execution (e.g., Scorecard, Trivy scan via `workflow_run`).
5. Confirm 100% of workflows have verified passing runs.

---

## 4. REQUIRED DELIVERABLES CONTRACT

For EVERY workflow in the repository, create two dedicated files in `workflow-fix/`:

### Deliverable 1: `workflow-fix/<name>.diff`
- Standalone patch against `$BASE_COMMIT`.
- Generated strictly via `git diff --output=workflow-fix/<name>.diff $BASE_COMMIT..HEAD -- .github/workflows/<file>`.
- If a workflow required 0 modifications, create an empty 0-byte `.diff` file.

### Deliverable 2: `workflow-fix/<name>.md`
Each file must follow this exact 6-section structure:
```markdown
# Workflow Fix & Audit Documentation: `<filename>`

## 1. Workflow Overview & Triggers
- Workflow Name, File Path, Original Purpose, Triggers, Job Dependency Graph.

## 2. Root Cause Analysis in Fork
- Specific reasons why this workflow failed, was skipped, or was disabled in the fork.

## 3. Detailed Code Changes & Rationale
- Line-by-line explanation of changes and how genuine testing integrity is preserved.

## 4. Alternate Jobs & Feature Flags (If Applicable)
- Runner substitutions, scale parameter calibrations, or feature flags introduced.

## 5. Secrets & Variables Created / Required
- Table of Secrets and Variables, their purpose, format, and exact `gh` CLI commands to configure them.

## 6. Verification Proof
- Workflow State, Verified Run ID, Direct Run URL, Duration, and Job-by-Job breakdown table.
```

### Deliverable 3: Master Reports
- `workflow-fix/FINAL_ALL_WORKFLOWS_AUDIT_REPORT.md`: Master matrix of all workflows, verified run IDs, duration, and status.
- `workflow-fix/FORK_RELEASE_AND_CREDENTIALS_AUDIT.md`: Complete audit of all skipped actions, release artifact impacts, and required credentials.
```

---

## Why This Prompt Works Universally

1. **Language & Ecosystem Neutral**: It does not assume Go, Python, or JavaScript; rather, it targets the **GitHub Actions orchestrator layer**, runner management, secret segregation, and event semantics that govern all GitHub repositories.
2. **Eliminates False Assumptions**: Prevents common LLM failures such as modifying code on feature branches and wondering why `workflow_run` didn't execute the change, or breaking `actionlint` by using `secrets` in `if:`.
3. **Enterprise Audit Quality**: Leaves behind complete documentation, unified patches, and reproducible proof that any software engineering team or compliance auditor can inspect.
