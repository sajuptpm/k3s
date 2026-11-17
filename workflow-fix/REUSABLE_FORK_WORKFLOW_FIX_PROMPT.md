# Master Prompt: End-to-End Workflow Audit, Adaptation, Testing, and Documentation for Forked Repositories

> **Purpose**: This prompt is a battle-tested, end-to-end operational blueprint used by Claude Opus, Claude Sonnet, and Gemini to systematically audit, fork-adapt, execute, verify, and document all GitHub Actions CI/CD pipelines in a forked repository without cheating or skipping genuine tests.
> **How to Use**: Copy and paste the prompt below into any AI agent (Claude Code, Antigravity, OpenCode, VSCode Copilot, Cursor, etc.) when onboarding a newly forked repository.

---

```markdown
# MISSION: Complete Fork Adaptation, Verification, and Documentation of All GitHub Actions Workflows

You are tasked with auditing, adapting, testing, and thoroughly documenting ALL GitHub Actions workflows in this forked repository so that 100% of workflows execute genuinely, cleanly, and reproducibly in a personal or organizational fork.

---

## 1. ABSOLUTE CONSTRAINTS & ANTI-CHEATING POLICY (STRICT ENFORCEMENT)

1. **Zero Cheating / No Test Skipping**:
   - You MUST NOT disable tests using `if: false`, commenting out steps, deleting test files, or removing assertions.
   - You MUST NOT add blanket `continue-on-error: true` to suppress failing test steps.
   - All tests, binary builds, container image builds, airgap tarballs, and security scans MUST execute genuinely and generate real artifacts.
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
   - Every diff must satisfy:
     ```bash
     git apply --check --allow-empty workflow-fix/<name>.diff
     ```
3. **Credentials & Secrets Security**:
   - NEVER hardcode credentials, passwords, or personal access tokens into git commits, workflow YAML files, or scripts.
   - Sensitive credentials (Docker tokens, GitHub PATs, AWS keys) MUST be set via GitHub Secrets:
     ```bash
     echo "<TOKEN>" | gh secret set <SECRET_NAME> --repo <OWNER>/<REPO>
     ```
   - Non-sensitive feature toggles MUST be set via GitHub Variables:
     ```bash
     gh variable set <VAR_NAME> --body "false" --repo <OWNER>/<REPO>
     ```
4. **Actionlint Static Validation**:
   - Every single modified workflow file MUST pass actionlint with 0 errors before triggering:
     ```bash
     actionlint .github/workflows/<file>
     ```

---

## 2. SYSTEM ARCHITECTURE & LESSONS LEARNED (CRITICAL PITFALLS)

Keep these core GitHub Actions and tool behaviors in mind when designing fixes:

1. **`workflow_run` Default Branch Enforcement**:
   - Workflows triggered by `on: workflow_run` ALWAYS execute using the workflow YAML file located on the repository's **default branch (`main` or `master`)**, completely ignoring the branch where the triggering workflow ran.
   - If a `workflow_run` workflow fails due to upstream bugs, its fix CANNOT be tested on a feature branch alone; the PR containing the fix must be merged to the default branch to take effect.
2. **Container Actions Reading `/github/workflow/event.json` (e.g., OpenSSF Scorecard)**:
   - Actions like `ossf/scorecard-action` inspect GitHub's raw `event.json`. If `event.ref` is not `refs/heads/<default_branch>`, the binary exits with a fatal error: `Only the default branch is supported`.
   - Environment variables cannot spoof `event.json`. Such workflows must execute directly on the default branch.
3. **Windows PowerShell Redirection Pitfall**:
   - In Windows PowerShell, redirecting output with `git diff ... > file.diff` defaults to UTF-16LE or corrupts UTF-8 symbols (e.g. `→`).
   - ALWAYS use `git diff --output=workflow-fix/<name>.diff` to preserve byte-exact UTF-8 line endings.
4. **Actionlint Secret Context Restrictions**:
   - GitHub Actions disallows referencing the `secrets` context directly inside job-level `if:` or step-level `if:` expressions (`"secrets" is not available in the given context: if`).
   - Fix: Pass secrets via `env:` and check them inside the shell script:
     ```yaml
     env:
       MY_TOKEN: ${{ secrets.MY_TOKEN }}
     run: |
       if [ -z "$MY_TOKEN" ]; then
         echo "::warning::MY_TOKEN not configured. Skipping step."
         exit 0
       fi
     ```
5. **Runner Architecture Adaptation (Self-Hosted to Standard)**:
   - Upstream repositories often rely on expensive, private self-hosted runners (e.g., 32-core CNCF bare-metal bare machines).
   - In forks, create an alternate job gated by a repository variable (e.g. `vars.ENABLE_UPSTREAM_DOCKER_LARGE == 'true'`) and provide a fork-adapted job targeting standard GitHub-hosted runners (`ubuntu-24.04`) with calibrated scale parameters (e.g., reducing concurrent replica counts so tests pass without timeout).
6. **Tool Exit Code Semantics (e.g., `govulncheck`)**:
   - Some security scanners (such as Go's `govulncheck`) exit with non-zero exit codes (e.g. code 3) when known upstream vulnerabilities are detected in dependencies, while exit code 1 or 2 represents a tool crash.
   - Capture exit code 3 to display the vulnerability report without crashing CI, while preserving failures on actual crashes.
7. **Companion & Cross-Repository Dispatches**:
   - Upstream workflows often dispatch events to companion repositories (e.g. `<repo>-upgrade`).
   - Use dynamic URLs: `https://api.github.com/repos/${{ github.repository_owner }}/<companion-repo>/dispatches`.
   - Read personal access tokens dynamically and output helpful warnings if the PAT is not yet configured.

