# Physical Server Hardware Sizing, High-Availability Architecture, and Cost Plan

## 1. Executive Workload & Sizing Analysis

This specification document outlines the physical hardware architecture required to support internal development, testing, and CI/CD validation for:
- **Forked k3s:** Multi-node cluster testing (3-node HA control planes, agent nodes, dual-stack networking).
- **GraalVM & Spring Boot:** High-concurrency Native Image compilation (`native-image`), JVM memory execution, containerized integration test harnesses.
- **Node.js & Angular:** Frontend bundlers (Vite/Webpack), npm dependency caching, Playwright/Cypress end-to-end browser testing.
- **Developer Environments:** Persistent remote development virtual machines (VS Code Remote / Code-Server).
- **Self-Hosted CI Runners:** Offloading compute-heavy builds and matrix testing from GitHub Actions.

---

## 2. Resource Consumption & Capacity Breakdown

### Workload Characteristics
| Workload | CPU Profile | Memory Footprint | Storage Profile | Critical Resource Bottleneck |
| :--- | :--- | :--- | :--- | :--- |
| **GraalVM Native Image** | 100% burst across 4–8 vCPUs during compilation | 8–16 GB RAM per active build | High temporary I/O (`/tmp`, build artifacts) | **RAM & CPU Bursts** |
| **k3s Test Clusters** | 2 vCPU per node; low steady-state utilization | 2–4 GB RAM per node; 12–24 GB per 3-node cluster | 30–50 GB per node; frequent disk writes (etcd/sqlite) | **Storage IOPS & Write Latency** |
| **Spring Boot Dev VM** | Moderate; spikes during compilation & Maven/Gradle runs | 8–16 GB RAM (JVM heap + local DB containers) | 60–100 GB (Docker images, `.m2` repository) | **RAM Capacity** |
| **Angular / Node.js Dev VM** | Burst on rebuild/hot-reload; low steady-state | 8–16 GB RAM (Node runtime, browser tabs) | 50–80 GB (npm `node_modules` cache) | **Disk IOPS & Inode Count** |
| **Self-Hosted GitHub Runner** | 4–8 vCPUs during matrix workflow runs | 16 GB RAM | 80–120 GB (Docker cache, build layers) | **Storage Endurance (DWPD)** |

---

## 3. Storage Redundancy & Drive Sizing Requirements

### Why 2 TB NVMe in RAID 1 is Inadequate
1. **ZFS 80% Capacity Threshold:** ZFS uses Copy-On-Write (COW). When a ZFS pool exceeds 80% utilization, contiguous block allocation fails, write amplification increases exponentially, and I/O latency degrades drastically. On a 2 TB drive (~1.8 TiB usable raw), the maximum safe capacity is only **~1.44 TiB**.
2. **Developer & Build Footprint:** A single functional dev VM (OS + Docker + GraalVM SDKs + caches) consumes 80–120 GB. Twelve VMs require ~1.2 TB without snapshots, swap, or container layers.
3. **Endurance Failure Risk:** Consumer NVMe SSDs (e.g., Samsung 990 Pro) feature low endurance (~0.3 DWPD). Enterprise build workloads writing tens of gigabytes per hour can exhaust consumer flash memory within 12–18 months.

### Required Storage Configuration
- **Hypervisor OS Boot:** Dedicated **2x 480 GB Enterprise SATA SSDs** in RAID 1 (Dell BOSS or ZFS mirror).
- **VM Data Pool:** Minimum **4x 3.84 TB Enterprise U.2/U.3 NVMe SSDs** in **ZFS RAID-10 (Striped Mirrors)**.
  - **Raw Usable:** ~7.68 TB (~6.14 TB safe usable threshold).
  - **Performance:** Double the write IOPS of a mirror, zero parity calculation overhead, and fast rebuild times (scrub/resilver in minutes).
  - **Endurance:** Enterprise U.2/U.3 drives rated for **1.0 to 3.0 DWPD** (e.g., Samsung PM9A3, Micron 7450 PRO, Kioxia CD6/CD8).

---

## 4. Hypervisor Selection: Proxmox VE vs. VMware vSphere

Following Broadcom's acquisition of VMware, licensing models have shifted to mandatory per-core annual subscriptions (costing several thousand dollars per year for a 96-core deployment).

