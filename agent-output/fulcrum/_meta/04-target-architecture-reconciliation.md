# Local target-policy reconciliation — approved DEV design

**Architect owner research, not independent review or formal Governance.**
**Result: partial; target-backed readiness remains blocked.**
No approved design, SKU, price, projection, review, approval or step status changed.
[Machine-readable receipt](04-target-architecture-reconciliation.json) contains
all policy references, source hashes and the complete 58-record screening index.

## Result and evidence limit

- **No actual design conflict confirmed by the 13 retained Deny conditions:**
  six compatible with approved choices; seven outside selected capabilities.
  These are policy constraints, **not thirteen deployed-resource violations**.
- **No new material user decision is justified now.** Missing rule evidence and
  later deployment bindings are not user-checkbox decisions.
- The target capture is current **L0 COMPLETE**, but it is **not a complete
  rule-body archive**: all 45 DINE deployment/existence bodies, all 13 Modify
  applicability/complete operations, and individual rules for 245 Audit results
  are absent. Its definition index contains identifiers, not definition bodies.
  Do not infer missing requirements from display names or prior Corp assumptions.
- **Important unresolved location exposure:** subscription DINE
  `policy-4330c156074e93cf` and `policy-04d8e79fd35652b4` carry
  **`Location=WestUS2`** and the same privately named resource-group parameter.
  Their deployment bodies are absent. This does **not** prove workload telemetry
  must leave Sweden Central, that a workload RG must use this location, or that
  the approved boundary is already violated. Governance/platform must establish
  deployed product, data path, existence condition and ownership first.

The approved boundary remains Sweden Central for workload compute, app data,
Blob, backups and monitoring. Only the previously approved qualified Entra
European processing and Microsoft-managed paired-EU ACR artifact exceptions
apply. They do not authorize foreign-region monitoring or a general policy waiver.

## Source and actual local checks

Opaque source scope: `8e02286b466548f4b011ea06560abf93`.

| Source | Immutable identity |
| --- | --- |
| Private index | `apex-private-policy://fulcrum/8e02286b466548f4b011ea06560abf93/04-policy-feasibility.json` |
| Index SHA256 | `538ee1199cba7f70c6182f036dba02bc3e03e258ec9ccab7476a1bc20e1b7796` |
| Private snapshot | Same opaque scope, `subscription-1.json` |
| Snapshot SHA256 | `98edd9c9aa613ce65a3e8dd86f3cfc30fd640dccacb0208c3ccd13f5fd9e3dff` |
| Discovery signature | `sha256:7c229c364db863e37de347eb2a53726f0de4d7566e3d1ddf5c4d178556d82292` |
| Original discovery / expiry | `2026-11-10T06:51:00Z` / `2026-11-17T06:51:00+00:00`; seven days, not restamped |
| Actual runtime integrity check | `2026-11-10T07:05:48.747260+00:00` |
| Local validation | Exact hashes, shared canonical signature, runtime TTL, shared Ajv2020 schema, exact private scope/index and inherited-scope consistency **PASS** |
| Privacy | Managed owner-only external directory `0700`, files `0600`; selector-only reads, no identifying policy payload in public outputs |

Nine assignments comprise three subscription and six inherited assignments.
All 71 expanded records have Default enforcement, no exclusions/selectors or
covering exemptions. Full Defender collection remains included. No resource
inventory, network, Azure, pricing or reviewer calls were made in this slice.
Tenant-match evidence was reused, not rerun or guessed from an active account.

All **69 approved consumed inputs** were compared with current recall.
Current recall has **70 records**: the prior authorized `policy_source` change
to tenant and addition of opaque `azure_read_scope` are the only value deltas.
The older named ledger contains **66**, not 69; neither it nor the frozen
69-input projection was rewritten. Requirements, rev2 manifest/LRS user pin,
17-line cost evidence, optional Design and approval receipts remain unchanged.

## Every Deny condition versus the approved design

All conditions below come from the canonical snapshot, including effective
parameters and scope controls—not policy display names.

