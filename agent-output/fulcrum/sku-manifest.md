# 📦 SKU Manifest - fulcrum

![Artifact](https://img.shields.io/badge/Artifact-SKU%20Manifest-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Draft-orange?style=for-the-badge)
![Schema](https://img.shields.io/badge/Schema-sku--manifest--v1-purple?style=for-the-badge)

<details open>
<summary><strong>📑 Manifest Contents</strong></summary>

- [Overview](#overview)
- [Environments](#environments)
- [Services](#services)
- [Revision History](#revision-history)
- [Open Substitutions](#open-substitutions)

</details>

> Rendered from `sku-manifest.json` (rev 2) by `tools/scripts/render-sku-manifest-md.mjs`.
>
> **Do not hand-edit this file.** Mutate `sku-manifest.json` and re-run
> the renderer (wired into lefthook + CI). Authoring rules:
> [`.github/instructions/sku-manifest.instructions.md`](../../.github/instructions/sku-manifest.instructions.md).

## Overview

| Field            | Value                                                      |
| ---------------- | ---------------------------------------------------------- |
| Project          | `fulcrum`                                        |
| Default region   | `swedencentral` (per-service `regions[]` inherits this) |
| Schema version   | `sku-manifest-v1`                                          |
| Current revision | `2`                               |
| Last updated     | `2026-11-09T13:48:00Z`                                     |
| Environments     | `dev` (comma-separated)                              |
| Service count    | `4`                                        |

**Scope**: creative SKU decisions only — App Service plans, VMs/VMSS, SQL,
Cosmos, AKS pools, Redis, APIM, App Gateway, Storage replication tiers.

**Out of scope** (do not add to `services[]`): bandwidth, Log Analytics,
vnet, subnet, NSG, route table, public IP, diagnostics. See
[`.github/instructions/sku-manifest.instructions.md`](../../.github/instructions/sku-manifest.instructions.md).

## Environments

| Environment | In scope | Notes |
| ----------- | -------- | ----- |
| `dev` | ✅ | — |

## Services

> Rendered from `sku-manifest.json` `services[]`. Per-environment values
> reflect `environment_overrides` on top of the base entry.

| `id` | Service | Size (base) | Capacity | Zonal | Regions | SLA target / achieved | Commitment | Source | Rev |
| ---- | ------- | ----------- | -------- | ----- | ------- | --------------------- | ---------- | ------ | --- |
| `access-compute` | Virtual Machines | `Standard_D2as_v5` | `fixed (default 1)` | ❌ | `swedencentral` | `Dev/test — occasional downtime acceptable` / `Not assessed for the complete ephemeral access path; VM/disk service-credit conditions require reconciliation with confirmed supporting configuration. No runtime availability claim.` | `on-demand` | `architect-derived` | `2` |
| `app-host` | Azure App Service | `B1` | `fixed (default 1)` | ❌ | `swedencentral` | `Dev/test — occasional downtime acceptable` / `99.95% non-zone-redundant paid App Service service-credit uptime threshold; November 2026 Microsoft Online Services SLA. Not tested availability or an end-to-end guarantee.` | `on-demand` | `architect-derived` | `2` |
| `document-store` | Azure Cosmos DB | `Serverless` | `fixed (default 1)` | ❌ | `swedencentral` | `Dev/test — occasional downtime acceptable` / `99.99% single-region service-credit availability threshold; November 2026 Microsoft Online Services SLA. Serverless throughput/latency and application recovery are not guaranteed by this number.` | `on-demand` | `architect-derived` | `2` |
| `storage-blob-replication` | Storage Account | `LRS` | `fixed (default 1)` | ❌ | `swedencentral` | `Dev/test — occasional downtime acceptable` / `99.9% service-credit availability threshold for Standard Hot LRS; November 2026 Microsoft Online Services SLA. Not achieved workload availability.` | `on-demand` | `user-pin` | `2` |

### Per-environment overrides

_No services declare environment overrides._

### Feature requirements

| `id` | `requires[]` | Verified at Step 4 |
| ---- | ------------ | ------------------ |
| `access-compute` | `vnet-integration`, `managed-identity`, `bastion-native-entra-ssh`, `explicit-outbound-access` | ✅ / ❌ |
| `app-host` | `private-endpoints`, `vnet-integration`, `managed-identity`, `private-container-image-pull` | ✅ / ❌ |
| `document-store` | `private-endpoints`, `managed-identity`, `continuous-backup-30-days` | ✅ / ❌ |
| `storage-blob-replication` | `private-endpoints`, `managed-identity`, `blob-point-in-time-restore`, `standard-gpv2` | ✅ / ❌ |

### Cost estimate (USD/month)

> Populated by `cost-estimate-subagent` via `manifest_writeback[]` —
> Architect never types prices from parametric knowledge.

| `id` | `cost_estimate_monthly_usd` | Confidence |
| ---- | --------------------------- | ---------- |
| `access-compute` | `$7.36` | `—` |
| `app-host` | `$13.14` | `—` |
| `document-store` | `$12.10` | `—` |
| `storage-blob-replication` | `$10.76` | `—` |

## Revision History

> Append-only. Each row is metadata about a git commit / apex-recall checkpoint.

| `rev` | Step | Agent | Created (UTC) | Summary | Changed `id`s | Commit | Checkpoint |
| ----- | ---- | ----- | ------------- | ------- | ------------- | ------ | ---------- |
| `1` | `1` | `02-Requirements` | `2026-11-06T14:34:00Z` | Draft Step 1 capture: sole explicit creative pin is LRS replication. App Service and Cosmos explicitly have no SKU preference. On-demand only, dev only, no environment override. No architecture-derived configuration or prices. Validation and checkpoint success are tracked separately. | `storage-blob-replication` | `16cd2c7` | `fulcrum:1:phase_5_artifact` |
| `2` | `2` | `03-Architect` | `2026-11-09T13:48:00Z` | Current DEV architect selections from three COMPLETE comparison-only pricing results; original LRS lock and Step 1 commit metadata preserved. Supporting access/network/recovery scope remains subject to confirmation; no prices written into manifest and no SKU or Architecture approval inferred. | `storage-blob-replication`, `app-host`, `document-store`, `access-compute` | — | `fulcrum:2:phase_2_waf` |

## Open Substitutions

> Captured at Step 6 (Deploy) when a planned SKU is unavailable due to
> quota / region capacity. Mirrors `decisions.sku_overrides[]` in
> `00-session-state.json`.

> **None open** — all SKUs deployed as planned.

---

## References

- Schema: [`tools/schemas/sku-manifest.schema.json`](../../tools/schemas/sku-manifest.schema.json)
- Authoring rules: [`.github/instructions/sku-manifest.instructions.md`](../../.github/instructions/sku-manifest.instructions.md)
- Renderer: `node tools/scripts/render-sku-manifest-md.mjs <project>`
- Validators: `npm run validate:sku-manifest` + `npm run validate:sku-iac-coverage`
