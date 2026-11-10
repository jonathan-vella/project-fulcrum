"""Bounded mechanical archive and linked ordinary review lifecycle; no review authorship."""
import datetime as dt
import hashlib
import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path("/workspaces/project-fulcrum")
P = ROOT / "agent-output/fulcrum"
PREFIX = "agent-output/fulcrum/"
META = P / "_meta"
RECEIPT = META / "02-delivery-residue-archive-map.json"
KINDS = ("cost-estimate", "architecture")
INITIAL = {
    kind: f"fulcrum-step2-{kind}-initial-20261109" for kind in KINDS
}
REQUEST_ID = {
    kind: f"fulcrum-step2-{kind}-archive-closure-20261109-2052" for kind in KINDS
}
MAPPING = {
    PREFIX + "02-waf-research.tmp.md":
        PREFIX + "_meta/step2-delivery-residue-archive/02-waf-research.md",
    **{
        PREFIX + f"contracts/02-cost-estimate.{name}.json":
            PREFIX + f"_meta/step2-delivery-residue-archive/02-cost-estimate.{name}.json"
        for name in ("conservative-planning-v1", "recovery-1", "recovery-2", "recovery-3")
    },
}


def load(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args):
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"{args}: exit {result.returncode}\n{result.stdout}\n{result.stderr}")
    return result.stdout


def persist_new(path, value):
    with path.open("x", encoding="utf-8") as target:
        target.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    assert load(path) == value


def recall():
    return json.loads(run(["apex-recall", "show", "fulcrum", "--json"]))["session"]


def request_path(kind):
    return META / f"02-review-request-{kind}-archive-closure.json"


def metadata(primary, paths):
    args = [
        "node", "tools/scripts/validate-challenger-findings.mjs",
        "--metadata", primary, "--reviewer", "challenger-review-subagent",
    ]
    for path in paths:
        args += ["--supporting-input", path]
    return json.loads(run(args))


