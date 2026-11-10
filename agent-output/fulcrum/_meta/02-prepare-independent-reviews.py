"""Generate request contracts from actual metadata; never calls a reviewer."""
import json
import hashlib
import subprocess
from pathlib import Path

ROOT = Path("/workspaces/project-fulcrum")
PROJECT = "agent-output/fulcrum/"
policy_view = ROOT / (PROJECT + "_meta/02-assumed-corp-review-evidence.json")
if policy_view.exists():
    raise SystemExit(f"Refusing existing policy view: {policy_view}")
policy_source = ".github/data/alz-corp-policy-baseline.json.gz"
policy_hash = hashlib.sha256((ROOT / policy_source).read_bytes()).hexdigest()
assert policy_hash == "97c367dc6ab1950e34d5e59fa8fef5d1afaff34b0a2f4b9a458cc539b1e2a2ed"
envelope = json.loads(subprocess.check_output([
    "python", ".github/skills/apex-azure-governance-discovery/scripts/governance_baseline.py",
    policy_source, "--alz-default", "--compact"
], cwd=ROOT, text=True))
names = {
    "Deny-HybridNetworking", "Deny-IP-forwarding", "Deny-MgmtPorts-Internet",
    "Deny-Public-Endpoints", "Deny-Public-IP-On-NIC",
    "Deny-Subnet-Without-Nsg", "Deploy-Private-DNS-Zones"
}
selected = [x for x in envelope["policies"] if x["assignment_id"].split("/")[-1] in names]
assert {x["assignment_id"].split("/")[-1] for x in selected} == names
view = {
    "evidence_kind": "Public shared policy library projection, NOT tenant evidence",
    "qualification": "Assumed Corp policies—not tenant-verified; DEV Architecture-only.",
    "source_path": policy_source, "source_sha256": policy_hash,
    "reader": "governance_baseline.py --alz-default --compact",
    "selection": sorted(names),
    "selection_boundary": "Only the seven assignments consumed by Architecture; other library policies and tenant customizations remain outside this bounded projection. Original shared gzip is also frozen.",
    "library_provenance": envelope["provenance"],
    "synthetic_scope_warning": "Any source scope/assignment identity below belongs to the public library's synthetic envelope; not an actual tenant, target or deployed assignment.",
    "policies": selected
}
policy_view.write_text(json.dumps(view, ensure_ascii=False, indent=2) + "\n")
json.loads(policy_view.read_text())
supporting = [
    PROJECT + "01-requirements.md",
    PROJECT + "03-des-sku-comparison.md",
    PROJECT + "_meta/assessment-step-2.json",
    PROJECT + "_meta/01-gate1-acr-revision-response-receipt.json",
    PROJECT + "_meta/02-assumed-corp-acceptance-receipt.json",
    ".github/data/alz-corp-policy-baseline.json.gz",
    PROJECT + "_meta/02-assumed-corp-review-evidence.json",
    PROJECT + "_meta/02-entra-residency-exception-receipt.json",
    PROJECT + "_meta/02-acr-residency-response-receipt.json",
    PROJECT + "_meta/02-confirmed-network-binding.json",
    PROJECT + "_meta/02-proposed-new-vnet-subnet-plan.json",
    PROJECT + "_meta/02-private-usage-normalization.json",
    PROJECT + "_meta/02-sku-network-meter-normalization.json",
    PROJECT + "_meta/02-monthly-planning-response-receipt.json",
    PROJECT + "_meta/02-monthly-planning-normalization.json",
    PROJECT + "_meta/02-bastion-evidence-extension-response-receipt.json",
    PROJECT + "_meta/02-final-dependency-closure.md",
    PROJECT + "_meta/02-final-official-evidence.json",
    PROJECT + "_meta/02-artifact-research-supplement.md",
    PROJECT + "_meta/02-cost-estimate-request.json",
    PROJECT + "_meta/02-cost-conservative-planning-request.json",
    PROJECT + "_meta/02-cost-conservative-planning-v2-request.json",
    PROJECT + "_meta/02-cost-conservative-planning-v2-validation.json",
    PROJECT + "_meta/02-cost-recovery-3-archive-receipt.json",
    PROJECT + "_meta/02-pricing-public-docs",
    PROJECT + "contracts/02-cost-estimate.conservative-planning-v2.json",
    PROJECT + "contracts/02-cost-estimate.conservative-planning-v2.json.retail-evidence",
    PROJECT + "contracts/02-cost-estimate.recovery-3.json",
    PROJECT + "contracts/02-cost-estimate.recovery-3.json.retail-evidence",
    PROJECT + "contracts/02-cost-estimate.conservative-planning-v1.json",
    PROJECT + "contracts/02-cost-candidates-app-host.json",
    PROJECT + "contracts/02-cost-candidates-document-store.json",
    PROJECT + "contracts/02-cost-candidates-access-compute.json",
]
for name in ["02-waf-scores", "03-des-cost-distribution", "03-des-cost-projection"]:
    supporting.extend(PROJECT + "assets/" + name + suffix for suffix in [".py", ".png", ".svg"])