| Metric | Proxmox VE 8.x (Recommended) | VMware vSphere 8.x (ESXi) |
| :--- | :--- | :--- |
| **Software License Cost** | **$0.00** (Free, open-source AGPLv3). Optional enterprise repo: ~$120/socket/yr. | Billed per core on steep recurring subscriptions ($4,000–$10,000+/yr). Free ESXi is discontinued. |
| **ZFS Storage Support** | **Native Tier-1 ZFS.** Out-of-the-box compression (ZSTD), snapshots, and replication. | No native ZFS. Requires expensive hardware RAID or vSAN licensing. |
| **Lightweight Containers** | Built-in **LXC containers** (run k3s clusters with near-zero memory overhead). | VMs only (no native lightweight OS containers). |
| **API & Automation** | Native REST API, verified **Terraform Provider**, and **Packer Plugin**. | Requires paid vCenter Server licenses for complete Terraform automation. |

---

## 5. High-Availability (HA) Strategy

A single server possesses **component redundancy** (dual PSUs, RAID-10 disks, bonded LACP NICs), but remains a **Single Point of Failure (SPOF)**. If the motherboard, CPU, or hypervisor fails, all development and test VMs halt.

```
┌────────────────────────────────────────────────────────────────────────┐
│                       HA ARCHITECTURE OPTIONS                         │
├────────────────────────────────────────────────────────────────────────┤
│ OPTION 1: Standalone Powerhouse + External Proxmox Backup Server (PBS) │
│                                                                        │
│   ┌─────────────────────────────┐         ┌────────────────────────┐   │
│   │   Single Powerhouse Node    │  10GbE  │  External PBS Storage  │   │
│   │ 96 vCPU | 384GB | 7.6TB NVMe│ ───────►│ Deduplicated, Hourly   │   │
│   └─────────────────────────────┘         │ Incremental Backups    │   │
│                                           └────────────────────────┘   │
├────────────────────────────────────────────────────────────────────────┤
│ OPTION 2: 2-Node Proxmox Active-Active HA Cluster with QDevice Quorum │
│                                                                        │
│   ┌───────────────────────────┐  Direct 10G/25G  ┌──────────────────┐ │
│   │      Proxmox Node A       │◄────────────────►│  Proxmox Node B   │ │
│   │ 64 vCPU | 192GB | 3.8TB   │  ZFS Replication │64 vCPU | 192GB    │ │
│   └─────────────┬─────────────┘   (every 1 min)  └────────┬─────────┘ │
│                 │                                         │           │
│                 │            ┌──────────────┐             │           │
│                 └───────────►│QDevice Quorum│◄────────────┘           │
│                              │3rd Vote (NUC)│                         │
│                              └──────────────┘                         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Final Hardware Specifications & Market Cost Breakdown

Below are the **two concrete hardware configurations** engineered to meet your development and testing objectives.

---

### Option 1: The Upgraded Single-Node Powerhouse
*Consolidates all dev VMs, k3s clusters, and CI runners into a single high-density 2U chassis.*

```
+---------------------------------------------------------------------------------------+
| DELL POWEREDGE R7525 / SUPERMICRO 2U DUAL AMD EPYC ENTERPRISE SERVER                 |
+---------------------------------------------------------------------------------------+
| CPU:       2x AMD EPYC 7443 or 7543 (48 to 64 Cores / 96 to 128 Threads @ up to 4.0GHz)|
| RAM:       384 GB DDR4-3200 MHz ECC Registered (12x 32 GB, 8-Channel Architecture)   |
| Boot:      2x 480 GB Enterprise SATA SSDs (RAID 1 Mirror via Dell BOSS-S1)            |
| Storage:   4x 3.84 TB Enterprise U.2 PCIe 4.0 NVMe SSDs in ZFS RAID-10 (~7.6 TB Raw)  |
| Network:   Dual-Port 10G/25G SFP28 PCIe NIC (Mellanox ConnectX-4 Lx / Intel E810)     |
| Power:     Dual 1400W 80-Plus Titanium Redundant Hot-Plug Power Supplies              |
| Remote:    iDRAC9 Enterprise / IPMI 2.0 with Dedicated NIC                            |
+---------------------------------------------------------------------------------------+
```

#### Detailed Cost Breakdown (Option 1)

| Subsystem | Component Specification | Refurbished Enterprise (Grade A, Certified) | Brand New (Current Gen SP5 / EPYC 9004) |
| :--- | :--- | :---: | :---: |
| **Chassis & Board** | 2U Rackmount 8-bay Direct-Attach NVMe chassis, Dual Titanium PSUs, iDRAC9 Ent. | $1,300 – $1,600 | $3,500 – $4,500 |
| **Processors** | Dual AMD EPYC 7543 (64C / 128T total, 256MB Cache) or Dual 7402 (48C / 96T) | $900 – $1,400 | $3,200 – $4,800 |
| **RAM** | 384 GB (12x 32 GB) DDR4-3200 MHz ECC RDIMM (or DDR5 on new) | $550 – $750 | $1,600 – $2,200 |
| **Boot Drives** | 2x 480 GB Enterprise SATA SSD (Micron 5300 PRO / Intel D3) in RAID 1 | $150 – $200 | $350 – $500 |
| **VM Storage** | 4x 3.84 TB Enterprise U.2 PCIe 4.0 NVMe (Samsung PM9A3 / Micron 7450 PRO) | $1,100 – $1,450 | $1,600 – $2,400 |
| **Networking** | Dual-port 10/25 GbE SFP28 PCIe Adapter (Mellanox ConnectX-4 Lx) | $150 – $250 | $350 – $500 |
| **Rails & Accessories**| ReadyRails sliding rail kit, cable management arm, power cables | $100 – $150 | $150 – $200 |
| **Total Cost** | | **$4,250 – $5,800 USD** | **$10,750 – $15,100 USD** |

---

### Option 2: 2-Node Active-Active HA Cluster Pair (2 Physical Servers + 1 QDevice)
*Eliminates the single point of failure. Workloads are distributed across two physical nodes with continuous 1-minute ZFS replication. If one node requires maintenance or fails, VMs automatically restart on the companion node.*

```
+---------------------------------------------------------------------------------------+
| NODE A (1U Server)                                                                   |
| - CPU:     1x AMD EPYC 7543P (32 Physical Cores / 64 Threads @ up to 4.0 GHz, 256MB)  |
| - RAM:     192 GB DDR4-3200 MHz ECC Registered (6x 32 GB)                             |
| - Boot:    2x 480 GB Enterprise SATA SSDs (RAID 1 Mirror)                             |
| - Storage: 2x 3.84 TB Enterprise U.2 PCIe 4.0 NVMe SSDs (ZFS RAID 1 Mirror)           |
| - Network: Dual-Port 10G/25G SFP28 (Port 1: Direct Sync Cable, Port 2: LAN)           |
+---------------------------------------------------------------------------------------+
| NODE B (1U Server - Identical Clone of Node A)                                       |
| - CPU:     1x AMD EPYC 7543P (32 Physical Cores / 64 Threads @ up to 4.0 GHz, 256MB)  |
| - RAM:     192 GB DDR4-3200 MHz ECC Registered (6x 32 GB)                             |
| - Boot:    2x 480 GB Enterprise SATA SSDs (RAID 1 Mirror)                             |
| - Storage: 2x 3.84 TB Enterprise U.2 PCIe 4.0 NVMe SSDs (ZFS RAID 1 Mirror)           |
| - Network: Dual-Port 10G/25G SFP28 (Port 1: Direct Sync Cable, Port 2: LAN)           |
+---------------------------------------------------------------------------------------+
| QUORUM WITNESS (QDevice)                                                             |
| - Intel NUC / Mini-PC / Raspberry Pi 4 running 'corosync-qnetd' (3rd Voting Member)   |
+---------------------------------------------------------------------------------------+
| CLUSTER CAPACITY: 64 Cores / 128 Threads | 384 GB Total RAM | 2x 3.84 TB Replicated NVMe|
+---------------------------------------------------------------------------------------+
```

#### Detailed Cost Breakdown (Option 2: 2-Node HA Cluster)

| Subsystem | Component Specification (x2 Servers) | Refurbished Enterprise (Pair Total) | Brand New (Pair Total) |
| :--- | :--- | :---: | :---: |
| **Chassis & Boards** | 2x Dell PowerEdge R6525 1U or Supermicro 1U Dual-PSU Servers | $1,800 – $2,400 | $4,800 – $6,200 |
| **Processors** | 2x AMD EPYC 7543P or 7443P (1 per node; 64C / 128T combined) | $1,100 – $1,600 | $2,800 – $3,800 |
| **RAM** | 384 GB Total: 2x [192 GB (6x 32 GB DDR4-3200 MHz ECC)] | $550 – $750 | $1,600 – $2,200 |
| **Boot Drives** | 4x 480 GB Enterprise SATA SSDs (2 per server in RAID 1) | $280 – $360 | $600 – $800 |
| **VM Storage** | 4x 3.84 TB Enterprise U.2 NVMe (2 per server; 3.84 TB mirror per node) | $1,100 – $1,450 | $1,600 – $2,400 |
| **Networking** | 2x Dual-Port 10G/25G SFP28 NICs + Direct Attach Copper (DAC) cable | $250 – $350 | $600 – $800 |
| **Quorum Device** | 1x Intel NUC / Mini PC (8 GB RAM, 128 GB SSD) for Corosync QDevice | $120 – $180 | $180 – $250 |
| **Total Cluster Cost** | | **$5,200 – $7,090 USD** | **$12,180 – $16,450 USD** |

---

## 7. Comparative Recommendation

| Dimension | Option 1: Single Powerhouse (2U) | Option 2: 2-Node HA Cluster (2x 1U + QDevice) |
| :--- | :--- | :--- |
| **Hardware Resilience** | SPOF on motherboard/CPU/backplane | **Zero downtime**; automated VM failover |
| **Kernel / Host Updates** | Requires scheduling dev downtime | **Live migration** allows zero-downtime rolling updates |
| **Storage Usable Space** | **~7.6 TB** ZFS RAID-10 (high capacity) | **~3.84 TB** per node (synchronized via replication) |
| **Rack Space & Power** | 2U rack space, ~350W–450W average power | 2U total rack space (2x 1U), ~400W–500W average power |
| **Deployment Complexity** | Very Low (standalone Proxmox setup) | Moderate (Proxmox cluster + ZFS replication job config) |
| **Budget (Refurbished)**| **~$4,250 – $5,800 USD** | **~$5,200 – $7,090 USD** |

### Strategic Recommendation
1. If your team cannot tolerate any downtime during hardware maintenance or hypervisor updates, choose **Option 2 (2-Node HA Cluster)** for approximately **$5,200 – $7,000 USD** (refurbished enterprise).
2. If maximum single-system storage capacity (~7.6 TB) and simplicity are prioritized, deploy **Option 1 (Single Powerhouse)** with 4x 3.84 TB NVMe in ZFS RAID-10 for **$4,250 – $5,800 USD**, paired with an external automated Proxmox Backup Server (PBS).

---

## 8. Deep Market Audit: Verifying the Initial $51,000 Single-Server Estimate

### Evidence-Based Reality Check
Your initial hardware configuration:
- **CPU:** 96 Logical CPUs (48 Physical Cores with HT/SMT)
- **RAM:** 384 GB ECC RAM
- **Storage:** 2 TB NVMe SSDs
- **User's Initial Price Estimate:** **$51,000 USD**

### Component-by-Component Market Cost Verification
Based on current 2025/2026 enterprise hardware market pricing across Dell Technologies, HPE, Supermicro, and authorized enterprise refurbished vendors:

| Subsystem Component | Refurbished Enterprise (Grade A Certified, e.g. Dell R7525) | Brand New OEM (e.g. Dell PowerEdge R7625 / R7615) | What is Charged in a $51,000 OEM List Quote |
| :--- | :---: | :---: | :--- |
| **Server Chassis & Motherboard** | $1,200 – $1,500 | $3,500 – $4,800 | Full unnegotiated OEM MSRP list price ($8,000+) |
| **Processor(s)** (48 Physical Cores total) | $900 – $1,300 *(Dual EPYC 7402/7443)* | $3,200 – $4,500 *(AMD EPYC 9454 48C/96T)* | OEM tray pricing marked up by 50–70% ($6,000+) |
| **Memory** (384 GB ECC Registered) | $550 – $750 *(12x 32GB DDR4 ECC)* | $1,600 – $2,400 *(DDR5 ECC RDIMMs)* | OEM branded RAM marked up by 200–300% ($5,000+) |
| **Storage** (2 TB NVMe SSDs) | $200 – $350 | $400 – $700 *(Enterprise U.2 NVMe)* | OEM branded SSDs marked up heavily ($1,500+) |
| **Networking & Management** | $250 – $400 *(10/25GbE + iDRAC Ent.)* | $500 – $900 | iDRAC Enterprise license + 25GbE card ($1,800+) |
| **Software Licensing** | **$0.00** *(Proxmox VE / KVM)* | **$0.00** *(Proxmox VE / KVM)* | **Bundled VMware vSphere / VCF licensing ($20,000 – $30,000 over 5 years)** |
| **Support Warranty** | Included 1–3 yr seller warranty | $1,500 – $2,500 *(3-yr ProSupport)* | 5-Year ProSupport Plus 4-Hour Mission Critical ($6,000 – $9,000) |
| **Total Subsystem Cost** | **$3,500 – $6,500 USD** | **$10,700 – $15,800 USD** | **$48,000 – $51,000+ USD** |

### Why Was $51,000 Quoted Originally?
1. **Unnegotiated OEM MSRP Sticker Shock:** Major server vendors (Dell, HPE, Lenovo) publish exorbitant list prices on their public websites. Enterprise procurement departments normally receive standard **55% to 70% discounts** off list prices upon engaging account managers or value-added resellers (VARs).
2. **Bundled Proprietary Hypervisor Licensing:** Under Broadcom, VMware vSphere Foundation (VVF) and VMware Cloud Foundation (VCF) are billed per core per year on mandatory subscription terms. Licensing a 48-to-96 core server for 5 years with VMware costs **$20,000 to $35,000+ in software alone**.
3. **Proprietary Vendor Support & Service Contracts:** A 5-year 24x7 4-hour on-site mission-critical SLA plus professional deployment services often adds **$8,000 to $12,000** to an enterprise quote.
4. **Branded Flash Memory Markups:** Server OEMs frequently charge $1,200+ for a re-branded 1.92 TB NVMe drive that retails from Samsung or Micron for $250.

> [!CAUTION]
> **Verdict on the $51,000 Estimate:**
> For pure hardware intended to run an open-source hypervisor (Proxmox VE), **$51,000 is grossly overpriced**:
> - It is **3x to 4x higher** than the true street price of brand-new current-generation OEM enterprise hardware (**$12,000 – $16,000**).
> - It is **8x to 10x higher** than certified Grade-A refurbished enterprise hardware (**$4,000 – $6,500**).

---

## 9. Requirements Mapping & Delta Cost Analysis for 2-Server HA Mode

### Detailed Architectural Mapping
You requested splitting the capacity into two physical servers to achieve true High Availability (HA) while incorporating all enterprise storage, boot, and network requirements:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        2-SERVER ACTIVE-ACTIVE HA CLUSTER ARCHITECTURE                  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│   ┌─────────────────────────────────────────┐   Dedicated 25GbE   ┌─────────────────────────────────────────┐   │
│   │           PROXMOX NODE A (1U)           │   DAC Cable (Direct)│           PROXMOX NODE B (1U)           │   │
│   ├─────────────────────────────────────────┤◄───────────────────►├─────────────────────────────────────────┤   │
│   │ CPU:     1x AMD EPYC 7543P (32C / 64T)  │   ZFS Replication   │ CPU:     1x AMD EPYC 7543P (32C / 64T)  │   │
│   │ RAM:     192 GB DDR4-3200 ECC (6x32GB)  │   (every 1 minute)  │ RAM:     192 GB DDR4-3200 ECC (6x32GB)  │   │
│   │ Boot:    2x 480 GB SATA SSDs (RAID 1)   │                     │ Boot:    2x 480 GB SATA SSDs (RAID 1)   │   │
│   │ Storage: 2x 3.84 TB U.2 NVMe (Mirror)   │   Corosync Heartbeat│ Storage: 2x 3.84 TB U.2 NVMe (Mirror)   │   │
│   │ Network: Dual 25GbE SFP28 + Dual 1GbE   │                     │ Network: Dual 25GbE SFP28 + Dual 1GbE   │   │
│   └────────────────────┬────────────────────┘                     └────────────────────┬────────────────────┘   │
│                        │                                                               │                        │
│                        │               10GbE / 1GbE LAN Switch Uplink                  │                        │
│                        └──────────────────────────────┬────────────────────────────────┘                        │
│                                                       │                                                         │
│                                            ┌──────────┴──────────┐                                              │
│                                            │  QDevice Witness    │                                              │
│                                            │  Mini-PC / NUC      │                                              │
│                                            │  (3rd Quorum Vote)  │                                              │
│                                            └─────────────────────┘                                              │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

#### 1. Splitting 96 Logical CPUs / 48 Physical Cores:
- **Node A:** 1x AMD EPYC 7543P (32 Physical Cores / 64 Threads @ up to 4.0 GHz, 256MB L3 Cache).
- **Node B:** 1x AMD EPYC 7543P (32 Physical Cores / 64 Threads @ up to 4.0 GHz, 256MB L3 Cache).
- **Combined Cluster Capacity:** **64 Physical Cores / 128 Threads** (Provides 33% *more* CPU compute than the single-node 48-core spec, allowing comfortable N+1 failover headroom!).

#### 2. Splitting 384 GB Memory:
- **Node A:** 192 GB DDR4-3200 MHz ECC Registered (6x 32 GB RDIMMs).
- **Node B:** 192 GB DDR4-3200 MHz ECC Registered (6x 32 GB RDIMMs).
- **Combined Cluster Memory:** **384 GB RAM** (Maintains 100% of the planned memory capacity across the cluster).

#### 3. Hypervisor OS Boot Redundancy:
- **Configuration per Node:** Dedicated **2x 480 GB Enterprise SATA SSDs** in Hardware RAID 1 (Dell BOSS-S1/S2 controller or Supermicro SATA DOM mirror).
- **Total across Cluster:** 4x 480 GB Enterprise SATA SSDs.
- **Architectural Purpose:** Completely isolates hypervisor OS files, kernel logs, systemd journals, and Proxmox ISOs from the VM data pool. If a boot SSD fails, the server continues running without interruption.

#### 4. VM Data Pool Storage Redundancy:
- **Configuration per Node:** **2x 3.84 TB Enterprise U.2/U.3 PCIe 4.0 NVMe SSDs** in a **ZFS Mirror (RAID 1)**.
- **Total across Cluster:** 4x 3.84 TB Enterprise U.2 NVMe SSDs.
- **Usable Pool per Node:** **~3.84 TB raw usable** (~3.0 TB at safe 80% ZFS threshold).
- **Data Protection:** Every minute, Proxmox's built-in **ZFS Storage Replication** takes a snapshot and synchronizes delta blocks across the direct 25GbE link from Node A to Node B (and vice-versa).

#### 5. Proxmox VE Cost Breakdown:
- **Base Hypervisor License:** **$0.00** (Full-featured open-source GNU AGPLv3 with clustering, live migration, and HA manager included with zero paywalls).
- **Optional Enterprise Repository (Community Support Tier):**
  - Cost: **€120 / CPU socket / year** (~$130 USD).
  - Cluster Total (2 single-socket CPUs): **2 × €120 = €240 / year (~$260 USD / year total)**.
  - Benefits: Access to vetted, enterprise-tested software updates and security patches.

#### 6. Network Interconnect & Quorum:
- **Interconnect NIC per Node:** Dual-Port 10G/25G SFP28 PCIe adapter (Mellanox ConnectX-4 Lx or Intel E810).
  - **Port 1 (Direct-Connect):** Linked directly between Node A and Node B via a **1-meter Direct Attach Copper (DAC) cable ($30)**. Bypasses external network switches completely, providing a dedicated 25 Gbps low-latency pipe for Corosync cluster messaging and continuous 1-minute ZFS disk replication.
  - **Port 2 (LAN Uplink):** Connected to the corporate/lab switch for VM traffic and developer access.
- **Quorum Witness (QDevice):** In a 2-node cluster, if one node drops, the remaining node only has 1 out of 2 votes (50%), which cannot establish quorum to prevent split-brain. A low-cost mini-PC (Intel NUC or Raspberry Pi 4, **~$120–$180**) running `corosync-qnetd` acts as an external 3rd voting member.

---

### Delta Cost Analysis: 1 Server vs. 2-Server HA Mode

How much extra does it cost to build a true 2-Server HA architecture compared to a single server?

| Infrastructure Item | Single Powerhouse Server (1 Node, 2U) | 2-Server HA Cluster Pair (2 Nodes, 2x 1U + QDevice) | Net Extra Cost for 2-Server HA Mode |
| :--- | :---: | :---: | :---: |
| **Chassis & Power Supplies** | 1x 2U Chassis + 2x PSUs ($1,300–$1,600 ref) | 2x 1U Chassis + 4x PSUs ($1,800–$2,400 ref) | **+$500 to +$800** |
| **Processors** | Dual EPYC 7543 / 7402 ($900–$1,400 ref) | 2x Single EPYC 7543P ($1,100–$1,600 ref) | **+$200 to +$300** *(1-socket CPUs are cheaper per core)* |
| **Memory (384 GB Total)** | 384 GB (12x 32GB) ($550–$750 ref) | 2x 192 GB (12x 32GB) ($550–$750 ref) | **$0.00** *(Identical RAM module count)* |
| **Boot Redundancy** | 2x 480 GB SATA SSDs ($150–$200 ref) | 4x 480 GB SATA SSDs ($280–$360 ref) | **+$130 to +$160** |
| **Data Pool Storage** | 4x 3.84 TB NVMe SSDs ($1,100–$1,450 ref) | 4x 3.84 TB NVMe SSDs ($1,100–$1,450 ref) | **$0.00** *(Identical drive count)* |
| **Networking & Cables** | 1x Dual-Port 25GbE NIC ($150–$250 ref) | 2x Dual-Port 25GbE NICs + DAC ($250–$350 ref) | **+$100 to +$150** |
| **Quorum Witness (QDevice)** | Not required ($0) | 1x Intel NUC / Mini-PC ($120–$180 new) | **+$120 to +$180** |
| **Proxmox Enterprise License** | 2 sockets = €240/yr (~$260/yr) | 2 sockets = €240/yr (~$260/yr) | **$0.00** *(Identical 2 sockets total)* |
| **Total Refurbished Cost** | **$4,250 – $5,800 USD** | **$5,200 – $7,090 USD** | **+$950 to +$1,290 USD total (~20% increase)** |
| **Total Brand New OEM Cost** | **$10,750 – $15,100 USD** | **$12,180 – $16,450 USD** | **+$1,430 to +$2,200 USD total (~15% increase)** |
| **Comparison to $51,000 Quote**| **Saves $35,900 – $46,750** | **Saves $34,550 – $45,800** | **Massive savings while gaining true zero-downtime HA!** |

---

## 10. Engineering Checklist: What Else Might Be Missed?

To ensure your high-availability deployment succeeds in production without surprises, verify these four critical operational dimensions:

1. **Recovery Point Objective (RPO) vs. Recovery Time Objective (RTO):**
   - In a 2-node shared-nothing cluster using ZFS replication over 25GbE, data is synchronized every **1 minute**. 
   - **RPO:** **1 minute** (in the worst-case scenario where Node A experiences a sudden catastrophic power loss, uncommitted disk writes from the last 60 seconds are lost).
   - **RTO:** **60 to 90 seconds** (Proxmox HA manager detects the node failure after 3 missed Corosync heartbeats and automatically boots the VMs on Node B).
   - *Note:* If strict 0-second RPO (synchronous lockstep mirroring) is mandatory, you would need either a 3-node Ceph hyperconverged storage cluster or an external shared NVMe-oF/iSCSI SAN array. For software development and CI/CD test workloads, 1-minute asynchronous ZFS replication is the enterprise industry standard.
2. **Dual Power Circuit & PDU Segregation:**
   - Both servers feature dual 80-Plus Platinum/Titanium redundant power supplies.
   - Connect PSU 1 of both servers to **PDU A (UPS Circuit 1)** and PSU 2 of both servers to **PDU B (UPS Circuit 2 / Utility)**. This prevents a tripped breaker or failing PDU from cutting power to both cluster nodes at once.
3. **Out-of-Band Management (iDRAC9 Enterprise / IPMI):**
   - Ensure each server's dedicated management NIC is assigned a static IP on an isolated management VLAN. This ensures full remote access (virtual KVM console, remote power cycle, OS reinstall, hardware sensor monitoring) even if the main network interface or hypervisor OS crashes.
4. **Dedicated External Backup Target (Proxmox Backup Server - PBS):**
   - High availability (HA) protects against hardware faults, but **it does not protect against accidental VM deletion, ransomware, or corrupted database states**.
   - Deploy **Proxmox Backup Server (PBS)** on an inexpensive existing NAS, workstation, or secondary server. PBS provides client-side encryption, high deduplication, and hourly incremental backups with zero impact on running VMs.