| Opaque policy reference | Actual effective condition/property | Owner reconciliation |
| --- | --- | --- |
| `policy-3051731b0239c6f4` | VM/VMSS SKU in effective 17-item blocked set and priority not Spot | **Compatible:** D2as_v5 and compared D2s_v5 are absent from this set; on-demand stays. |
| `policy-f7430a9147179ef4` | Same condition, separate effective 44-item set | **Compatible:** neither approved/compared runner SKU matches. |
| `policy-50c2009f31a13487` | Same condition, separate effective 64-item set | **Compatible:** neither approved/compared runner SKU matches. |
| `policy-698afb784acd4256` | AKS `agentPoolProfiles[*]` count greater than 10 | **Out of scope:** no AKS. |
| `policy-801388434e7a5c32` | VMSS capacity exists, nonempty, guarded numeric capacity greater than 10 | **Out of scope:** one standalone VM, no VMSS. |
| `policy-433af166f71690e6` | Cognitive Services deployment `sku.name=ProvisionedManaged` | **Out of scope:** no such service. |
| `policy-b14dda4a68790a30` | Workspace `sku.capacityReservationLevel>100` | **Compatible:** approved usage-based Analytics Logs allocation has no capacity reservation. |
| `policy-198877c72ad6081c` | SQL server without Entra-only administrator authentication, outside managed-service exclusion and allowed tag branch | **Out of scope:** no SQL server; no exception tag adopted. |
| `policy-742bc6652d3adbf8` | SQL MI without Entra-only administrator authentication and allowed tag branch | **Out of scope:** no SQL MI. |
| `policy-7a76e060e7a5a2cc` | `type` in effective 57-item classic-resource deny set and type exists | **Compatible:** selected modern ARM resources do not match; not a ban on modern service-owned public IPs, disks or NSGs. |
| `policy-90f8749e4e1ec9c0` | Managed HSM with `enablePurgeProtection` equal to string `true`, outside allowed tag branch | **Out of scope:** no HSM/vault. Actual unusual polarity retained, not reversed from a title. |
| `policy-0bc6f85e98967646` | Ring-dependent condition AND one of seven classic service types | **Out of scope:** modern selected types make conjunction false regardless of unresolved ring/tag values. |
| `policy-d2d9ba61572c3cbf` | `location=westeurope` | **Compatible:** Sweden Central does not match. This is an exclusion, not an allowed-region allowlist. |

No Deny match depends on disclosing a real principal, tag contact value, DNS zone
identifier or future resource-group name.

## Modify, DINE and Audit — applicability is not a deployment verdict

The JSON receipt maps **every one of the 58** non-Deny records to its opaque
reference and private source ordinal. These groups partition all 58 records.

| Group | Count | Evidence-backed design impact / limit |
| --- | ---: | --- |
| Subscription DINE | 14 | Retained `if` matches subscription. Missing deployment/existence bodies leave products, destinations, permissions and cost ownership **unknown**. Two carry `WestUS2`; do not infer data movement from an RG/location parameter alone. |
| DINE excluded by complete retained `if` | 31 | Unselected service types, Windows-only VM condition, or Functions/workflow app kinds. In particular, `policy-15ea63f06623214f` and `policy-43fea2076ec2a3f1` do **not** select the ordinary Linux container web app merely because their type is `Microsoft.Web/sites`. |
| VM Modify | 2 | Extracted identity values include `SystemAssigned`, but target property, applicability and complete operations are absent. Existing runner MI intent is compatible in principle, not exact verified policy implementation. |
| Data Modify settings aligned | 5 | Storage public Blob=false, shared key=false, public network=Disabled; Cosmos disableLocalAuth=true and public network=Disabled agree with approved design. Full applicability/operations remain unknown. |
| Other Modify extracted types outside plan | 6 | Event Hubs, Service Bus, Cognitive Services, ML, Key Vault and SQL are unselected. Because full `if` is absent, extracted-type screening is **not** a stronger full-rule exclusion proof. |
| Audit/AuditIfNotExists | 245 summary results | Individual rules/parameters are absent; item-level operational assessment is unavailable. Counts are not Deny failures, resource violations, risk acceptances or cost quantities. |

Subscription parameters also include enabled scanning/data-discovery flags and a
per-storage-account scanning cap. A cap is not observed usage. Without deployment
bodies these do not establish applicable workload charges, ownership or regional
processing. No policy exception tags, exemption, disabling or remediation is adopted.

## Exact requested design checks

| Area | Actual result |
| --- | --- |
| Required RG tags/casing and RG same-region rule | `tags_required=[]`; none of the 13 Deny rules establishes required RG tag keys/casing or resource/RG location equality. Exception-tag parameters are not required RG tags. Do not represent the generic nine-tag fallback as tenant policy. Audit-only controls remain unassessed. |
| Allowed locations | `allowed_locations=[]` is not an unrestricted-tenant certification. The retained regional Deny excludes `westeurope`; Sweden Central stays. |
| App B1 / ACR Premium / Cosmos Serverless / GPv2 LRS | No demonstrated in-scope Deny requires changing these selections, adding replicas or changing the sole LRS user pin. |
| Runner / disk / ephemeral lifecycle | D2as_v5 is not in any of the three blocked sets. No retained applicable Deny mandates a different P6 disk or lifetime. VM Modify exact operations and supported Ubuntu/identity/extension bindings remain unresolved; no new agent, CMK or ephemeral-OS-disk requirement inferred. |
| Network / public IPs / NSGs / routing | No demonstrated rule forces UDR, central firewall, WAF, persistent NAT, a modern public-IP ban or changed subnets. Keep four approved rows, NSG auto, no route tables, runner-only NAT, two managed-service public IPs and PE policies Disabled. No public VM NIC, VPN/P2S or app-through-80h-NAT workaround. |
| Central private DNS | Actual central ownership, zone/record/link IDs and permissions remain unknown; no retained matching rule proves the assumed DNS DINE binding. This is a technical dependency, not an actual denied match or inventory-read authority. Four-zone allocation is not duplicate deployment/ownership proof. |
| Public Monitor / 30-day retention | No inspected Deny forces AMPLS/private ingestion or longer retention; omitted Audit and subscription DINE bodies prevent a blanket permission claim. Authenticated public monitoring and 730h independent app egress remain conditional exactly as approved. |
| No Key Vault / managed identity | No retained applicable condition requires a vault. Preserve secretless MI/platform HTTPS; exact VM Modify and principal grants require evidence/binding, not contact questionnaires. |
| Recovery / minimal alerts | No demonstrated rule changes paid 30-day Cosmos recovery, Blob PITR/prerequisites, operational alerts or approved DEV minimal cost monitoring. Missing rule coverage is not permission to waive policy. |