instruction = """## Inputs
Read the exact primary and captured supporting inputs using .github/skills/apex-azure-defaults/references/one-shot-review.md and applicable WAF/security/governance/cost/template checklists. This is greenfield DEV delivery practical-v1, default review depth, same existing Step2 cycle, initial pass1. Both independent lenses are required. No reviewer has yet been dispatched for Step2. Assumed Corp policies—not tenant-verified; DEV Architecture-only. Shared gzip is an accepted library, not live tenant evidence; do not infer IDs, deployed policy, DNS ownership or runtime tests. All69 current material records are in assessment-step-2.json; earlier66 ledger/history and pending prose are historical where actual later receipts supersede them. Current Step1 approval is separate from unchanged Requirements wording.
## Activities
Independently assess the entire artifact and its actual evidence, not the producer's hoped-for verdict. Check capability paths, maturity/version confidence, WAF scores and sizing, dependency closure, residency exceptions, recovery limits, selective730h app versus80h runner NAT, NSG/PE/DNS semantics and anonymous infrastructure-only scope. Tenant verification remains mandatory before planning completion/CodeGen/deploy, not an Architecture target-ID gate under accepted Corp assumptions. Pricing owner COMPLETE conservative-planning-v2 is actual current evidence for all17 lines, not historical FAILED subtotals. Verify equations, native unit/rate provenance, lifetime/backup/shared allocations and full current69 applicability. Approved additionalapp1GB+NAT5=MGN6GB at own highest verified paid native rate; separateBastion5GB at its OWN highest verified paid native rate with new complete raw5tiers/nullNextPageLink. No free credit/discount/actual invoice tier claimed. Independently judge appropriateness of that conservative scenario; owner preference cannot certify tariff facts or excuse missing evidence. Final new0MCP/1direct, cumulative35/35; historical comparisons separate. BudgetUSD500–2000 is a soft planning range, not a hard cap. Runtime paths remain Unverified. Existing source references in historical FAILED contracts must remain immutable; these are not current totals.
Read only supplied/linked existing paths with valid ranges; short files without ranges. No shell/code execution, file writes including scratch, direct session-state reads, delegation, Azure access or user questions. The shared gzip is frozen for source integrity; 02-assumed-corp-review-evidence.json is the deterministic, hash-bound readable projection of the seven consumed assignments produced through the documented governance_baseline.py reader. Read that bounded projection; do not try to execute code to decompress gzip. It is not a tenant discovery envelope. If other essential evidence is inaccessible, return that exact issue rather than guessing. Do not treat proposals as deployed facts or later implementation bindings as automatically fatal at design scope.
## Outputs
Return exactly one complete raw JSON object beginning{ending}, schema_version1.0, challenged_artifact, matching artifact_type/review_focus/pass_number, independent overall_assessment and risk_level, findings, exact unchanged cache_inputs/supporting_inputs. Each finding uses traces_to array and required substantive fields; must_fix includes suggested_fix.artifact_path/proposed_edit. Omit IDs, severity counts and review_execution; actual recorder derives those. No fence, introduction or conclusion."""

for artifact, kind, focus in [
    ("02-architecture-assessment.md", "architecture", "comprehensive"),
    ("03-des-cost-estimate.md", "cost-estimate", "cost-feasibility"),
]:
    request_path = ROOT / (PROJECT + f"_meta/02-review-request-{kind}.json")
    if request_path.exists():
        raise SystemExit(f"Refusing existing request: {request_path}")
    other = "03-des-cost-estimate.md" if kind == "architecture" else "02-architecture-assessment.md"
    inputs = supporting + [PROJECT + other]
    for path in inputs:
        if not (ROOT / path).exists():
            raise SystemExit(f"Missing exact supporting input: {path}")
    command = ["node", "tools/scripts/validate-challenger-findings.mjs",
               "--metadata", PROJECT + artifact, "--reviewer", "challenger-review-subagent"]
    for path in inputs:
        command.extend(["--supporting-input", path])
    metadata = json.loads(subprocess.check_output(command, cwd=ROOT, text=True))
    request = {
        "request_id": f"fulcrum-step2-{kind}-initial-20261109",
        "step": "2", "review_depth": "default",
        "artifact_path": PROJECT + artifact, "project_name": "fulcrum",
        "artifact_type": kind, "review_focus": focus, "pass_number": 1,
        "prior_findings": None,
        "output_path": PROJECT + f"reviews/challenge-findings-{kind}.json",
        "overwrite": False,
        **metadata,
        "instructions": instruction,
    }
    request_path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n")
    json.loads(request_path.read_text())
    print(json.dumps({"request_path": str(request_path.relative_to(ROOT)),
                      "request_id": request["request_id"],
                      "supporting_input_count": len(inputs)}))
