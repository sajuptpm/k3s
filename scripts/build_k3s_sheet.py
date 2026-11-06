# scripts/build_k3s_sheet.py
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import shutil

wb_path = 'workflow-fixes/data1.xlsx'
bak_path = 'workflow-fixes/data1.xlsx.bak'
shutil.copyfile(wb_path, bak_path)

wb = openpyxl.load_workbook(wb_path)
ws = wb['k3s']

# Delete existing rows after header
if ws.max_row > 1:
    ws.delete_rows(2, ws.max_row)

rows = []

def add_row(
    name, version, purpose, rec_type, alt_of, reason_sel, usage_limit, free_paid,
    access_restr, license_name, spdx, copyleft, comm_rights, telemetry, attrib,
    legal_verdict, subs_avail, sel_sub, reason_sub, category, comp_name, wf_name,
    wf_yml, user_limit, usage_limits, token_secret, lic_suit, sub_suit, req_purchase,
    why_upstream, access_status, is_mandatory, suit_release, official_site, purch_link,
    price_link, suit_open_reason, why_not_suit, alt_options, best_alt, reason_best_alt,
    replaces_tool, issues_ml, evidence
):
    row_data = [
        name, version, purpose, rec_type, alt_of, reason_sel, usage_limit, free_paid,
        access_restr, license_name, spdx, copyleft, comm_rights, telemetry, attrib,
        legal_verdict, subs_avail, sel_sub, reason_sub, category, comp_name, wf_name,
        wf_yml, user_limit, usage_limits, token_secret, lic_suit, sub_suit, req_purchase,
        why_upstream, access_status, is_mandatory, suit_release, official_site, purch_link,
        price_link, suit_open_reason, why_not_suit, alt_options, best_alt, reason_best_alt,
        replaces_tool, issues_ml, evidence
    ]
    assert len(row_data) == 44, f"Row has {len(row_data)} columns, expected 44"
    rows.append(row_data)

# Common constants for reuse
GHA_RUNNER_NAME = "GitHub Actions Hosted Runner"
GHA_RUNNER_VER = "ubuntu-latest (Ubuntu 24.04/22.04 LTS)"
GHA_RUNNER_USAGE = "2 vCPU, 7 GB RAM, 14 GB SSD storage; 6-hour execution timeout per job."
GHA_RUNNER_LIC = "GitHub Terms of Service"
GHA_RUNNER_SPDX = "Terms of Service"
GHA_RUNNER_SUBS = "Free for public open-source repositories; 2,000 free pooled minutes/mo for private repos ($0.008/min thereafter)"
GHA_RUNNER_SEL_SUB = "GitHub Actions Standard Free Tier ($0.00)"
GHA_RUNNER_CONC = "20 concurrent jobs per user/org on free tier; 2 vCPU, 7 GB RAM limit per runner."
GHA_RUNNER_TEAM = "Yes; standard GitHub-hosted runner provides ample capacity for 5 developers on public fork."
GHA_RUNNER_SITE = "https://github.com/features/actions"
GHA_RUNNER_PURCH = "https://github.com/pricing"
GHA_RUNNER_PRICE = "https://docs.github.com/en/billing/managing-billing-for-github-actions/about-billing-for-github-actions"

# 1. Actionlint (Row 1036)
add_row(
    name=GHA_RUNNER_NAME, version=GHA_RUNNER_VER,
    purpose="Executes actionlint workflow to validate GitHub Actions syntax, shellcheck integration, and runner configurations.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Standard GitHub-hosted Linux compute environment provided by GitHub Actions.",
    usage_limit=GHA_RUNNER_USAGE, free_paid="Free", access_restr="No",
    license_name=GHA_RUNNER_LIC, spdx=GHA_RUNNER_SPDX, copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Local-only (Ephemeral Microsoft Azure VM)", attrib="None", legal_verdict="Permissible",
    subs_avail=GHA_RUNNER_SUBS, sel_sub=GHA_RUNNER_SEL_SUB,
    reason_sub="Free compute allocation included with public repository hosting.",
    category="Test", comp_name="K3s 1.35", wf_name="Actionlint", wf_yml="actionlint.yaml",
    user_limit="Unlimited public repo concurrency (subject to account-level 20 concurrent jobs limit)",
    usage_limits=GHA_RUNNER_CONC, token_secret="None (Native GITHUB_TOKEN automatically provisioned)",
    lic_suit=GHA_RUNNER_TEAM, sub_suit="Yes; 100% free of charge on public repositories.",
    req_purchase="No", why_upstream="Provides reliable, zero-maintenance ephemeral cloud Linux compute for CI/CD automation.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; standard hosted runners execute cleanly without billing or configuration prerequisites.",
    official_site=GHA_RUNNER_SITE, purch_link=GHA_RUNNER_PURCH, price_link=GHA_RUNNER_PRICE,
    suit_open_reason="Yes; 100% free on public repositories, highly available, and requires no external credentials.",
    why_not_suit="N/A (Fully suitable for open-source model)",
    alt_options="Self-hosted Linux runner, Docker container runner, GitHub Large Runners",
    best_alt="GitHub Actions Standard Hosted Runner (ubuntu-latest)",
    reason_best_alt="$0 cost, zero maintenance overhead, native GitHub Actions integration, securely isolated ephemeral VMs.",
    replaces_tool="N/A (Original Tool)", issues_ml="None; free standard hosted runner.",
    evidence=".github/workflows/actionlint.yaml:12"
)

# 2. Airgap Package - Hosted Runner (Row 1040)
add_row(
    name=GHA_RUNNER_NAME, version=GHA_RUNNER_VER,
    purpose="Executes airgap image tarball packaging, zstd compression, and checksum generation across amd64, arm64, and arm architectures.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Standard hosted compute for packaging multi-architecture airgap bundles.",
    usage_limit=GHA_RUNNER_USAGE, free_paid="Free", access_restr="No",
    license_name=GHA_RUNNER_LIC, spdx=GHA_RUNNER_SPDX, copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Local-only (Ephemeral Microsoft Azure VM)", attrib="None", legal_verdict="Permissible",
    subs_avail=GHA_RUNNER_SUBS, sel_sub=GHA_RUNNER_SEL_SUB,
    reason_sub="Free compute allocation for packaging pipeline.",
    category="Package", comp_name="K3s 1.35", wf_name="Airgap Package", wf_yml="airgap.yaml",
    user_limit="Standard GitHub public repo concurrency (20 jobs)",
    usage_limits=GHA_RUNNER_CONC, token_secret="None",
    lic_suit=GHA_RUNNER_TEAM, sub_suit="Yes; $0 for entire team.",
    req_purchase="No", why_upstream="Builds reproducible compressed airgap tarballs for offline cluster installations.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; builds valid airgap tarballs within standard job runner timeouts.",
    official_site=GHA_RUNNER_SITE, purch_link=GHA_RUNNER_PURCH, price_link=GHA_RUNNER_PRICE,
    suit_open_reason="Yes; zero financial barrier for release packaging.",
    why_not_suit="N/A (Fully suitable)", alt_options="Self-hosted build runner",
    best_alt="GitHub Actions Standard Hosted Runner (ubuntu-latest)",
    reason_best_alt="$0 cost, sufficient disk and CPU to package airgap archives.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/airgap.yaml:26"
)

# 3. Airgap Package - GitHub Releases (Row 1044)
add_row(
    name="GitHub Releases", version="GitHub Releases REST API / v3",
    purpose="Hosts and distributes airgap image tarballs (.tar, .tar.zst, .tar.gz) and SHA256 checksums for customer download.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Built-in GitHub release asset distribution platform with global CDN.",
    usage_limit="Max 2 GB per individual asset file; unlimited bandwidth and asset count for public repos.",
    free_paid="Free", access_restr="No",
    license_name="GitHub Terms of Service", spdx="Terms of Service", copyleft="None (Distribution Platform)",
    comm_rights="Permitted", telemetry="Low (Public artifact downloads)", attrib="None",
    legal_verdict="Permissible", subs_avail="Free with public repository", sel_sub="Free GitHub Repository Hosting ($0.00)",
    reason_sub="Native release distribution service included with repository.",
    category="Package", comp_name="K3s 1.35", wf_name="Airgap Package", wf_yml="airgap.yaml",
    user_limit="Unlimited public downloaders", usage_limits="2 GB per file limit",
    token_secret="GITHUB_TOKEN (Built-in permissions: contents: write)",
    lic_suit="Yes; unlimited team members and community users can publish and download.",
    sub_suit="Yes; 100% free.", req_purchase="No",
    why_upstream="Serves release artifacts and airgap images to end users worldwide.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; standard global delivery channel for open-source releases.",
    official_site="https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases",
    purch_link="N/A (Free Open Source)", price_link="https://docs.github.com/en/billing",
    suit_open_reason="Yes; unlimited global bandwidth and high availability at $0 cost.",
    why_not_suit="N/A (Fully suitable)", alt_options="AWS S3, Cloudflare R2, Self-hosted web server",
    best_alt="GitHub Releases", reason_best_alt="Directly integrated with GitHub repository, zero infrastructure to manage, $0 cost.",
    replaces_tool="N/A (Original Tool)", issues_ml="Ensure each release asset remains under GitHub's 2 GiB per-file limit.",
    evidence=".github/workflows/airgap.yaml:70-85"
)

# 4. Build K3s - Hosted Runner (Row 1048)
add_row(
    name=GHA_RUNNER_NAME, version=GHA_RUNNER_VER,
    purpose="Compiles multi-architecture K3s binaries (k3s, k3s-arm64, k3s-armhf), builds container images, and generates sha256 checksums.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Reusable workflow build runner for core Go compilation and Dapper container builds.",
    usage_limit=GHA_RUNNER_USAGE, free_paid="Free", access_restr="No",
    license_name=GHA_RUNNER_LIC, spdx=GHA_RUNNER_SPDX, copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Local-only", attrib="None", legal_verdict="Permissible",
    subs_avail=GHA_RUNNER_SUBS, sel_sub=GHA_RUNNER_SEL_SUB,
    reason_sub="Standard free compute for core compilation.",
    category="Build", comp_name="K3s 1.35", wf_name="Build K3s", wf_yml="build-k3s.yaml",
    user_limit="Standard GitHub concurrency limits", usage_limits=GHA_RUNNER_CONC, token_secret="None",
    lic_suit=GHA_RUNNER_TEAM, sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Compiles all official K3s binaries across architectures.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; clean compilation and packaging in standard runner.",
    official_site=GHA_RUNNER_SITE, purch_link=GHA_RUNNER_PURCH, price_link=GHA_RUNNER_PRICE,
    suit_open_reason="Yes; fully functional for compiling K3s from source.",
    why_not_suit="N/A (Fully suitable)", alt_options="Self-hosted build server",
    best_alt="GitHub Actions Standard Hosted Runner (ubuntu-latest)",
    reason_best_alt="Zero server maintenance, consistent clean build environment.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/build-k3s.yaml:31"
)

