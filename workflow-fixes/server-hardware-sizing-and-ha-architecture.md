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