---

## 3. PHASE-BY-PHASE EXECUTION STRATEGY

### Phase 1: Baseline Establishment & Inventory
1. Pin `$BASE_COMMIT = $(git rev-parse HEAD)` and save it to `workflow-fix/.base_commit`.
2. Inventory all workflows in `.github/workflows/`:
   ```bash
   gh workflow list -a
   ```
3. Enable all workflows that GitHub disabled automatically upon forking:
   ```bash
   gh workflow enable <workflow-name-or-file>
   ```
4. Create a working branch:
   ```bash
   git checkout -b workflow-fix/audit-all-workflows
   ```
5. Open a Pull Request against `main` early to track ongoing check statuses.

### Phase 2: Tiered Pipeline Execution
Divide workflows into 3 tiers and execute systematically:

- **Tier 1: Fast & Static Checks (Linters, Security Scanners, Quick Units)**
  - Workflows: Actionlint, CodeQL, Stalebot, Unit tests, Validate.
  - Action: Add `workflow_dispatch` if missing, fix repository references, calibrate shallow clones, ensure actionlint passes.
  - Trigger and verify passing run IDs.

- **Tier 2: Core Build & Integration Suites**
  - Workflows: Airgap image tarballs, Reusable builds (`build-k3s`), Integration tests, VM install tests (`install.yaml`, `nightly-install.yaml`).
  - Action: Replace hardcoded self-hosted runners with standard GitHub runners (`ubuntu-24.04`, `ubuntu-24.04-arm`), calibrate Vagrant/KVM VM resource allocations, calibrate test concurrency from parallel to serial if runners become memory-constrained.
  - Trigger, monitor logs, and capture passing run proofs.