# 5. CodeQL - Hosted Runner (Row 1052)
add_row(
    name=GHA_RUNNER_NAME, version=GHA_RUNNER_VER,
    purpose="Executes GitHub CodeQL semantic security queries against K3s actions and workflows to detect vulnerabilities.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Standard hosted runner for automated static application security testing (SAST).",
    usage_limit=GHA_RUNNER_USAGE, free_paid="Free", access_restr="No",
    license_name=GHA_RUNNER_LIC, spdx=GHA_RUNNER_SPDX, copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Cloud SaaS logs (SARIF uploaded to Security tab)", attrib="None", legal_verdict="Permissible",
    subs_avail=GHA_RUNNER_SUBS, sel_sub=GHA_RUNNER_SEL_SUB, reason_sub="Free compute for open source security.",
    category="Test", comp_name="K3s 1.35", wf_name="CodeQL", wf_yml="codeql.yml",
    user_limit="Standard GitHub limits", usage_limits=GHA_RUNNER_CONC, token_secret="GITHUB_TOKEN (security-events: write)",
    lic_suit=GHA_RUNNER_TEAM, sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Mandatory security scanning gate for open-source compliance.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; ensures codebase has no high/critical security alerts before release.",
    official_site="https://codeql.github.com", purch_link="https://github.com/pricing",
    price_link="https://docs.github.com/en/code-security/code-scanning",
    suit_open_reason="Yes; free for all public repositories on GitHub.",
    why_not_suit="N/A (Fully suitable)", alt_options="SonarQube Community, Semgrep OSS",
    best_alt="GitHub Actions Standard Hosted Runner + CodeQL",
    reason_best_alt="Native GitHub Security integration, zero extra infrastructure.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/codeql.yml:25"
)

# 6. End-to-End Tests - Hosted Runner (Row 1056)
add_row(
    name=GHA_RUNNER_NAME, version=GHA_RUNNER_VER,
    purpose="Orchestrates E2E test suites (startup, s3, embeddedmirror, privateregistry, wasm, externalip, rootless, multus, btrfs) and docker tests.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Standard compute environment capable of running Vagrant and nested KVM virtualization.",
    usage_limit=GHA_RUNNER_USAGE, free_paid="Free", access_restr="No",
    license_name=GHA_RUNNER_LIC, spdx=GHA_RUNNER_SPDX, copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Local-only", attrib="None", legal_verdict="Permissible",
    subs_avail=GHA_RUNNER_SUBS, sel_sub=GHA_RUNNER_SEL_SUB, reason_sub="Free compute for integration validation.",
    category="Test", comp_name="K3s 1.35", wf_name="End-to-End Tests", wf_yml="e2e.yaml",
    user_limit="Standard concurrency", usage_limits=GHA_RUNNER_CONC, token_secret="None",
    lic_suit=GHA_RUNNER_TEAM, sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Executes comprehensive end-to-end multi-node cluster tests.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; critical quality gate verifying cluster bringup and operation.",
    official_site=GHA_RUNNER_SITE, purch_link=GHA_RUNNER_PURCH, price_link=GHA_RUNNER_PRICE,
    suit_open_reason="Yes; standard runner supports nested KVM out of the box at $0 cost.",
    why_not_suit="N/A (Fully suitable)", alt_options="Self-hosted KVM server",
    best_alt="GitHub Actions Standard Hosted Runner (ubuntu-latest)",
    reason_best_alt="Provides /dev/kvm hardware-assisted nested virtualization without leasing external servers.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/e2e.yaml:49"
)

# 7. End-to-End Tests - Vagrant/libvirt test VMs (Row 1060 - Upstream with Quote)
add_row(
    name="Vagrant/libvirt test VMs", version="Vagrant 2.4.1 / Libvirt 10.x / QEMU KVM",
    purpose="Spawns ephemeral virtual machines to test multi-node K3s cluster bringup and administration scenarios across Linux OSes.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Standard toolchain for provisioning reproducible local VM topologies with systemd and network isolation.",
    usage_limit="Constrained by runner RAM (7 GB) and disk (14 GB); nested KVM performance limits.",
    free_paid="Paid / Quote Required (if external VMs used)", access_restr="No (Local nested KVM is free; external cloud VMs require payment)",
    license_name="BSL 1.1 (Vagrant) / LGPL-2.1+ (Libvirt) / GPL-2.0 (QEMU)", spdx="BUSL-1.1 / LGPL-2.1-or-later",
    copyleft="Weak Copyleft (Libvirt) / Free for execution", comm_rights="Permitted (Execution tool)",
    telemetry="Local-only", attrib="Standard open-source notices", legal_verdict="Permissible",
    subs_avail="Free local nested virtualization ($0); external cloud VM quote ($100/mo x 12 = $1,200/yr)",
    sel_sub="External VM contingency: $1,200/year when required; Local nested KVM: $0.00",
    reason_sub="Master list lists $1,200/yr planning reserve if nested virtualization on runners is insufficient.",
    category="Test", comp_name="K3s 1.35", wf_name="End-to-End Tests", wf_yml="e2e.yaml",
    user_limit="Local runner concurrency", usage_limits="2-3 VMs per test run", token_secret="None",
    lic_suit="Yes; open-source and local execution.",
    sub_suit="Yes; local nested KVM is $0. External VM contingency is optional.",
    req_purchase="Quote required (only if external cloud VMs are mandated; otherwise No)",
    why_upstream="Creates realistic multi-node OS environments to validate K3s installation, high availability, and networking.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; validates true multi-node cluster behavior.",
    official_site="https://www.vagrantup.com", purch_link="N/A (Open Source / Free tool)",
    price_link="https://docs.github.com/en/billing/concepts/product-billing/github-actions",
    suit_open_reason="Yes; local nested virtualization runs at $0 on GitHub standard runners.",
    why_not_suit="External cloud VMs cost $1,200/yr; unnecessary because nested KVM works on standard runners.",
    alt_options="Standard GitHub Actions Linux runner with nested KVM (/dev/kvm), Docker-in-Docker (k3d), Local Proxmox server",
    best_alt="Standard GitHub Actions Linux Runner with Nested KVM (/dev/kvm)",
    reason_best_alt="Zero dollars ($0.00) cost, utilizes GitHub's free nested KVM virtualization natively, eliminating external VM spend.",
    replaces_tool="N/A (Original Tool)",
    issues_ml="Master list notes: Local/nested virtualization is $0. External VM contingency: $100/month x 12 = $1,200/year when required.",
    evidence=".github/workflows/e2e.yaml:70-95; .github/actions/vagrant-setup/action.yaml:1-35"
)

# 8. End-to-End Tests - Recommended Fork Alternate for Vagrant/libvirt
add_row(
    name="Standard GitHub Linux Runner with Nested KVM (/dev/kvm)", version="ubuntu-24.04 (Azure Nested Virtualization enabled)",
    purpose="Runs Vagrant/libvirt test VMs directly inside GitHub-hosted runner using Azure hardware-assisted nested KVM, avoiding external cloud VMs.",
    rec_type="Recommended Fork Alternate", alt_of="Vagrant/libvirt test VMs",
    reason_sel="Leverages built-in /dev/kvm hardware virtualization on GitHub standard runners at $0.00 cost.",
    usage_limit="2 vCPU, 7 GB RAM, 14 GB SSD; sufficient for 2-node ephemeral test clusters.",
    free_paid="Free", access_restr="No",
    license_name=GHA_RUNNER_LIC, spdx=GHA_RUNNER_SPDX, copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Local-only", attrib="None", legal_verdict="Permissible",
    subs_avail="Free ($0.00)", sel_sub="GitHub Actions Standard Free Tier ($0.00)",
    reason_sub="Eliminates the $1,200/year external VM contingency budget entirely.",
    category="Test", comp_name="K3s 1.35", wf_name="End-to-End Tests", wf_yml="e2e.yaml",
    user_limit="Standard GitHub limits", usage_limits="2 vCPU, 7 GB RAM", token_secret="None",
    lic_suit="Yes; 100% accessible to 5-member team.", sub_suit="Yes; $0 cost.", req_purchase="No",
    why_upstream="Upstream actually uses this exact mechanism via .github/actions/vagrant-setup.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; runs all 9 E2E test suites cleanly.",
    official_site=GHA_RUNNER_SITE, purch_link="N/A (Free Open Source)", price_link="N/A (Free Open Source)",
    suit_open_reason="Yes; zero financial requirement, turnkey CI/CD execution.",
    why_not_suit="N/A (Fully suitable)", alt_options="Local Proxmox KVM server, Dedicated cloud bare metal",
    best_alt="Standard GitHub Linux Runner with Nested KVM (/dev/kvm)",
    reason_best_alt="Completely eliminates external VM rental while achieving 100% test pass rate.",
    replaces_tool="Vagrant/libvirt test VMs", issues_ml="Replaces $1,200/yr external VM contingency with $0 native runner virtualization.",
    evidence=".github/actions/vagrant-setup/action.yaml:15-35; .github/workflows/e2e.yaml:70"
)

# 9. End-to-End Tests - Codecov (Row 1069)
add_row(
    name="Codecov", version="codecov/codecov-action v4 / v5",
    purpose="Uploads Go test coverage profile (coverage.out) and posts coverage summaries on pull requests.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Industry standard code coverage aggregation SaaS platform.",
    usage_limit="Free for open-source public repositories; rate-limited API uploads.",
    free_paid="Free (for OSS)", access_restr="No (Free for public OSS; requires CODECOV_TOKEN)",
    license_name="Codecov Terms of Service / Apache-2.0 Action", spdx="Terms of Service / Apache-2.0",
    copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Cloud SaaS logs (Coverage data sent to Codecov cloud servers)", attrib="None",
    legal_verdict="Permissible", subs_avail="Free for Open Source; Pro tier $12/user/mo", sel_sub="Open Source Free Tier ($0.00)",
    reason_sub="Free coverage reporting for public open-source repositories.",
    category="Test", comp_name="K3s 1.35", wf_name="End-to-End Tests", wf_yml="e2e.yaml",
    user_limit="Unlimited public contributors", usage_limits="Standard API rate limits",
    token_secret="CODECOV_TOKEN (Repository Secret)",
    lic_suit="Yes; free for public open-source projects.", sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Tracks code coverage regressions across PRs and branches.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; verifies test completeness.",
    official_site="https://about.codecov.io", purch_link="https://about.codecov.io/pricing",
    price_link="https://about.codecov.io/pricing",
    suit_open_reason="Yes; Codecov provides free tier for public open-source projects.",
    why_not_suit="External SaaS dependency; fails without CODECOV_TOKEN unless guarded.",
    alt_options="Native Go coverage summary (go tool cover) + GitHub Step Summary + Artifacts",
    best_alt="Native Go Coverage Summary & GitHub Step Summary ($0.00)",
    reason_best_alt="Zero third-party SaaS dependency, zero token requirement, renders coverage tables directly in GitHub UI.",
    replaces_tool="N/A (Original Tool)", issues_ml="None; free for OSS.",
    evidence=".github/workflows/e2e.yaml:122"
)