def archive():
    assert not RECEIPT.exists()
    session = recall()
    projection = load(META / "assessment-step-2.json")
    assert projection["inputs"] == session["material_inputs"]
    assert len(projection["inputs"]) == 69
    step2_cycles = [v for v in session["decisions"]["review_cycles"].values() if v["step"] == "2"]
    assert len(step2_cycles) == 2
    assert all(v["calls"] == 1 and v["max_calls"] == 2 for v in step2_cycles)
    assert {v["projection"] for v in step2_cycles} == {
        "9ecc1ef96f5ad0c3f9f557129b95534f897ed295b06088536c30377392427707"
    }
    protected = set()
    supporting = {}
    initial_reviews = []
    for kind in KINDS:
        original_path = META / f"02-review-request-{kind}.json"
        original = load(original_path)
        review_path = ROOT / original["output_path"]
        run(["node", "tools/scripts/validate-challenger-findings.mjs",
             "--path", str(review_path), "--verify-cache"])
        review = load(review_path)
        assert review["overall_assessment"] == "APPROVED" and review["findings"] == []
        assert review["review_execution"]["request_id"] == INITIAL[kind]
        protected.update([original["artifact_path"], str(original_path.relative_to(ROOT)),
                          str(review_path.relative_to(ROOT))])
        initial_reviews.append({
            "request_id": INITIAL[kind], "path": str(review_path.relative_to(ROOT)),
            "sha256": sha(review_path),
            "status_after_archive": "Historical actual APPROVED result; old supporting identity intentionally no longer current.",
        })
        current_meta = metadata(original["artifact_path"], [x["path"] for x in original["supporting_inputs"]])
        assert current_meta["cache_inputs"] == original["cache_inputs"]
        assert current_meta["supporting_inputs"] == original["supporting_inputs"]
        for item in original["supporting_inputs"]:
            supporting[item["path"]] = item["sha256"]
            if (ROOT / item["path"]).is_file():
                protected.add(item["path"])
    protected.update(PREFIX + x for x in (
        "contracts/sku-manifest.json", "sku-manifest.md",
        "_meta/02-gate2-response-receipt.json",
        "_meta/02-optional-design-response-receipt.json",
        "_meta/02-current-material-input-ledger.json",
        "reviews/challenge-findings-requirements-acr-revision.json",
        "reviews/challenge-findings-architecture-decisions.json",
        "_meta/02-review-publication-receipt.json",
    ))
    protected_hashes = {path: sha(ROOT / path) for path in sorted(protected) if path not in MAPPING}
    entries = []
    for old, new in MAPPING.items():
        src, dst = ROOT / old, ROOT / new
        assert src.is_file() and not src.is_symlink() and not dst.exists()
        if src.suffix == ".json":
            assert load(src)["status"] == "FAILED"
        entries.append({"old_path": old, "archive_path": new, "sha256": sha(src)})
    receipt = {
        "schema_version": "step2-mechanical-archive-v1",
        "captured_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "project": "fulcrum", "step": "2",
        "authority": "Current delegated owner instruction: byte-equivalent delivery-residue archive and each existing ordinary closure; no material/pricing/source changes.",
        "operation": "No-overwrite rename of five files. Raw retail directories remain in place. Historical paths in immutable source/query/approval/review records resolve via this map; those records are not rewritten.",
        "original_gate2_receipt": PREFIX + "_meta/02-gate2-response-receipt.json",
        "primary_bytes_changed": False,
        "approval_statement": "Actual earlier approve_and_continue remains recorded for the same unchanged primary bundle; this operation is not a new human answer.",
        "material_projection_sha256": step2_cycles[0]["projection"],
        "material_records": 69,
        "prearchive_cycles": step2_cycles,
        "initial_reviews": initial_reviews,
        "archive_mapping": entries,
        "protected_file_sha256": protected_hashes,
        "prearchive_declared_supporting_sha256": supporting,
        "pricing_new_calls": 0,
        "completion_or_transition_authorized": False,
    }
    persist_new(RECEIPT, receipt)
    for item in entries:
        src, dst = ROOT / item["old_path"], ROOT / item["archive_path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        assert sha(src) == item["sha256"] and not dst.exists()
        src.rename(dst)
        assert not src.exists() and sha(dst) == item["sha256"]
        if dst.suffix == ".json":
            assert load(dst)["status"] == "FAILED"
    print(json.dumps({"archive_map": str(RECEIPT.relative_to(ROOT)), "sha256": sha(RECEIPT),
                      "mapping": entries}, indent=2))


INSTRUCTIONS = """## Inputs
Use .github/skills/apex-azure-defaults/references/one-shot-review.md and its applicable WAF/security/governance/cost/template checklists. This is the ordinary closure of this lens's original Step2 initial review, not a new cycle. Actual original findings are []. Independently judge the current artifact and evidence without a predetermined verdict. Read the supplied archive map first: five residue files were renamed byte-for-byte; historical old locations in immutable ledgers, primary documents and prior reviews resolve through that map. Original reviews remain historical unchanged. All approved primary documents, SKU comparison, manifest, current COMPLETE pricing, 69 material values and raw retail directories are unchanged. No new pricing, source repair or architecture decision.
## Activities
Verify the archive identity/location repair and the artifact's continued evidence integrity in this lens. Read current COMPLETE conservative-planning-v2, current69 projection, supplied official evidence and complete dependency closure. DEV-only Assumed Corp policies, not tenant-verified; target verification is mandatory before planning completion/CodeGen/deploy, not now. Runtime stays Unverified. Existing qualified Entra-European and ACR managed-paired-EU-artifact exceptions only; all other workload scope Sweden Central. The approved conditional conservative scenario is not measured spend/invoice tiers/free entitlement: additional app1GB+NAT5=MGN6GB and separate Bastion5GB each own highest verified paid native rate; native GB/TB/Tb distinctions preserved. All17 lines are COMPLETE, historical FAILED costs are not current totals. Existing pricing35/35 unchanged; no pricing authorized. Reconcile any source locations only via the immutable map, without asking for primary/source/history edits. Read the bounded supplied Corp projection, not code execution to decompress gzip. Read only supplied/linked existing paths with valid ranges, short files without ranges. No shell, code, writes/scratch, direct session-state access, delegation, Azure access or user questions. Missing essential context is an explicit failure, not guessed evidence.
## Outputs
Return exactly one raw JSON object with schema_version1.0, challenged_artifact, matching artifact_type/review_focus/pass_number, independent overall_assessment and risk_level, findings, and exact unchanged cache_inputs/supporting_inputs. Each finding uses substantive required fields and traces_to array; must_fix includes suggested_fix.artifact_path/proposed_edit. Omit IDs, severity counts and review_execution. No fence or introduction."""


def prepare():
    receipt = load(RECEIPT)
    for kind in KINDS:
        original = load(META / f"02-review-request-{kind}.json")
        paths = [MAPPING.get(x["path"], x["path"]) for x in original["supporting_inputs"]]
        paths += [str(RECEIPT.relative_to(ROOT))]
        captured = metadata(original["artifact_path"], paths)
        assert captured["cache_inputs"] == original["cache_inputs"]
        expected = {MAPPING.get(x["path"], x["path"]): x["sha256"]
                    for x in original["supporting_inputs"]}
        assert {x["path"]: x["sha256"] for x in captured["supporting_inputs"]
                if x["path"] != str(RECEIPT.relative_to(ROOT))} == expected
        req = {
            **original,
            "request_id": REQUEST_ID[kind], "prior_findings": [],
            "output_path": PREFIX + f"reviews/challenge-findings-{kind}-archive-closure.json",
            "cache_inputs": captured["cache_inputs"],
            "supporting_inputs": captured["supporting_inputs"],
            "instructions": INSTRUCTIONS,
        }
        assert not (ROOT / req["output_path"]).exists()
        persist_new(request_path(kind), req)
        preflight = json.loads(run(["node", "tools/scripts/record-review.mjs",
                                    "--preflight", "--request", str(request_path(kind))]))
        persist_new(META / f"02-review-preflight-{kind}-archive-closure.json", preflight)
        print(json.dumps({"kind": kind, "request_path": str(request_path(kind).relative_to(ROOT)),
                          "preflight": preflight}, indent=2))


def verify():
    receipt = load(RECEIPT)
    for path, digest in receipt["protected_file_sha256"].items():
        assert sha(ROOT / path) == digest, path
    for item in receipt["archive_mapping"]:
        assert not (ROOT / item["old_path"]).exists()
        assert sha(ROOT / item["archive_path"]) == item["sha256"]
    session = recall()
    projection = load(META / "assessment-step-2.json")
    assert len(projection["inputs"]) == 69 and projection["inputs"] == session["material_inputs"]
    # Execute the existing read-only validator unchanged, with only read-path
    # resolution for the two historical JSON identities. No source bytes altered.
    validator = META / "02-cost-conservative-planning-v2-validation.py"
    source = validator.read_text()
    native_read_bytes = Path.read_bytes
    native_read_text = Path.read_text

    def resolved(path):
        relative = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
        return ROOT / MAPPING[relative] if relative in MAPPING else path

    def read_bytes(path):
        return native_read_bytes(resolved(path))

    def read_text(path, *args, **kwargs):
        return native_read_text(resolved(path), *args, **kwargs)

    Path.read_bytes, Path.read_text = read_bytes, read_text
    try:
        exec(compile(source, str(validator), "exec"), {"__name__": "__main__"})
    finally:
        Path.read_bytes, Path.read_text = native_read_bytes, native_read_text
    for kind in KINDS:
        req = load(request_path(kind))
        captured = metadata(req["artifact_path"], [x["path"] for x in req["supporting_inputs"]])
        assert captured["cache_inputs"] == req["cache_inputs"]
        assert captured["supporting_inputs"] == req["supporting_inputs"]
    from apex_recall.step2_gate import step2_residue
    assert step2_residue("fulcrum") == []
    cost = load(P / "contracts/02-cost-estimate.conservative-planning-v2.json")
    assert cost["status"] == "COMPLETE" and len(cost["resources"]) == 17
    assert sum(Decimal(str(x["monthly_cost"])) for x in cost["resources"]) == Decimal(str(cost["monthly_total"]))
    print(json.dumps({
        "status": "PASS_UNCHANGED_PROTECTED_INPUTS_AND_EMPTY_RESIDUE",
        "protected_files": len(receipt["protected_file_sha256"]),
        "archive_files": len(receipt["archive_mapping"]),
        "primary_bytes_changed": False, "step2_residue": [],
        "material_records": 69, "cost_lines": 17,
        "monthly_total": cost["monthly_total"], "yearly_total": cost["yearly_total"],
        "validator": "Existing unchanged validator, historical file reads explicitly resolved through immutable archive map only.",
    }, indent=2))


def start(kind):
    req = load(request_path(kind))
    pf = json.loads(run(["node", "tools/scripts/record-review.mjs", "--preflight",
                        "--request", str(request_path(kind))]))
    args = ["apex-recall", "review-audit", "fulcrum", "2",
            "--attempt-id", req["request_id"], "--attempt-kind", "invocation",
            "--attempt-outcome", "started", "--review-request", str(request_path(kind)),
            "--closure-of", INITIAL[kind], "--json"]
    for path in pf["attempt_inputs"]:
        args += ["--attempt-input", path]
    outcome = json.loads(run(args))
    persist_new(META / f"02-review-start-{kind}-archive-closure.json", outcome)
    print(json.dumps(outcome, indent=2))


def finalize():
    verify()
    session = recall()
    current = session["effective_reviews"]["2"]
    assert current["status"] == "current", current
    assert session["gate_readiness"]["step-2-complete"]["status"] == "current"
    assert session["steps"]["2"]["status"] == "in_progress"
    assert session["steps"]["2"]["sub_step"] == "phase_6_gate2_pending"
    assert session["steps"]["3"]["status"] == "pending"
    cycles = {v["lens"]: v for v in session["decisions"]["review_cycles"].values() if v["step"] == "2"}
    assert len(cycles) == 2 and all(v["calls"] == v["max_calls"] == 2 for v in cycles.values())
    manifest_validation = run([
        "node", "tools/scripts/validate-sku-manifest.mjs",
        PREFIX + "contracts/sku-manifest.json",
    ])
    headings = load(ROOT / "tools/scripts/_lib/artifact-headings-summary.json")
    checked_headings = {}
    for name in ("02-architecture-assessment.md", "03-des-cost-estimate.md", "00-handoff.md"):
        observed = [line for line in (P / name).read_text().splitlines() if line.startswith("## ")]
        expected = headings[name]
        assert observed[:len(expected)] == expected, (name, observed, expected)
        if name == "00-handoff.md":
            assert len(observed) == 6
        checked_headings[name] = "PASS"
    readme_required = [
        "## 📋 Project Summary", "## ✅ Workflow Progress", "## 🏛️ Architecture",
        "## 📄 Generated Artifacts", "## 🔗 Related Resources",
    ]
    readme_headings = [line for line in (P / "README.md").read_text().splitlines() if line.startswith("## ")]
    assert readme_headings[:len(readme_required)] == readme_required
    checked_headings["README.md"] = "PASS"
    events_path = load(META / "02-review-publication-receipt.json")["actual_events_path"]
    reconciliation = json.loads(run([
        "apex-recall", "review-audit", "fulcrum", "2",
        "--reconcile-events", events_path, "--json",
    ]))
    audit = {x["request_id"]: x for x in reconciliation["requests"]}
    results = []
    for kind in KINDS:
        req = load(request_path(kind))
        target = ROOT / req["output_path"]
        report = load(target)
        assert report["overall_assessment"] == "APPROVED" and report["findings"] == []
        assert report["review_execution"]["request_id"] == req["request_id"]
        validation = run(["node", "tools/scripts/validate-challenger-findings.mjs",
                          "--path", str(target), "--verify-cache"])
        assert audit[req["request_id"]]["gap"] is False
        assert audit[req["request_id"]]["start_timing"] == "before_dispatch"
        results.append({
            "request_id": req["request_id"], "closure_of": INITIAL[kind],
            "request_path": str(request_path(kind).relative_to(ROOT)),
            "result_path": req["output_path"], "result_sha256": sha(target),
            "artifact_type": kind, "review_focus": req["review_focus"], "pass_number": 1,
            "overall_assessment": report["overall_assessment"], "risk_level": report["risk_level"],
            "findings": report["findings"], "review_execution": report["review_execution"],
            "strict_cache": {"status": "PASS", "errors": 0, "warnings": 0, "actual_output": validation},
            "native_lifecycle": audit[req["request_id"]],
            "cycle": cycles[req["review_focus"]],
        })
    receipt = load(RECEIPT)
    persist_new(META / "02-archive-closure-publication-receipt.json", {
        "status": "MECHANICAL_REPAIR_COMPLETE_PARENT_TRANSITION_READY",
        "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "project": "fulcrum", "step": "2",
        "archive_map": str(RECEIPT.relative_to(ROOT)), "archive_map_sha256": sha(RECEIPT),
        "archive_files_byte_equivalent": 5, "step2_residue": [],
        "protected_files_unchanged": len(receipt["protected_file_sha256"]),
        "material_records": 69, "material_projection_sha256": receipt["material_projection_sha256"],
        "primary_bytes_changed": False, "reapproval_required_by_this_repair": False,
        "input_digest": "e1702bf778d8cfcdc0e8e9064666b7ac69032cb65f64f9547cfeed80aa59d789",
        "actual_events_path": events_path,
        "reviews_in_presentation_order": results,
        "checks": {
            "cost": "PASS: unchanged validator with historical JSON reads mapped through immutable archive receipt; 17 lines, 14 native archives, seven direct envelopes, original freshness.",
            "manifest": manifest_validation,
            "heading_order": checked_headings,
            "strict_cache": "Both attributed closure files PASS; initial review bytes preserved as historical, not revalidated as current.",
            "gate2_readiness": session["gate_readiness"]["step-2-complete"],
        },
        "original_gate2_receipt": PREFIX + "_meta/02-gate2-response-receipt.json",
        "actual_gate2_response": load(META / "02-gate2-response-receipt.json")["actual_response"],
        "actual_optional_design_response": load(META / "02-optional-design-response-receipt.json")["actual_response"],
        "policy_qualification": "Assumed Corp policies—not tenant-verified; DEV Architecture-only.",
        "new_pricing_calls": 0, "pricing_account_unchanged": "35/35; no remaining calls",
        "review_allowances_reset_or_extended": False,
        "step2_status": session["steps"]["2"]["status"],
        "step2_phase": session["steps"]["2"]["sub_step"], "step2_completed_here": False,
        "step3_status": session["steps"]["3"]["status"], "design_dispatched_here": False,
        "next_owner": "Interactive parent: retry approved atomic 2→3 completion/transition; only after success dispatch 04-Design for both diagram and ADRs.",
    })
    print(json.dumps({"status": "MECHANICAL_REPAIR_COMPLETE_PARENT_TRANSITION_READY",
                      "receipt": PREFIX + "_meta/02-archive-closure-publication-receipt.json",
                      "step2_residue": [], "primary_bytes_changed": False}, indent=2))


if __name__ == "__main__":
    action = sys.argv[1]
    if action == "archive":
        archive()
    elif action == "prepare":
        prepare()
    elif action == "verify":
        verify()
    elif action == "start":
        start(sys.argv[2])
    elif action == "finalize":
        finalize()
    else:
        raise SystemExit("Unknown bounded action")