- **Tier 3: Complex Multi-Arch Release & Cross-Repo Pipelines**
  - Workflows: Release packaging (`release.yml`), OpenSSF Scorecard (`scorecard.yml`), Trivy scanning (`trivy-trigger.yml` & `trivy-scan.yml`), Dependency bots (`updatecli.yaml`).
  - Action:
    - Gated upstream-internal Vault and corporate S3 buckets behind `vars.ENABLE_UPSTREAM_RELEASE`.
    - Set up DockerHub and GHCR multi-arch login and release asset publishing.
    - Fix curl HTTP 302 redirect bugs (`curl -fsSLO`) and guard non-PR dispatches.
    - Provide token fallback for Scorecard (`SCORECARD_TOKEN || GITHUB_TOKEN`).
    - Connect companion repository dispatches with dynamic owner targeting.

### Phase 3: Merging & Final Default-Branch Verification
1. Verify all diffs apply cleanly against `$BASE_COMMIT`:
   ```bash
   git apply --check --allow-empty workflow-fix/*.diff
   ```
2. Merge the audited PR into `main` using `gh pr merge --merge`.
3. Switch local to `main` and pull:
   ```bash
   git checkout main && git pull origin main
   ```
4. Execute and verify the default-branch-restricted workflows on `main`:
   - Run Scorecard: `gh workflow run scorecard.yml --ref main`
   - Run Trivy Trigger: `gh workflow run trivy-trigger.yml --ref main` (which triggers `trivy-scan.yml` via `workflow_run`)
5. Confirm 100% success across all workflows.

---

## 4. REQUIRED DELIVERABLES CONTRACT

For EVERY workflow in the repository, you MUST generate two dedicated files inside the `workflow-fix/` directory:

### Deliverable A: `workflow-fix/<name>.diff`
- Must be a clean, standalone, unified patch file.
- Generated strictly against `$BASE_COMMIT`:
  ```bash
  git diff --output=workflow-fix/<name>.diff $BASE_COMMIT..HEAD -- .github/workflows/<file>
  ```
- If a workflow required 0 code modifications to pass, create a 0-byte file (`workflow-fix/<name>.diff`).

### Deliverable B: `workflow-fix/<name>.md`
Each markdown file must strictly follow this 6-section structure:
```markdown
# Workflow Fix & Audit Documentation: `<filename>`

## 1. Workflow Overview & Triggers
- Workflow Name, File path, Original Purpose, Triggers, Job Dependency Graph.

## 2. Root Cause Analysis in Fork
- Specific reasons why this workflow failed or was disabled in a fork context.

## 3. Detailed Code Changes & Rationale
- Line-by-line explanation of modifications and how genuine testing rigor is preserved.

## 4. Alternate Jobs & Feature Flags (If Applicable)
- Feature flags created, runner substitutions, or scale calibrations.

## 5. Secrets & Variables Created / Required
- Table of Secrets and Variables, their purpose, format, and exact `gh` CLI commands to configure them.

## 6. Verification Proof
- Workflow State, Verified Run ID, Direct Run URL, Execution Duration, and Job-by-Job breakdown table with status and duration.
```

### Deliverable C: Master Documentation
1. `workflow-fix/FINAL_ALL_WORKFLOWS_AUDIT_REPORT.md`: Comprehensive table listing all workflows, triggers, verified Run IDs, job pass counts, and summary of fixes.
2. `workflow-fix/FORK_RELEASE_AND_CREDENTIALS_AUDIT.md`: Complete audit of all skipped actions, release artifact impacts, and companion repository setup.
```

---

## Key Benefits of This Methodology

1. **100% Genuine CI/CD**: Ensures the fork produces genuine, production-grade binaries, container images, and test passes without synthetic shortcuts (`if: false` or blanket `continue-on-error`).
2. **Reversible & Upstream-Compatible**: All patches are cumulative against `$BASE_COMMIT` and use feature flags (`vars.ENABLE_*`), making upstream rebasing trivial.
3. **Zero Secrets in Git**: Mandates strict credential segregation using GitHub Secrets and Variables.
4. **Deterministic Auditing**: Provides a clear verification proof (Run ID, Run URL, Duration, Artifact list) for every single workflow.