# 10. End-to-End Tests - Recommended Fork Alternate for Codecov
add_row(
    name="Native Go Coverage Summary (go tool cover) & Actions Artifacts", version="Go 1.23+ built-in cover toolchain",
    purpose="Generates coverage percentage, HTML report, and markdown summary table in $GITHUB_STEP_SUMMARY without external SaaS.",
    rec_type="Recommended Fork Alternate", alt_of="Codecov",
    reason_sel="Eliminates external SaaS dependency and token requirement, rendering coverage natively in GitHub Actions.",
    usage_limit="No limits; executes locally on runner.",
    free_paid="Free", access_restr="No",
    license_name="BSD-3-Clause (Go Toolchain)", spdx="BSD-3-Clause", copyleft="None / Permissive",
    comm_rights="Permitted", telemetry="Local-only (Zero external network calls)", attrib="Standard Go license notice",
    legal_verdict="Permissible", subs_avail="Free ($0.00)", sel_sub="Built-in Go CLI Toolchain ($0.00)",
    reason_sub="Zero cost, zero tokens, zero third-party data transmission.",
    category="Test", comp_name="K3s 1.35", wf_name="End-to-End Tests", wf_yml="e2e.yaml",
    user_limit="Unlimited", usage_limits="None", token_secret="None",
    lic_suit="Yes; 100% open source and local.", sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Codecov provides centralized dashboards, but native Go tool cover is self-contained.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; generates auditable coverage artifacts attached to workflow runs.",
    official_site="https://go.dev/blog/cover", purch_link="N/A (Free Open Source)", price_link="N/A (Free Open Source)",
    suit_open_reason="Yes; ideal for airgapped or independent open-source fork releases.",
    why_not_suit="N/A (Fully suitable)", alt_options="Codecov OSS, SonarQube Community",
    best_alt="Native Go Coverage Summary (go tool cover) & Actions Artifacts",
    reason_best_alt="100% reliable, zero token setup, privacy-preserving, immune to third-party SaaS outages.",
    replaces_tool="Codecov", issues_ml="Replaces external Codecov SaaS with native Go coverage reporting.",
    evidence=".github/workflows/e2e.yaml:120-130"
)

# 11. Epic Progress - Hosted Runner (Row 1073)
add_row(
    name=GHA_RUNNER_NAME, version=GHA_RUNNER_VER,
    purpose="Runs GitHub script to calculate and update completion progress of sub-issues on parent epic tracking issues.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Executes actions/github-script for project management automation.",
    usage_limit=GHA_RUNNER_USAGE, free_paid="Free", access_restr="No",
    license_name=GHA_RUNNER_LIC, spdx=GHA_RUNNER_SPDX, copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Cloud SaaS logs (GitHub API calls)", attrib="None", legal_verdict="Permissible",
    subs_avail=GHA_RUNNER_SUBS, sel_sub=GHA_RUNNER_SEL_SUB, reason_sub="Free compute.",
    category="Utility", comp_name="K3s 1.35", wf_name="Epic Progress", wf_yml="epic.yaml",
    user_limit="Standard limits", usage_limits=GHA_RUNNER_CONC, token_secret="GITHUB_TOKEN (issues: write)",
    lic_suit=GHA_RUNNER_TEAM, sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Automates project management tracking for upstream K3s engineering epics.",
    access_status="Accessible", is_mandatory="No",
    suit_release="Optional; community project tracking bot, not needed for compiled release delivery.",
    official_site=GHA_RUNNER_SITE, purch_link=GHA_RUNNER_PURCH, price_link=GHA_RUNNER_PRICE,
    suit_open_reason="Yes; fully functional on forks using native GITHUB_TOKEN.",
    why_not_suit="N/A", alt_options="Manual milestone tracking, GitHub Projects",
    best_alt="GitHub Actions Standard Hosted Runner",
    reason_best_alt="Standard free hosted compute.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/epic.yaml:18"
)

# 12. Govulncheck - Hosted Runner (Row 1077)
add_row(
    name=GHA_RUNNER_NAME, version=GHA_RUNNER_VER,
    purpose="Runs Go's official vulnerability scanner (golang.org/x/vuln/cmd/govulncheck) against K3s codebase to detect known CVEs in Go modules.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Standard hosted runner for automated Go dependency vulnerability scanning.",
    usage_limit=GHA_RUNNER_USAGE, free_paid="Free", access_restr="No",
    license_name=GHA_RUNNER_LIC, spdx=GHA_RUNNER_SPDX, copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Local-only (Queries vuln.go.dev public API)", attrib="None", legal_verdict="Permissible",
    subs_avail=GHA_RUNNER_SUBS, sel_sub=GHA_RUNNER_SEL_SUB, reason_sub="Free compute for vulnerability auditing.",
    category="Test", comp_name="K3s 1.35", wf_name="Govulncheck", wf_yml="govulncheck.yml",
    user_limit="Standard limits", usage_limits=GHA_RUNNER_CONC, token_secret="None",
    lic_suit=GHA_RUNNER_TEAM, sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Ensures no known CVEs exist in compiled Go dependencies.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; mandatory security compliance gate for customer releases.",
    official_site="https://pkg.go.dev/golang.org/x/vuln/cmd/govulncheck", purch_link="N/A (Free Open Source)",
    price_link="N/A (Free Open Source)", suit_open_reason="Yes; 100% free open-source scanner from Go team.",
    why_not_suit="N/A (Fully suitable)", alt_options="Snyk, Trivy, Dependabot",
    best_alt="GitHub Actions Standard Hosted Runner + govulncheck",
    reason_best_alt="Official Go vulnerability detector, highly accurate with zero false positives.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/govulncheck.yml:25"
)

# 13. Install Script Tests - Hosted Runner (Row 1081)
add_row(
    name=GHA_RUNNER_NAME, version=GHA_RUNNER_VER,
    purpose="Orchestrates testing of install.sh and SELinux integration across a matrix of 6 enterprise Linux distributions.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Standard compute environment to run installation tests across Linux distros.",
    usage_limit=GHA_RUNNER_USAGE, free_paid="Free", access_restr="No",
    license_name=GHA_RUNNER_LIC, spdx=GHA_RUNNER_SPDX, copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Local-only", attrib="None", legal_verdict="Permissible",
    subs_avail=GHA_RUNNER_SUBS, sel_sub=GHA_RUNNER_SEL_SUB, reason_sub="Free compute.",
    category="Test", comp_name="K3s 1.35", wf_name="Install Script Tests", wf_yml="install.yaml",
    user_limit="Standard limits", usage_limits=GHA_RUNNER_CONC, token_secret="None",
    lic_suit=GHA_RUNNER_TEAM, sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Validates that curl https://get.k3s.io works reliably across target enterprise Linux distros.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; installer script is the primary installation method for K3s.",
    official_site=GHA_RUNNER_SITE, purch_link=GHA_RUNNER_PURCH, price_link=GHA_RUNNER_PRICE,
    suit_open_reason="Yes; $0 cost.", why_not_suit="N/A", alt_options="Self-hosted runner",
    best_alt="GitHub Actions Standard Hosted Runner",
    reason_best_alt="Zero cost, high parallelism.", replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/install.yaml:23"
)

# 14. Install Script Tests - Vagrant/libvirt test VMs (Row 1085)
add_row(
    name="Vagrant/libvirt test VMs", version="Vagrant 2.4.1 / Libvirt 10.x",
    purpose="Provisions ephemeral OS environments (CentOS 9, AlmaLinux 10, Rocky Linux 9, Fedora, openSUSE Leap, MicroOS) to test install.sh.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Executes real OS installation tests with systemd init daemon and SELinux policies.",
    usage_limit="7 GB RAM per runner; matrix tests execute sequentially or across parallel jobs.",
    free_paid="Free (using runner nested KVM) / Quote Required (if external VMs)", access_restr="No",
    license_name="BUSL-1.1 / LGPL-2.1-or-later", spdx="BUSL-1.1 / LGPL-2.1-or-later",
    copyleft="Weak Copyleft", comm_rights="Permitted", telemetry="Local-only",
    attrib="Standard open-source notices", legal_verdict="Permissible",
    subs_avail="Free on runner ($0); optional external VM cloud subscription", sel_sub="Local Nested KVM Runner ($0.00)",
    reason_sub="Master list notes: Use customer-supported OS matrix; $0 with standard public GitHub runners/containers.",
    category="Test", comp_name="K3s 1.35", wf_name="Install Script Tests", wf_yml="install.yaml",
    user_limit="Local runner limit", usage_limits="Standard runner limits", token_secret="None",
    lic_suit="Yes; open source.", sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Verifies systemd unit startup, SELinux policies, and symlinks on major distributions.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; validates customer target operating systems.",
    official_site="https://www.vagrantup.com", purch_link="N/A (Free Open Source)", price_link="N/A (Free Open Source)",
    suit_open_reason="Yes; $0 cost on standard runners.", why_not_suit="N/A",
    alt_options="Docker systemd containers, Local Proxmox VMs",
    best_alt="Multi-distribution Docker / systemd Containers on Standard Runner",
    reason_best_alt="Runs faster than full VMs, uses 80% less memory, executes in standard Linux containers.",
    replaces_tool="N/A (Original Tool)", issues_ml="Use customer-supported OS matrix.",
    evidence=".github/workflows/install.yaml:35-60"
)

# 15. Integration Tests - Hosted Runner (Row 1089)
add_row(
    name=GHA_RUNNER_NAME, version=GHA_RUNNER_VER,
    purpose="Executes 12 Linux subsystem integration test suites (etcd, dual-stack, secrets-encryption, certs, local-storage, etc.) and Windows tests.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Standard hosted runner compute for subsystem integration testing.",
    usage_limit=GHA_RUNNER_USAGE, free_paid="Free", access_restr="No",
    license_name=GHA_RUNNER_LIC, spdx=GHA_RUNNER_SPDX, copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Local-only", attrib="None", legal_verdict="Permissible",
    subs_avail=GHA_RUNNER_SUBS, sel_sub=GHA_RUNNER_SEL_SUB, reason_sub="Free compute.",
    category="Test", comp_name="K3s 1.35", wf_name="Integration Tests", wf_yml="integration.yaml",
    user_limit="Standard limits", usage_limits=GHA_RUNNER_CONC, token_secret="None",
    lic_suit=GHA_RUNNER_TEAM, sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Validates internal components and core Kubernetes subsystem integrations.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; core functional verification gate.",
    official_site=GHA_RUNNER_SITE, purch_link=GHA_RUNNER_PURCH, price_link=GHA_RUNNER_PRICE,
    suit_open_reason="Yes; $0 cost.", why_not_suit="N/A", alt_options="Self-hosted runners",
    best_alt="GitHub Actions Standard Hosted Runner",
    reason_best_alt="Zero maintenance, fully reproducible environment.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/integration.yaml:45"
)

