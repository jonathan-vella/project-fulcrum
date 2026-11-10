"""Persist a delegated human gate from actual current evidence; never approves."""
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path("/workspaces/project-fulcrum")
PROJECT = ROOT / "agent-output/fulcrum"
META = PROJECT / "_meta"
request_id = "fulcrum-gate2-current69-20261109-184300"
paths = {
    "form": META / "02-gate2-native-form.json",
    "context": META / "02-gate2-question-context.json",
    "envelope": META / "02-gate2-input-request.json",
    "validation": META / "02-gate2-form-validation.json"
}
for path in paths.values():
    if path.exists():
        raise SystemExit(f"Refusing existing Gate2 file: {path}")
session = json.loads(subprocess.check_output(["apex-recall", "show", "fulcrum", "--json"]))["session"]
projection = json.loads((META / "assessment-step-2.json").read_text())
assert session["current_step"] == 2 and session["steps"]["2"]["status"] == "in_progress"
assert projection["inputs"] == session["material_inputs"] and len(projection["inputs"]) == 69
assert session["effective_reviews"]["2"]["status"] == "current"
for kind in ["cost-estimate", "architecture"]:
    path = PROJECT / "reviews" / f"challenge-findings-{kind}.json"
    subprocess.run(["node", "tools/scripts/validate-challenger-findings.mjs",
                    "--path", str(path), "--verify-cache"], cwd=ROOT, check=True)
    review = json.loads(path.read_text())
    assert review["overall_assessment"] == "APPROVED" and review["findings"] == []
estimate = json.loads((PROJECT / "contracts/02-cost-estimate.conservative-planning-v2.json").read_text())
assert estimate["status"] == "COMPLETE" and len(estimate["resources"]) == 17
assert estimate["monthly_total"] == 168.104995 and estimate["yearly_total"] == 2017.25994
form = {
    "message": """Gate2 — Project Fulcrum DEV Architecture. The complete architecture, cost report, SKU comparison/manifest view and all three PNG/SVG chart pairs are ready for your stage decision. The unchanged69 inputs are preserved; no settled usage, SKU, residency, network or policy-source choice is being repeated.

WAF design scores/confidence: Security7/10 Medium; Reliability5/10 Medium; Performance6/10 Low; Cost Optimization8/10 Medium; Operational Excellence6/10 Medium. These are design scores, not deployed-control measurements.

Verified full17-line conservative planning scenario: USD168.104995/month; USD2017.25994/year. It is below your USD500–2,000/month soft planning range, not a hard-cap/spend authorization or invoice prediction. Current adopted transfer remains app1decimalGB + NAT5GB = MGN6GB at its own highest verified paid native rate, separateBastion5GB at Bastion's own highest verified paid native rate; no shared free entitlement or discount. The last authorized continuation used exactly0MCP/1direct, cumulative35/35; no request allowance remains.

Both actual independent reviews are APPROVED, riskMedium, strict-cache valid: cost-feasibility0findings; architecture comprehensive0findings. There are no reviewer findings requiring disposition and no closure call was used.

Assumed Corp policies—not tenant-verified; DEV Architecture-only. Remaining explicit design limitations: single-region/non-zonal/single-workerDEV exposure; runtime identity/SDK/image/privateDNS/alert bindings and performance/recovery objectives remain Unverified. Actual target policies, centralDNS ownership and applicable dependency reconciliation are mandatory before planning completion, CodeGen or deployment. Shared corporate-policy costs outside this17-line project scenario are unknown, not free. Minimal cost monitoring retains budget and operational alerts; its effective human Owner recipient must be verified later. Qualified Entra-European and ACR-managed pairedEU-artifact exceptions remain narrow and unchanged.

Approve and continue authorizes completing this Architecture stage and continuing only through the existing owner/routing process; the parent must collect the still-unset optionalDesign selection before dispatch. Approve and pause approves only the current stage and stops continuation. Revise returns your requested changes to the proper owner. Stop/cancel grants no approval. None of these choices authorizes spending, Azure operations, deployment, deletion, Production or an individual remediation.""",
    "requestedSchema": {
        "properties": {
            "architecture_gate2_decision": {
                "type": "string",
                "title": "Fulcrum Gate2 — current DEV Architecture stage decision",
                "description": "Choose the current stage outcome. Approval covers the exact reviewed bundle and its conservative scenario/Corp qualifications, not deployment or spending. You may enter custom revision instructions in this same field; ambiguity must be resolved rather than treated as approval.",
                "enum": ["approve_and_continue", "approve_and_pause", "revise", "stop"],
                "enumNames": [
                    "Approve current Architecture and continue via the existing optional Design / Governance routing",
                    "Approve current Architecture and pause; do not dispatch the next owner",
                    "Revise; do not approve the current stage",
                    "Stop; no Architecture approval or continuation"
                ]
            }
        }
    }
}
context = {
    "answers": {key: value["value"] for key, value in session["material_inputs"].items()},
    "fields": {
        "architecture_gate2_decision": {"input_id": "architecture_gate2_decision", "kind": "approval"}
    }
}
spec = importlib.util.spec_from_file_location("question_validator", ROOT / "tools/scripts/validate_question_batching.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
errors = module.validate_payload(form, context, require_context=True)
assert errors == [], errors
envelope = {
    "status": "USER_INPUT_REQUIRED", "request_id": request_id,
    "request_id_source": "apex-local", "project": "fulcrum",
    "execution_mode": "delegated", "phase": "gate_2_human_approval",
    "needed_inputs": ["architecture_gate2_decision"],
    "form_path": "agent-output/fulcrum/_meta/02-gate2-native-form.json",
    "context_path": "agent-output/fulcrum/_meta/02-gate2-question-context.json",
    "review_receipt_path": "agent-output/fulcrum/_meta/02-review-publication-receipt.json",
    "cost_path": "agent-output/fulcrum/contracts/02-cost-estimate.conservative-planning-v2.json",
    "gate2_ready_to_ask": True, "gate2_approved": False,
    "step2_complete": False, "optional_design_choice": "Not yet answered; ask only after actual continue trigger",
    "parent_action": "Read exact native form and separate context; validate_payload(require_context=True); pass only form.message/form.requestedSchema to native ask_user unchanged. Preserve this local correlation ID with actual response. Do not complete/dispatch on task output, independent review or cancellation."
}
validation = {
    "request_id": request_id, "status": "PASS",
    "validate_payload_require_context_errors": errors,
    "current_material_record_count": 69, "all_answers_exactly_equal_recall": True,
    "required_reviews": "Both APPROVED,0findings, strict current",
    "closure_calls": 0, "stage_approved": False,
    "schema_root_properties_only": True, "default_approval": False,
    "repeated_settled_inputs": False, "unconditional_companion_fields": False
}
for key, value in [("form", form), ("context", context), ("envelope", envelope), ("validation", validation)]:
    paths[key].write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    json.loads(paths[key].read_text())
for name in ["README.md", "00-handoff.md"]:
    archive = META / ("02-pre-gate2-" + name.lower())
    assert not archive.exists()
    archive.write_bytes((PROJECT / name).read_bytes())
print(json.dumps({"request_id": request_id, "errors": errors,
                  "form_path": envelope["form_path"], "context_path": envelope["context_path"],
                  "input_count": len(context["answers"]), "status": "USER_INPUT_REQUIRED"}))