DNS/link/RBAC/image/SDK/alert-recipient bindings, capacity/overlap and eventual
deployment validation remain technical prerequisites. No real identity, tag
contact value or alert address is requested now. All runtime paths remain
**Unverified**; application implementation and tests remain with the other team.

## Cost consequences — preserved, not repriced

The protected COMPLETE worker contract remains **USD168.104995/month** and
**USD2017.25994/year**, across 17 billable lines. Exact contract hash, decimal
line sum and annualization passed. This is the unchanged **conditional
conservative planning allocation**, not actual spend or a target-verified bill.

No demonstrated constraint yet mandates a new project resource, SKU, quantity,
retention or provisioned lifetime. Therefore no new total or mandatory repricing
is asserted. Conversely, pricing feasibility is **not fully resolved**:
subscription DINE/Defender/external telemetry and central allocation ownership
remain unknown, not free. New meters or changed scope may require repricing once
the actual bodies/ownership establish an obligation.

Keep all approved 80h access versus 730h host/PE assumptions, four-zone shared
allocation, MGN6GB and separate Bastion5GB paid bounds, recovery quantities and
LRS pin. Pricing remains **35/35 used; zero new queries**. Any required new quote
needs actual pricing-owner scope and an explicit exhausted-allowance extension;
equivalent source reuse does not authorize changing material assumptions.

## Blocking ownership and future authority

| Sequence / owner | Required next action |
| --- | --- |
| 1 — Interactive parent → Governance evidence owner | Resolve missing original effective rule bodies. If they were not retained locally, obtain a separately authorized bounded evidence-recovery task. Do not repeat target/consent, query Azure in this slice, invent definitions or mutate signed L0. This is not a request for user-prepared private files. |
| 2 — Governance/platform/cost-allocation owners → Architect | Establish what the subscription DINEs deploy, whether any workload telemetry/data uses foreign-region services, applicable permissions and who bears incremental costs. Resolve actual DNS ownership and exact Modify obligations. A central RG metadata location alone is not a data-residency decision. |
| 3 — Architect / actual material owner, through parent | Only if evidence establishes a conflict, obtain the specific policy-compliant boundary/topology/SKU/retention/allocation choice. **None is justified now.** Narrow Entra/ACR exceptions are not a monitoring exception; mandatory policy cannot be waived through a checkbox. |
| 4 — Actual recovery/review authority | Before dispatch, grant a bounded recovery/review extension tied to the **actually captured** new source/material projection. Architecture cycle `48012a6e8a889c6bd1e203bc4c61e302d1bb6a291f794d4f1e0d43838a2d55ba` and cost cycle `12a93c25d9249919345a8f90b79db85423f41441d314ae6b768b66af4208c5ba` are each **2/2 used**. No reset, automatic new cycle or premanufactured extension projection. |
| 5 — Independent architecture and cost reviewers, later | Freeze actual affected owner artifacts/source projection and the exact private index **plus every snapshot**, their hashes, and the COMPLETE pricing contract/consumed evidence. Authorized private read mapping stays private. Formal Governance additionally requires its exact canonical private JSON only after formal execution is authorized. |
| 6 — Interactive parent | After current independent reviews and resolved blockers, consider any applicable human gate. **No premature Gate2 reapproval now.** Formal Step3.5 remains pending/separately authorized; no Planner/CodeGen/deployment handoff. |

Requirements review remains current. Historical assumed-bundle architecture/cost
approvals and Gate2 `approve_and_continue`/Design `both` remain history, not
restamped target-backed approvals. Current strict review reuse is invalid because
the private supporting inputs were absent; effective Step2/3 assessment views
remain blocked despite historical Step2/3 COMPLETE statuses.

Local protected baseline covers **316 existing project files**, excluding direct
session-state/backup/lock reads, the temporary selector and these two new reports.
Current material inputs, step histories and all 14 review-attempt records are
checked through supported recall, not state-file access. Source/credential changes,
pricing/reviewer calls, Azure/network calls and approved-artifact writes: **zero**.
Private detailed working notes remain owner-only under the managed scope; their
opaque research reference and hashes are in the JSON receipt.

**Return owner:** interactive parent. **Blocking issue:** evidence coverage and
bounded recovery/review authority—not a demonstrated policy violation, a new
material user choice, or missing target/consent.