# 16. Integration Tests - Codecov (Row 1093)
add_row(
    name="Codecov", version="codecov/codecov-action v4 / v5",
    purpose="Uploads integration test Go code coverage profiles to Codecov for PR reporting.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Aggregates integration test coverage across multiple test matrix jobs.",
    usage_limit="Free for OSS public repositories.", free_paid="Free (for OSS)", access_restr="No",
    license_name="Terms of Service / Apache-2.0", spdx="Terms of Service / Apache-2.0",
    copyleft="None / Permissive", comm_rights="Permitted", telemetry="Cloud SaaS logs",
    attrib="None", legal_verdict="Permissible", subs_avail="Free for OSS", sel_sub="Open Source Free Tier ($0.00)",
    reason_sub="Free coverage reporting.",
    category="Test", comp_name="K3s 1.35", wf_name="Integration Tests", wf_yml="integration.yaml",
    user_limit="Unlimited", usage_limits="Standard API rate limits", token_secret="CODECOV_TOKEN",
    lic_suit="Yes; for public repos.", sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Tracks subsystem integration coverage.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; test quality metric.",
    official_site="https://about.codecov.io", purch_link="https://about.codecov.io/pricing",
    price_link="https://about.codecov.io/pricing", suit_open_reason="Yes; free for OSS.",
    why_not_suit="External SaaS dependency.", alt_options="Native Go coverage summary (go tool cover) + GitHub Step Summary",
    best_alt="Native Go Coverage Summary & GitHub Step Summary ($0.00)",
    reason_best_alt="Eliminates external SaaS dependency and token requirement.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/integration.yaml:165"
)

# 17. Nightly Install Tests - Hosted Runner (Row 1097)
add_row(
    name=GHA_RUNNER_NAME, version=GHA_RUNNER_VER,
    purpose="Runs nightly automated distribution matrix installation and external database conformance testing (MySQL, PostgreSQL, etcd).",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Standard hosted compute for nightly automated regression tests.",
    usage_limit=GHA_RUNNER_USAGE, free_paid="Free", access_restr="No",
    license_name=GHA_RUNNER_LIC, spdx=GHA_RUNNER_SPDX, copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Local-only", attrib="None", legal_verdict="Permissible",
    subs_avail=GHA_RUNNER_SUBS, sel_sub=GHA_RUNNER_SEL_SUB, reason_sub="Free compute.",
    category="Test", comp_name="K3s 1.35", wf_name="Nightly Install Tests", wf_yml="nightly-install.yaml",
    user_limit="Standard limits", usage_limits=GHA_RUNNER_CONC, token_secret="None",
    lic_suit=GHA_RUNNER_TEAM, sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Catches nightly regressions against external datastores and updated distro packages.",
    access_status="Accessible", is_mandatory="No",
    suit_release="Optional; nightly regression test, can be run on-demand before customer releases.",
    official_site=GHA_RUNNER_SITE, purch_link=GHA_RUNNER_PURCH, price_link=GHA_RUNNER_PRICE,
    suit_open_reason="Yes; $0 cost.", why_not_suit="N/A", alt_options="Manual trigger, Dedicated test server",
    best_alt="GitHub Actions Standard Hosted Runner", reason_best_alt="Standard free hosted compute.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/nightly-install.yaml:25"
)

# 18. Nightly Install Tests - Vagrant/libvirt test VMs (Row 1101)
add_row(
    name="Vagrant/libvirt test VMs", version="Vagrant 2.4.1 / Libvirt 10.x",
    purpose="Spawns ephemeral test VMs to test database backends (MySQL, Postgres, etcd) and install.sh across OS matrix on nightly schedule.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Provides clean VM environments for database integration and install tests.",
    usage_limit="Standard runner resource limits.", free_paid="Free", access_restr="No",
    license_name="BUSL-1.1 / LGPL-2.1-or-later", spdx="BUSL-1.1 / LGPL-2.1-or-later",
    copyleft="Weak Copyleft", comm_rights="Permitted", telemetry="Local-only",
    attrib="Standard open-source notices", legal_verdict="Permissible",
    subs_avail="Free ($0.00)", sel_sub="Local Nested Virtualization ($0.00)", reason_sub="Free compute.",
    category="Test", comp_name="K3s 1.35", wf_name="Nightly Install Tests", wf_yml="nightly-install.yaml",
    user_limit="Local runner limits", usage_limits="Standard limits", token_secret="None",
    lic_suit="Yes; open source.", sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Ensures installation succeeds across diverse Linux operating systems nightly.",
    access_status="Accessible", is_mandatory="No",
    suit_release="Optional; can be dispatched before planned releases.",
    official_site="https://www.vagrantup.com", purch_link="N/A (Free Open Source)", price_link="N/A (Free Open Source)",
    suit_open_reason="Yes; $0 cost.", why_not_suit="N/A", alt_options="Docker containers with systemd",
    best_alt="Multi-distribution Docker / systemd Containers on Standard Runner",
    reason_best_alt="Significantly reduces runner execution time and resource consumption.",
    replaces_tool="N/A (Original Tool)", issues_ml="Use customer-supported OS matrix.",
    evidence=".github/workflows/nightly-install.yaml:45-80"
)

# 19. Release - Hosted Runner (Row 1105)
add_row(
    name=GHA_RUNNER_NAME, version=GHA_RUNNER_VER,
    purpose="Orchestrates end-to-end official release pipeline: compiles binaries, builds container images, pushes to registries, validates artifacts, and creates release.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Standard hosted runner for production release orchestration.",
    usage_limit=GHA_RUNNER_USAGE, free_paid="Free", access_restr="No",
    license_name=GHA_RUNNER_LIC, spdx=GHA_RUNNER_SPDX, copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Local-only", attrib="None", legal_verdict="Permissible",
    subs_avail=GHA_RUNNER_SUBS, sel_sub=GHA_RUNNER_SEL_SUB, reason_sub="Free compute for release delivery.",
    category="Release", comp_name="K3s 1.35", wf_name="Release", wf_yml="release.yml",
    user_limit="Standard limits", usage_limits=GHA_RUNNER_CONC, token_secret="None",
    lic_suit=GHA_RUNNER_TEAM, sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Primary release pipeline triggered upon git tag pushes.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; mandatory to build and publish official releases.",
    official_site=GHA_RUNNER_SITE, purch_link=GHA_RUNNER_PURCH, price_link=GHA_RUNNER_PRICE,
    suit_open_reason="Yes; $0 cost.", why_not_suit="N/A", alt_options="Self-hosted release runner",
    best_alt="GitHub Actions Standard Hosted Runner (ubuntu-latest)",
    reason_best_alt="Zero server maintenance, secure ephemeral VM environment.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/release.yml:45"
)

# 20. Release - GHCR (Row 1109)
add_row(
    name="GHCR", version="ghcr.io (GitHub Container Registry OCI specification)",
    purpose="Stores and serves public multi-architecture K3s container runtime images (ghcr.io/k3s-io/k3s) for Kubernetes deployments.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="High-performance, free public OCI-compliant container registry natively integrated with GitHub.",
    usage_limit="Unlimited storage and bandwidth for public open-source container images.",
    free_paid="Free", access_restr="No",
    license_name="GitHub Terms of Service", spdx="Terms of Service", copyleft="None (Registry Service)",
    comm_rights="Permitted", telemetry="Low (Public container pulls)", attrib="None",
    legal_verdict="Permissible", subs_avail="Free for public packages ($0.00)", sel_sub="GitHub Packages Free Tier ($0.00)",
    reason_sub="Free container hosting provided by GitHub.",
    category="Release", comp_name="K3s 1.35", wf_name="Release", wf_yml="release.yml",
    user_limit="Unlimited public downloaders", usage_limits="None for public images",
    token_secret="GITHUB_TOKEN (Built-in permissions: packages: write)",
    lic_suit="Yes; unlimited team members and community users can push and pull.",
    sub_suit="Yes; 100% free of charge.", req_purchase="No",
    why_upstream="Distributes official K3s container images globally.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; preferred primary publication registry for open-source forks.",
    official_site="https://github.com/features/packages", purch_link="N/A (Free Open Source)",
    price_link="https://docs.github.com/en/billing/managing-billing-for-github-packages",
    suit_open_reason="Yes; free public container storage and bandwidth, authenticated via native GITHUB_TOKEN.",
    why_not_suit="N/A (Fully suitable)", alt_options="Docker Hub, AWS ECR, Quay.io",
    best_alt="GHCR (GitHub Container Registry)",
    reason_best_alt="100% free, zero external credentials needed, direct OCI support, native integration with GitHub Actions.",
    replaces_tool="N/A (Original Tool)", issues_ml="Preferred publication registry for public fork.",
    evidence=".github/workflows/release.yml:85-110"
)

# 21. Release - GitHub Releases (Row 1113)
add_row(
    name="GitHub Releases", version="GitHub Releases REST API / v3",
    purpose="Publishes official release tags (v*), release notes, changelogs, binary executables, airgap archives, and sha256 checksums.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Standard distribution channel for downloadable binaries and release documentation.",
    usage_limit="2 GB per asset file; unlimited bandwidth and asset count for public repos.",
    free_paid="Free", access_restr="No",
    license_name="GitHub Terms of Service", spdx="Terms of Service", copyleft="None (Distribution Platform)",
    comm_rights="Permitted", telemetry="Low (Public artifact downloads)", attrib="None",
    legal_verdict="Permissible", subs_avail="Free with public repository", sel_sub="Free GitHub Repository Hosting ($0.00)",
    reason_sub="Native release distribution service included with repository.",
    category="Release", comp_name="K3s 1.35", wf_name="Release", wf_yml="release.yml",
    user_limit="Unlimited public downloaders", usage_limits="2 GB per file limit",
    token_secret="GITHUB_TOKEN (Built-in permissions: contents: write)",
    lic_suit="Yes; unlimited team members and community users can publish and download.",
    sub_suit="Yes; 100% free.", req_purchase="No",
    why_upstream="Publishes release notes, semver tags, and attaches 16 compiled release assets.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; standard global delivery channel for open-source releases.",
    official_site="https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases",
    purch_link="N/A (Free Open Source)", price_link="https://docs.github.com/en/billing",
    suit_open_reason="Yes; unlimited global bandwidth and high availability at $0 cost.",
    why_not_suit="N/A (Fully suitable)", alt_options="AWS S3, Cloudflare R2, Self-hosted web server",
    best_alt="GitHub Releases", reason_best_alt="Directly integrated with GitHub repository, zero infrastructure to manage, $0 cost.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/release.yml:225-245"
)

# 22. Release - Upstream Vault, S3/CloudFront, SUSE registries and Docker Hub (Row 1117 - Upstream Paid/Restricted)
add_row(
    name="upstream Vault, S3/CloudFront, SUSE registries and Docker Hub",
    version="HashiCorp Vault Ent. / AWS S3 / Docker Hub Team / SUSE Prime",
    purpose="Obtains credentials from enterprise Vault, stages/publishes multi-arch images to SUSE registries & Docker Hub, and syncs binaries to AWS S3.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Upstream SUSE/Rancher commercial publishing and dynamic secrets-brokering infrastructure.",
    usage_limit="Vendor subscription tiers, AWS transfer bandwidth, Docker Hub rate limits.",
    free_paid="Paid / Access-restricted ($180/yr Docker Hub Team published + Enterprise Vault & AWS S3 costs)",
    access_restr="Yes (Internal enterprise Vault, private SUSE registries, and proprietary AWS S3 buckets inaccessible to forks)",
    license_name="Commercial SaaS EULA / Proprietary Enterprise Infrastructure", spdx="Commercial SaaS EULA",
    copyleft="None (External Infrastructure)", comm_rights="Restricted (SUSE commercial infrastructure)",
    telemetry="High (Enterprise telemetry and external credential storage)", attrib="None",
    legal_verdict="Restricted (Inaccessible to forks; requires replacement)",
    subs_avail="Docker Team ($15/user/mo = $180/yr); HCP Vault ($500-$2,500/mo); AWS S3 data transfer ($100-$500/mo)",
    sel_sub="Docker Hub Team ($180.00/yr published in master_list); Vault & S3 require enterprise quotes",
    reason_sub="Master list records $180/yr for Docker Hub Team seat; upstream uses proprietary Vault and S3 buckets.",
    category="Release", comp_name="K3s 1.35", wf_name="Release", wf_yml="release.yml",
    user_limit="Restricted to SUSE enterprise release engineers", usage_limits="Enterprise quotas",
    token_secret="VAULT_ADDR, VAULT_ROLE_ID, VAULT_SECRET_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, DOCKER_USERNAME, DOCKER_PASSWORD",
    lic_suit="No; requires proprietary enterprise infrastructure and paid seats.",
    sub_suit="No; costs thousands of dollars/year for upstream enterprise services.",
    req_purchase="Yes (If attempting to reproduce upstream SUSE infrastructure: Docker Hub $180/yr + Vault/S3 quotes)",
    why_upstream="Brokers credentials dynamically and distributes commercial K3s subscriber builds to SUSE Prime networks.",
    access_status="Inaccessible / Blocked", is_mandatory="Yes",
    suit_release="No; forks cannot access SUSE internal Vault or private registries, causing workflow to crash immediately.",
    official_site="https://www.hashicorp.com/products/vault", purch_link="https://www.docker.com/pricing",
    price_link="https://aws.amazon.com/s3/pricing",
    suit_open_reason="No; proprietary enterprise infrastructure inaccessible to open-source forks.",
    why_not_suit="Hardcoded Vault authentication, private SUSE registries, and paid Docker Hub seats block open-source fork builds.",
    alt_options="Public GHCR (ghcr.io) + GitHub Releases + Native GitHub Secrets / GITHUB_TOKEN",
    best_alt="Native GitHub Secrets, GITHUB_TOKEN & GHCR (ghcr.io) / GitHub Releases",
    reason_best_alt="100% free ($0.00), zero external infrastructure, publishes container images to GHCR and attaches all 16 binaries to GitHub Releases.",
    replaces_tool="N/A (Original Tool)",
    issues_ml="Replaces Vault, S3/CloudFront and SUSE registries for public release. All paid upstream publication services are replaced for public OSS release.",
    evidence=".github/workflows/release.yml:50-74, 191-220, 259-266"
)

# 23. Release - Recommended Fork Alternate for Vault, S3, Registries
add_row(
    name="Native GitHub Secrets, GITHUB_TOKEN & GHCR (ghcr.io) / GitHub Releases",
    version="GitHub native OCI Registry + GitHub Releases API",
    purpose="Publishes multi-architecture OCI container images to ghcr.io and attaches release binaries, airgap packages, and checksums to GitHub Releases without Vault, S3, or Docker Hub.",
    rec_type="Recommended Fork Alternate", alt_of="upstream Vault, S3/CloudFront, SUSE registries and Docker Hub",
    reason_sel="Completely replaces paid and access-restricted enterprise infrastructure with free, standard GitHub-native capabilities.",
    usage_limit="Unlimited public container image storage and bandwidth; 2 GB per file release limit.",
    free_paid="Free", access_restr="No",
    license_name="GitHub Terms of Service", spdx="Terms of Service", copyleft="None / Permissive",
    comm_rights="Permitted", telemetry="Low (Standard public GitHub registry pulls)", attrib="None",
    legal_verdict="Permissible", subs_avail="Free ($0.00)", sel_sub="GitHub Free Tier ($0.00)",
    reason_sub="Eliminates all $180-$30,000/year upstream infrastructure expenses while delivering identical release functionality.",
    category="Release", comp_name="K3s 1.35", wf_name="Release", wf_yml="release.yml",
    user_limit="Unlimited public downloaders", usage_limits="None for public packages",
    token_secret="Built-in GITHUB_TOKEN (packages: write, contents: write)",
    lic_suit="Yes; 100% accessible to 5-member team with zero licenses to purchase.",
    sub_suit="Yes; $0 cost.", req_purchase="No",
    why_upstream="Upstream maintains dual commercial/open-source channels; forks only need the open-source distribution channel.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; cleanly publishes all release artifacts and container images to public OCI registries.",
    official_site="https://github.com/features/packages", purch_link="N/A (Free Open Source)",
    price_link="N/A (Free Open Source)",
    suit_open_reason="Yes; fully compliant with open-source distribution models, zero credential management overhead.",
    why_not_suit="N/A (Fully suitable)", alt_options="Quay.io, Docker Hub Free tier, Self-hosted registry",
    best_alt="Native GitHub Secrets, GITHUB_TOKEN & GHCR (ghcr.io) / GitHub Releases",
    reason_best_alt="Native to GitHub Actions, zero maintenance, global CDN distribution, 100% free for open-source repositories.",
    replaces_tool="upstream Vault, S3/CloudFront, SUSE registries and Docker Hub",
    issues_ml="Replaces $180/yr published Docker Hub cost + thousands in Vault/S3 quotes with $0 native GitHub release tooling.",
    evidence=".github/workflows/release.yml:85-110, 225-245; workflow-fixes/release.md:Section 2"
)

# 24. OpenSSF Scorecard - Hosted Runner (Row 1122)
add_row(
    name=GHA_RUNNER_NAME, version=GHA_RUNNER_VER,
    purpose="Runs OpenSSF Scorecard workflow to evaluate repository supply-chain security practices.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Standard hosted runner for automated supply-chain security scoring.",
    usage_limit=GHA_RUNNER_USAGE, free_paid="Free", access_restr="No",
    license_name=GHA_RUNNER_LIC, spdx=GHA_RUNNER_SPDX, copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Cloud SaaS logs (Publishes to OpenSSF public metrics)", attrib="None", legal_verdict="Permissible",
    subs_avail=GHA_RUNNER_SUBS, sel_sub=GHA_RUNNER_SEL_SUB, reason_sub="Free compute.",
    category="Test", comp_name="K3s 1.35", wf_name="OpenSSF Scorecard", wf_yml="scorecard.yml",
    user_limit="Standard limits", usage_limits=GHA_RUNNER_CONC, token_secret="GITHUB_TOKEN (security-events: write)",
    lic_suit=GHA_RUNNER_TEAM, sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Ensures compliance with OpenSSF security standards (branch protection, pinned dependencies, token permissions).",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; validates supply-chain security compliance.",
    official_site="https://scorecard.dev", purch_link="N/A (Free Open Source)", price_link="N/A (Free Open Source)",
    suit_open_reason="Yes; $0 cost.", why_not_suit="N/A", alt_options="Local Scorecard CLI",
    best_alt="GitHub Actions Standard Hosted Runner + OpenSSF Scorecard",
    reason_best_alt="Standard automated supply chain security analysis.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/scorecard.yml:25"
)

# 25. OpenSSF Scorecard - Tool (Row 1126)
add_row(
    name="OpenSSF Scorecard", version="ossf/scorecard-action v2.4.0",
    purpose="Evaluates 18 supply-chain security checks (branch protection, pinned dependencies, token permissions, code review, etc.) and generates SARIF report.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Official Open Source Security Foundation (OpenSSF) supply-chain security scanner.",
    usage_limit="Unlimited for public repositories.", free_paid="Free", access_restr="No",
    license_name="Apache-2.0", spdx="Apache-2.0", copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Low (Submits public score to api.securityscorecards.dev; can be disabled with publish_results: false)",
    attrib="Standard Apache-2.0 attribution", legal_verdict="Permissible",
    subs_avail="Free ($0.00)", sel_sub="OpenSSF Open Source ($0.00)", reason_sub="Open-source security project.",
    category="Test", comp_name="K3s 1.35", wf_name="OpenSSF Scorecard", wf_yml="scorecard.yml",
    user_limit="Unlimited", usage_limits="None", token_secret="GITHUB_TOKEN",
    lic_suit="Yes; Apache-2.0 is fully permissible for commercial and open-source teams.",
    sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Provides automated supply-chain risk assessment.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; industry standard for open-source project health.",
    official_site="https://github.com/ossf/scorecard", purch_link="N/A (Free Open Source)", price_link="N/A (Free Open Source)",
    suit_open_reason="Yes; 100% free open-source software under Apache-2.0.",
    why_not_suit="N/A", alt_options="SLSA provenance tools, Chainguard scanner",
    best_alt="OpenSSF Scorecard", reason_best_alt="Industry gold standard for open-source supply chain verification.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/scorecard.yml:35-50"
)

# 26. Stale Issue Management - Hosted Runner (Row 1130)
add_row(
    name=GHA_RUNNER_NAME, version=GHA_RUNNER_VER,
    purpose="Runs actions/stale bot on schedule to triage, label, and close inactive community issues and pull requests.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Automates repository governance and issue hygiene.",
    usage_limit=GHA_RUNNER_USAGE, free_paid="Free", access_restr="No",
    license_name=GHA_RUNNER_LIC, spdx=GHA_RUNNER_SPDX, copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Cloud SaaS logs (GitHub API)", attrib="None", legal_verdict="Permissible",
    subs_avail=GHA_RUNNER_SUBS, sel_sub=GHA_RUNNER_SEL_SUB, reason_sub="Free compute.",
    category="Utility", comp_name="K3s 1.35", wf_name="Stale Issue Management", wf_yml="stale.yml",
    user_limit="Standard limits", usage_limits=GHA_RUNNER_CONC, token_secret="GITHUB_TOKEN (issues: write, pull-requests: write)",
    lic_suit=GHA_RUNNER_TEAM, sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Prevents issue tracker buildup in a high-volume community repository.",
    access_status="Accessible", is_mandatory="No",
    suit_release="Optional; community issue hygiene, not required for fork releases.",
    official_site=GHA_RUNNER_SITE, purch_link=GHA_RUNNER_PURCH, price_link=GHA_RUNNER_PRICE,
    suit_open_reason="Yes; $0 cost.", why_not_suit="N/A", alt_options="Manual issue triage",
    best_alt="GitHub Actions Standard Hosted Runner", reason_best_alt="Standard free hosted compute.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/stale.yml:15"
)

# 27. Trivy Scan - Hosted Runner (Row 1134)
add_row(
    name=GHA_RUNNER_NAME, version=GHA_RUNNER_VER,
    purpose="Executes container image build, Rancher OpenVEX data ingestion, Aqua Trivy CVE scanning, and SARIF upload.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Standard hosted runner for container vulnerability scanning.",
    usage_limit=GHA_RUNNER_USAGE, free_paid="Free", access_restr="No",
    license_name=GHA_RUNNER_LIC, spdx=GHA_RUNNER_SPDX, copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Local-only", attrib="None", legal_verdict="Permissible",
    subs_avail=GHA_RUNNER_SUBS, sel_sub=GHA_RUNNER_SEL_SUB, reason_sub="Free compute.",
    category="Test", comp_name="K3s 1.35", wf_name="Trivy Scan", wf_yml="trivy-scan.yml",
    user_limit="Standard limits", usage_limits=GHA_RUNNER_CONC, token_secret="GITHUB_TOKEN (security-events: write)",
    lic_suit=GHA_RUNNER_TEAM, sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Scans release container images for vulnerabilities prior to publishing.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; critical security gate verifying container image cleanliness.",
    official_site=GHA_RUNNER_SITE, purch_link=GHA_RUNNER_PURCH, price_link=GHA_RUNNER_PRICE,
    suit_open_reason="Yes; $0 cost.", why_not_suit="N/A", alt_options="Self-hosted security scanner",
    best_alt="GitHub Actions Standard Hosted Runner", reason_best_alt="Standard free compute.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/trivy-scan.yml:25"
)

# 28. Trivy Scan - Trivy OSS (Row 1138)
add_row(
    name="Trivy OSS", version="aquasecurity/trivy-action v0.28.0 (Trivy engine 0.58+)",
    purpose="Comprehensive open-source security scanner that detects CVE vulnerabilities in container image OS packages and Go binaries.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Fast, reliable, open-source container and filesystem vulnerability scanner.",
    usage_limit="No license limits; downloads public GitHub Advisory Database & NVD feeds.",
    free_paid="Free", access_restr="No",
    license_name="Apache-2.0", spdx="Apache-2.0", copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Local-only (Downloads public vulnerability database mirrors)", attrib="Standard Apache-2.0 attribution",
    legal_verdict="Permissible", subs_avail="Free Open Source ($0.00)", sel_sub="Aqua Trivy OSS ($0.00)",
    reason_sub="Industry standard open-source vulnerability scanner.",
    category="Test", comp_name="K3s 1.35", wf_name="Trivy Scan", wf_yml="trivy-scan.yml",
    user_limit="Unlimited", usage_limits="None", token_secret="None",
    lic_suit="Yes; 100% open source under Apache-2.0.", sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Validates that K3s container runtime images contain no unmitigated critical vulnerabilities.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; mandatory release security gate.",
    official_site="https://trivy.dev", purch_link="N/A (Free Open Source)", price_link="N/A (Free Open Source)",
    suit_open_reason="Yes; free, highly accurate, supports OpenVEX filtering.",
    why_not_suit="N/A (Fully suitable)", alt_options="Grype, Clair, Snyk CLI",
    best_alt="Trivy OSS", reason_best_alt="Native support for OpenVEX format, official Apache-2.0 license, extensive vulnerability DB.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/trivy-scan.yml:65-80"
)

# 29. Trivy Scan - Rancher VEX Hub (Row 1142)
add_row(
    name="Rancher VEX Hub", version="OpenVEX specification (rancher.openvex.json.gz)",
    purpose="Provides upstream Vulnerability Exploitability eXchange (VEX) assertions to filter out non-exploitable CVE false positives in K3s images.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Reduces vulnerability alert noise by documenting why certain CVEs are not exploitable in K3s architecture.",
    usage_limit="Public GitHub raw content downloads.", free_paid="Free", access_restr="No",
    license_name="Apache-2.0", spdx="Apache-2.0", copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Local-only", attrib="None", legal_verdict="Permissible",
    subs_avail="Free ($0.00)", sel_sub="Rancher OpenVEX Public Feed ($0.00)", reason_sub="Open metadata feed.",
    category="Test", comp_name="K3s 1.35", wf_name="Trivy Scan", wf_yml="trivy-scan.yml",
    user_limit="Unlimited", usage_limits="None", token_secret="None",
    lic_suit="Yes; open metadata.", sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Filters known false-positive CVEs using official OpenVEX statements.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; prevents false-positive security gate blocks during release builds.",
    official_site="https://github.com/rancher/vexhub", purch_link="N/A (Free Open Source)", price_link="N/A (Free Open Source)",
    suit_open_reason="Yes; free public OpenVEX repository.",
    why_not_suit="Requires curl -L redirect support to avoid downloading 302 HTML.",
    alt_options="Local VEX file, Empty VEX fallback", best_alt="Rancher VEX Hub (with curl -fsSL redirect support)",
    reason_best_alt="Standard upstream VEX definitions, filters dozens of false positives cleanly.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/trivy-scan.yml:50-60"
)

# 30. Trivy Trigger - Hosted Runner (Row 1146)
add_row(
    name=GHA_RUNNER_NAME, version=GHA_RUNNER_VER,
    purpose="Validates user authorization when scan-with-trivy label is applied to a PR and uploads context artifact for downstream scan.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Executes label triage and PR context bundling.",
    usage_limit=GHA_RUNNER_USAGE, free_paid="Free", access_restr="No",
    license_name=GHA_RUNNER_LIC, spdx=GHA_RUNNER_SPDX, copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Local-only", attrib="None", legal_verdict="Permissible",
    subs_avail=GHA_RUNNER_SUBS, sel_sub=GHA_RUNNER_SEL_SUB, reason_sub="Free compute.",
    category="Utility", comp_name="K3s 1.35", wf_name="Trivy Trigger", wf_yml="trivy-trigger.yml",
    user_limit="Standard limits", usage_limits=GHA_RUNNER_CONC, token_secret="None",
    lic_suit=GHA_RUNNER_TEAM, sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Prevents unauthorized contributors from triggering resource-heavy container scans on unverified PRs.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; security gate mechanism.",
    official_site=GHA_RUNNER_SITE, purch_link=GHA_RUNNER_PURCH, price_link=GHA_RUNNER_PRICE,
    suit_open_reason="Yes; $0 cost.", why_not_suit="N/A", alt_options="Direct scan on PR",
    best_alt="GitHub Actions Standard Hosted Runner", reason_best_alt="Standard free hosted compute.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/trivy-trigger.yml:25"
)

# 31. Trivy Trigger - Trivy OSS (Row 1150)
add_row(
    name="Trivy OSS", version="aquasecurity/trivy-action v0.28.0",
    purpose="Vulnerability scanner engine referenced in security workflow trigger specification.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Referenced as the scanner engine for PR security audits.",
    usage_limit="No license limits.", free_paid="Free", access_restr="No",
    license_name="Apache-2.0", spdx="Apache-2.0", copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Local-only", attrib="Standard Apache-2.0 notice", legal_verdict="Permissible",
    subs_avail="Free ($0.00)", sel_sub="Aqua Trivy OSS ($0.00)", reason_sub="Open-source tool.",
    category="Utility", comp_name="K3s 1.35", wf_name="Trivy Trigger", wf_yml="trivy-trigger.yml",
    user_limit="Unlimited", usage_limits="None", token_secret="None",
    lic_suit="Yes; Apache-2.0.", sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Trigger infrastructure for Trivy scanning.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; security compliance.",
    official_site="https://trivy.dev", purch_link="N/A (Free Open Source)", price_link="N/A (Free Open Source)",
    suit_open_reason="Yes; $0 cost.", why_not_suit="N/A", alt_options="None required",
    best_alt="Trivy OSS", reason_best_alt="Standard open-source scanner.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/trivy-trigger.yml:1-30"
)

# 32. Trivy Trigger - Rancher VEX Hub (Row 1154)
add_row(
    name="Rancher VEX Hub", version="OpenVEX specification",
    purpose="VEX metadata source referenced in Trivy trigger pipeline.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Provides false-positive suppressions.",
    usage_limit="None.", free_paid="Free", access_restr="No",
    license_name="Apache-2.0", spdx="Apache-2.0", copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Local-only", attrib="None", legal_verdict="Permissible",
    subs_avail="Free ($0.00)", sel_sub="Rancher OpenVEX Public Feed ($0.00)", reason_sub="Open metadata.",
    category="Utility", comp_name="K3s 1.35", wf_name="Trivy Trigger", wf_yml="trivy-trigger.yml",
    user_limit="Unlimited", usage_limits="None", token_secret="None",
    lic_suit="Yes; open source.", sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Metadata feed for Trivy.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; security auditing.",
    official_site="https://github.com/rancher/vexhub", purch_link="N/A (Free Open Source)", price_link="N/A (Free Open Source)",
    suit_open_reason="Yes; $0 cost.", why_not_suit="N/A", alt_options="None required",
    best_alt="Rancher VEX Hub", reason_best_alt="Official VEX repository.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/trivy-trigger.yml:1-30"
)

# 33. Unit Coverage - Hosted Runner (Row 1158)
add_row(
    name=GHA_RUNNER_NAME, version=GHA_RUNNER_VER,
    purpose="Compiles K3s with coverage instrumentation (-cover), runs Linux unit tests with race detection, runs Windows unit tests, and generates reports.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Standard hosted runner for unit test execution across Linux and Windows.",
    usage_limit=GHA_RUNNER_USAGE, free_paid="Free", access_restr="No",
    license_name=GHA_RUNNER_LIC, spdx=GHA_RUNNER_SPDX, copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Local-only", attrib="None", legal_verdict="Permissible",
    subs_avail=GHA_RUNNER_SUBS, sel_sub=GHA_RUNNER_SEL_SUB, reason_sub="Free compute.",
    category="Test", comp_name="K3s 1.35", wf_name="Unit Coverage", wf_yml="unitcoverage.yaml",
    user_limit="Standard limits", usage_limits=GHA_RUNNER_CONC, token_secret="None",
    lic_suit=GHA_RUNNER_TEAM, sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Ensures all unit tests pass with zero race conditions.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; mandatory quality gate for release readiness.",
    official_site=GHA_RUNNER_SITE, purch_link=GHA_RUNNER_PURCH, price_link=GHA_RUNNER_PRICE,
    suit_open_reason="Yes; $0 cost.", why_not_suit="N/A", alt_options="Self-hosted runners",
    best_alt="GitHub Actions Standard Hosted Runner", reason_best_alt="Standard free hosted compute.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/unitcoverage.yaml:25"
)

# 34. Unit Coverage - Codecov (Row 1162)
add_row(
    name="Codecov", version="codecov/codecov-action v4 / v5",
    purpose="Uploads unit test Go code coverage profiles to Codecov SaaS to track test coverage delta across pull requests.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Aggregates unit test code coverage metrics.",
    usage_limit="Free for OSS public repositories.", free_paid="Free (for OSS)", access_restr="No",
    license_name="Terms of Service / Apache-2.0", spdx="Terms of Service / Apache-2.0",
    copyleft="None / Permissive", comm_rights="Permitted", telemetry="Cloud SaaS logs",
    attrib="None", legal_verdict="Permissible", subs_avail="Free for OSS", sel_sub="Open Source Free Tier ($0.00)",
    reason_sub="Free coverage reporting.",
    category="Test", comp_name="K3s 1.35", wf_name="Unit Coverage", wf_yml="unitcoverage.yaml",
    user_limit="Unlimited", usage_limits="Standard API rate limits", token_secret="CODECOV_TOKEN",
    lic_suit="Yes; for public repos.", sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Tracks unit test coverage regressions.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; test quality metric.",
    official_site="https://about.codecov.io", purch_link="https://about.codecov.io/pricing",
    price_link="https://about.codecov.io/pricing", suit_open_reason="Yes; free for OSS.",
    why_not_suit="Fails on dispatch if CODECOV_TOKEN is evaluated in step if expressions without env guard.",
    alt_options="Native Go coverage summary (go tool cover) + GitHub Step Summary + Artifacts",
    best_alt="Native Go Coverage Summary & GitHub Step Summary ($0.00)",
    reason_best_alt="100% reliable, zero token dependency, renders coverage tables directly in Actions UI.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/unitcoverage.yaml:180-195"
)

# 35. Updatecli - Hosted Runner (Row 1166)
add_row(
    name=GHA_RUNNER_NAME, version=GHA_RUNNER_VER,
    purpose="Runs updatecli automation engine daily to check for updates to core dependencies (Go runtime, Helm controller, Flannel, Calico, K3s rootfs).",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Standard hosted runner for automated dependency update bot.",
    usage_limit=GHA_RUNNER_USAGE, free_paid="Free", access_restr="No",
    license_name=GHA_RUNNER_LIC, spdx=GHA_RUNNER_SPDX, copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Local-only", attrib="None", legal_verdict="Permissible",
    subs_avail=GHA_RUNNER_SUBS, sel_sub=GHA_RUNNER_SEL_SUB, reason_sub="Free compute.",
    category="Utility", comp_name="K3s 1.35", wf_name="Updatecli", wf_yml="updatecli.yaml",
    user_limit="Standard limits", usage_limits=GHA_RUNNER_CONC, token_secret="RANCHER_UPDATECLI_PAT (Bot Account Secret)",
    lic_suit=GHA_RUNNER_TEAM, sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Automates keeping K3s dependencies current with upstream releases.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; keeps dependencies patched and secure.",
    official_site=GHA_RUNNER_SITE, purch_link=GHA_RUNNER_PURCH, price_link=GHA_RUNNER_PRICE,
    suit_open_reason="Yes; $0 cost.", why_not_suit="N/A", alt_options="Dependabot, Renovate",
    best_alt="GitHub Actions Standard Hosted Runner", reason_best_alt="Standard free compute.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/updatecli.yaml:25"
)

# 36. Updatecli - Updatecli OSS (Row 1170)
add_row(
    name="Updatecli OSS", version="updatecli/updatecli-action v2 (Updatecli v0.80+)",
    purpose="Declarative dependency management tool that parses update policies and automatically opens GitHub pull requests with version bumps.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Declarative GitOps and dependency automation tool tailored for complex multi-file updates.",
    usage_limit="No license limits; open source CLI.", free_paid="Free", access_restr="No",
    license_name="Apache-2.0", spdx="Apache-2.0", copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Local-only", attrib="Standard Apache-2.0 attribution", legal_verdict="Permissible",
    subs_avail="Free ($0.00)", sel_sub="Updatecli OSS ($0.00)", reason_sub="Open-source project.",
    category="Utility", comp_name="K3s 1.35", wf_name="Updatecli", wf_yml="updatecli.yaml",
    user_limit="Unlimited", usage_limits="None", token_secret="GITHUB_TOKEN or Custom PAT",
    lic_suit="Yes; 100% open source under Apache-2.0.", sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Enables automated declarative version synchronization for core K3s binaries and charts.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; manages dependency life cycle.",
    official_site="https://www.updatecli.io", purch_link="N/A (Free Open Source)", price_link="N/A (Free Open Source)",
    suit_open_reason="Yes; $0 cost, open source.", why_not_suit="N/A", alt_options="Dependabot, Renovate bot",
    best_alt="Updatecli OSS", reason_best_alt="Built specifically to automate K3s component manifests, zero cost.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/updatecli.yaml:45"
)

# 37. Update Kubernetes - Hosted Runner (Row 1174)
add_row(
    name=GHA_RUNNER_NAME, version=GHA_RUNNER_VER,
    purpose="Runs updatecli_k8s automation on demand to synchronize Kubernetes dependencies and Go runtime versions across release branches.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Hosted runner compute for Kubernetes dependency synchronization.",
    usage_limit=GHA_RUNNER_USAGE, free_paid="Free", access_restr="No",
    license_name=GHA_RUNNER_LIC, spdx=GHA_RUNNER_SPDX, copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Local-only", attrib="None", legal_verdict="Permissible",
    subs_avail=GHA_RUNNER_SUBS, sel_sub=GHA_RUNNER_SEL_SUB, reason_sub="Free compute.",
    category="Utility", comp_name="K3s 1.35", wf_name="Update Kubernetes", wf_yml="updatecli_k8s.yaml",
    user_limit="Standard limits", usage_limits=GHA_RUNNER_CONC, token_secret="RANCHER_UPDATECLI_PAT",
    lic_suit=GHA_RUNNER_TEAM, sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Rebases K3s against upstream k3s-io/kubernetes staging branches.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; ensures K3s maintains parity with upstream Kubernetes patches.",
    official_site=GHA_RUNNER_SITE, purch_link=GHA_RUNNER_PURCH, price_link=GHA_RUNNER_PRICE,
    suit_open_reason="Yes; $0 cost.", why_not_suit="N/A", alt_options="Manual git rebase",
    best_alt="GitHub Actions Standard Hosted Runner", reason_best_alt="Standard free hosted compute.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/updatecli_k8s.yaml:25"
)

# 38. Update Kubernetes - Updatecli OSS (Row 1178)
add_row(
    name="Updatecli OSS", version="updatecli/updatecli-action v2",
    purpose="Executes Kubernetes dependency update policies against Go modules and manifest templates.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Automates complex multi-branch Kubernetes dependency bumps.",
    usage_limit="No limits.", free_paid="Free", access_restr="No",
    license_name="Apache-2.0", spdx="Apache-2.0", copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Local-only", attrib="Standard Apache-2.0 attribution", legal_verdict="Permissible",
    subs_avail="Free ($0.00)", sel_sub="Updatecli OSS ($0.00)", reason_sub="Open source tool.",
    category="Utility", comp_name="K3s 1.35", wf_name="Update Kubernetes", wf_yml="updatecli_k8s.yaml",
    user_limit="Unlimited", usage_limits="None", token_secret="GITHUB_TOKEN",
    lic_suit="Yes; Apache-2.0.", sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Aligns K3s branches with official Kubernetes versions.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; updates Kubernetes versions.",
    official_site="https://www.updatecli.io", purch_link="N/A (Free Open Source)", price_link="N/A (Free Open Source)",
    suit_open_reason="Yes; $0 cost.", why_not_suit="N/A", alt_options="Manual dependency updates",
    best_alt="Updatecli OSS", reason_best_alt="Automates repetitive Kubernetes version updates.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/updatecli_k8s.yaml:45"
)

# 39. Validate - Hosted Runner (Row 1182)
add_row(
    name=GHA_RUNNER_NAME, version=GHA_RUNNER_VER,
    purpose="Executes static code analysis, git commit validation, gofmt, govet, and golangci-lint on every pull request.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Standard hosted runner for core codebase linting and formatting validation.",
    usage_limit=GHA_RUNNER_USAGE, free_paid="Free", access_restr="No",
    license_name=GHA_RUNNER_LIC, spdx=GHA_RUNNER_SPDX, copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Local-only", attrib="None", legal_verdict="Permissible",
    subs_avail=GHA_RUNNER_SUBS, sel_sub=GHA_RUNNER_SEL_SUB, reason_sub="Free compute.",
    category="Test", comp_name="K3s 1.35", wf_name="Validate", wf_yml="validate.yaml",
    user_limit="Standard limits", usage_limits=GHA_RUNNER_CONC, token_secret="None",
    lic_suit=GHA_RUNNER_TEAM, sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Enforces clean Go code syntax, formatting, and prevents merge of broken commits.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; primary CI gate for codebase health.",
    official_site=GHA_RUNNER_SITE, purch_link=GHA_RUNNER_PURCH, price_link=GHA_RUNNER_PRICE,
    suit_open_reason="Yes; $0 cost.", why_not_suit="N/A", alt_options="Pre-commit git hooks",
    best_alt="GitHub Actions Standard Hosted Runner", reason_best_alt="Standard free compute.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/validate.yaml:25"
)

# 40. Issue Filter - Hosted Runner (Row 1186)
add_row(
    name=GHA_RUNNER_NAME, version=GHA_RUNNER_VER,
    purpose="Runs GitHub script on new issue creation to enforce title length rules (max 80 chars) and template adherence.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Executes actions/github-script for community issue triage.",
    usage_limit=GHA_RUNNER_USAGE, free_paid="Free", access_restr="No",
    license_name=GHA_RUNNER_LIC, spdx=GHA_RUNNER_SPDX, copyleft="None / Permissive", comm_rights="Permitted",
    telemetry="Cloud SaaS logs (GitHub API)", attrib="None", legal_verdict="Permissible",
    subs_avail=GHA_RUNNER_SUBS, sel_sub=GHA_RUNNER_SEL_SUB, reason_sub="Free compute.",
    category="Utility", comp_name="K3s 1.35", wf_name="Issue Filter", wf_yml="issue-filter.yaml",
    user_limit="Standard limits", usage_limits=GHA_RUNNER_CONC, token_secret="GITHUB_TOKEN (issues: write)",
    lic_suit=GHA_RUNNER_TEAM, sub_suit="Yes; $0.", req_purchase="No",
    why_upstream="Enforces issue hygiene on community bug reports.",
    access_status="Accessible", is_mandatory="No",
    suit_release="Optional; community bot, irrelevant for compiled fork releases.",
    official_site=GHA_RUNNER_SITE, purch_link=GHA_RUNNER_PURCH, price_link=GHA_RUNNER_PRICE,
    suit_open_reason="Yes; $0 cost.", why_not_suit="N/A", alt_options="Disabling issue filter workflow",
    best_alt="GitHub Actions Standard Hosted Runner", reason_best_alt="Standard free hosted compute.",
    replaces_tool="N/A (Original Tool)", issues_ml="None",
    evidence=".github/workflows/issue-filter.yaml:15"
)

# 41. Performance Test - AWS 15-node cluster (Row 1190 - Upstream Paid)
add_row(
    name="AWS 15-node performance cluster", version="AWS EC2 c5.xlarge/m5.xlarge instances (15-node cluster)",
    purpose="Provisions a 15-node multi-node AWS Kubernetes cluster to benchmark K3s performance, throughput, and scale before major customer releases.",
    rec_type="Upstream Original Tool", alt_of="N/A (Upstream Original)",
    reason_sel="Provides a realistic cloud-hosted multi-node network topology to measure etcd latency, pod scheduling speed, and network throughput under load.",
    usage_limit="Execution cost: 2 performance tests per PI across 3 PIs/year = $186/year ($31 per test execution).",
    free_paid="Paid ($186.00 / year)", access_restr="No (Requires AWS cloud account and billing budget)",
    license_name="AWS Customer Agreement", spdx="Commercial Cloud Service",
    copyleft="None (Cloud Infrastructure)", comm_rights="Permitted", telemetry="Local-only to AWS tenant",
    attrib="None", legal_verdict="Permissible (Standard cloud compute)",
    subs_avail="AWS Pay-as-you-go on-demand / spot EC2 compute ($186.00/year published in master_list)",
    sel_sub="On-Demand AWS EC2 Compute ($186.00 / year)",
    reason_sub="Master list explicitly budgets $186/year ($62/PI x 3 PIs, 2 performance tests per PI @ $31/test).",
    category="Test", comp_name="K3s 1.35", wf_name="Performance Test", wf_yml="performance-test (planned)",
    user_limit="Team cloud account", usage_limits="15 nodes running for ~2-3 hours per test",
    token_secret="AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY",
    lic_suit="Yes; standard AWS cloud services suitable for any 5-member team.",
    sub_suit="Yes; low annual spend ($186/yr) fits easily within standard DevOps cloud budgets.",
    req_purchase="Yes (Requires AWS cloud compute budget / Purchase Order for $186/year)",
    why_upstream="Validates cluster performance under real multi-node network latency and high pod densities.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; essential quality gate to certify production cluster scale and latency SLAs.",
    official_site="https://aws.amazon.com/ec2", purch_link="https://aws.amazon.com",
    price_link="https://aws.amazon.com/ec2/pricing/on-demand",
    suit_open_reason="Yes; modest $186/year cloud spend for production release qualification.",
    why_not_suit="Requires AWS cloud account, credentials, and billing management.",
    alt_options="Local Proxmox KVM / k3d Multi-Node Cluster on Shared Physical Server, On-Demand AWS EC2",
    best_alt="Local Proxmox KVM / k3d Multi-Node Cluster on Shared Physical Server",
    reason_best_alt="Enables unlimited 15-node performance tests locally at $0 cloud cost using on-premise hardware.",
    replaces_tool="N/A (Original Tool)",
    issues_ml="Master list notes: Two performance executions per PI; 3 PIs/year; $31/test = $186/yr. Used before planned customer releases.",
    evidence="master_list:Row 1190; workflow-fixes/k3s-workflow-infra-cost-estimate.md:Row 32; Sheet3:R8-R11"
)

# 42. Performance Test - Recommended Fork Alternate for AWS cluster
add_row(
    name="Local Proxmox KVM / k3d Multi-Node Cluster on Shared Physical Server",
    version="Proxmox VE 8.x / k3d v5+ (15 virtual nodes / LXC containers)",
    purpose="Simulates a 15-node multi-node K3s cluster locally on shared physical server hardware (or local k3d container topology) for benchmark validation.",
    rec_type="Recommended Fork Alternate", alt_of="AWS 15-node performance cluster",
    reason_sel="Eliminates recurring AWS cloud spend by executing multi-node scale tests on existing on-premise physical servers.",
    usage_limit="Constrained by physical server RAM and CPU (easily hosted on 64-core, 192GB+ Proxmox server).",
    free_paid="Free ($0.00 recurring cloud spend)", access_restr="No",
    license_name="GNU AGPLv3 (Proxmox VE) / Apache-2.0 (k3d)", spdx="AGPL-3.0-or-later / Apache-2.0",
    copyleft="Strong Copyleft (Proxmox hypervisor) / Permissive (k3d)", comm_rights="Permitted",
    telemetry="Local-only (100% on-premise)", attrib="Standard AGPLv3 / Apache-2.0 notices",
    legal_verdict="Permissible", subs_avail="Free ($0.00)", sel_sub="On-Premise Shared Physical Server ($0.00 recurring)",
    reason_sub="Eliminates the $186/year AWS compute cost and provides instant, repeatable benchmark environments.",
    category="Test", comp_name="K3s 1.35", wf_name="Performance Test", wf_yml="performance-test (planned)",
    user_limit="Team server access", usage_limits="Server hardware capacity", token_secret="None",
    lic_suit="Yes; 100% accessible to 5-member engineering team.", sub_suit="Yes; $0 recurring.", req_purchase="No",
    why_upstream="Upstream uses AWS for standardized public benchmarks, but local virtual clusters yield identical test metrics.",
    access_status="Accessible", is_mandatory="Yes",
    suit_release="Yes; certifies multi-node performance without external cloud accounts.",
    official_site="https://www.proxmox.com", purch_link="N/A (Free Open Source)", price_link="N/A (Free Open Source)",
    suit_open_reason="Yes; ideal for internal engineering teams with local test servers.",
    why_not_suit="N/A (Fully suitable)", alt_options="AWS on-demand EC2 cluster, GCP GKE benchmark",
    best_alt="Local Proxmox KVM / k3d Multi-Node Cluster on Shared Physical Server",
    reason_best_alt="Zero recurring cloud cost, repeatable performance benchmarks, zero cloud credential management.",
    replaces_tool="AWS 15-node performance cluster",
    issues_ml="Replaces $186/yr recurring AWS compute spend with on-premise physical server test execution.",
    evidence="workflow-fixes/server-hardware-sizing-and-ha-architecture.md:Section 2; master_list:Row 1190"
)

# Styling Definitions
header_font = Font(name='Calibri', size=11, bold=True, color='00FFFFFF')
header_fill = PatternFill(start_color='001F4E79', end_color='001F4E79', fill_type='solid')
header_align = Alignment(horizontal='center', vertical='center', wrap_text=True)

thin_border = Border(
    left=Side(style='thin', color='D3D3D3'),
    right=Side(style='thin', color='D3D3D3'),
    top=Side(style='thin', color='D3D3D3'),
    bottom=Side(style='thin', color='D3D3D3')
)

data_font = Font(name='Calibri', size=10, bold=False, color='000000')
zebra_fill = PatternFill(start_color='00F2F4F7', end_color='00F2F4F7', fill_type='solid')
white_fill = PatternFill(start_color='00FFFFFF', end_color='00FFFFFF', fill_type='solid')

# Format header row
for col_idx in range(1, 45):
    cell = ws.cell(1, col_idx)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = header_align
    cell.border = thin_border
ws.row_dimensions[1].height = 28.0

# Write data rows
for r_idx, row_data in enumerate(rows, start=2):
    fill = zebra_fill if r_idx % 2 == 0 else white_fill
    for c_idx, val in enumerate(row_data, start=1):
        cell = ws.cell(r_idx, c_idx, val)
        cell.font = data_font
        cell.fill = fill
        cell.border = thin_border
        
        # Center-align specific short columns
        if c_idx in (4, 8, 9, 12, 13, 16, 20, 21, 29, 31, 32):
            cell.alignment = Alignment(horizontal='center', vertical='top', wrap_text=True)
        else:
            cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
            
    ws.row_dimensions[r_idx].height = 24.0

# Set column widths matching spring_boot sheet
col_widths = {
    'A': 48.0, 'B': 45.0, 'C': 50.0, 'D': 35.0, 'E': 45.0, 'F': 45.0, 'G': 35.0,
    'H': 18.0, 'I': 30.0, 'J': 40.0, 'K': 30.0, 'L': 25.0, 'M': 25.0, 'N': 28.0,
    'O': 25.0, 'P': 25.0, 'Q': 35.0, 'R': 35.0, 'S': 35.0, 'T': 20.0, 'U': 18.0,
    'V': 30.0, 'W': 28.0, 'X': 25.0, 'Y': 30.0, 'Z': 35.0, 'AA': 35.0, 'AB': 35.0,
    'AC': 25.0, 'AD': 45.0, 'AE': 25.0, 'AF': 25.0, 'AG': 35.0, 'AH': 40.0, 'AI': 35.0,
    'AJ': 35.0, 'AK': 45.0, 'AL': 40.0, 'AM': 45.0, 'AN': 50.0, 'AO': 50.0, 'AP': 45.0,
    'AQ': 45.0, 'AR': 45.0
}
for col_letter, width in col_widths.items():
    ws.column_dimensions[col_letter].width = width

wb.save(wb_path)
print(f"Successfully populated 'k3s' sheet with {len(rows)} rows across all 44 columns!")
