"""Read-only checks of pricing-owner results; never publishes or authors prices."""
import datetime as dt
import hashlib
import json
import subprocess
from decimal import Decimal as D, ROUND_HALF_UP
from pathlib import Path

ROOT = Path("/workspaces/project-fulcrum")
PROJECT = ROOT / "agent-output/fulcrum"
NOW = dt.datetime.now(dt.timezone.utc)


def load(path):
    return json.loads(Path(path).read_text())


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fresh(stamp):
    elapsed = NOW - dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    assert dt.timedelta(0) <= elapsed <= dt.timedelta(days=30)


def strip(value):
    if isinstance(value, dict):
        return {k: strip(v) for k, v in value.items() if k != "notes"}
    if isinstance(value, list):
        return [strip(v) for v in value]
    return value


request = load(PROJECT / "_meta/02-cost-conservative-planning-v2-request.json")
result_path = ROOT / request["output_path"]
result = load(result_path)
prior = load(PROJECT / "_meta/02-cost-conservative-planning-request.json")
assert result["status"] == "COMPLETE" and result["unresolved_items"] == []
assert len(result["resources"]) == 17
assert result["mcp_calls_used"] == 0 and result["direct_api_calls_used"] == 1
assert result["currency"] == "USD" and result["region"] == "swedencentral"
assert strip(request["manifest_usage"]) == strip(prior["manifest_usage"])
assert strip(request["supplemental_resources"]) == strip(prior["supplemental_resources"])
fresh(result["queried_at"])
assert all(D(str(x["monthly_cost"])).is_finite() and x["monthly_cost"] >= 0
           for x in result["resources"])
assert sum(D(str(x["monthly_cost"])) for x in result["resources"]) == D(str(result["monthly_total"]))
assert D(str(result["monthly_total"])) * 12 == D(str(result["yearly_total"]))
session = json.loads(subprocess.check_output(["apex-recall", "show", "fulcrum", "--json"]))["session"]
projection = load(PROJECT / "_meta/assessment-step-2.json")
assert projection["inputs"] == session["material_inputs"] and len(projection["inputs"]) == 69
historical = load(PROJECT / "_meta/02-current-material-input-ledger.json")["material_inputs"]
assert all(projection["inputs"][key] == value for key, value in historical.items())
binding = result["query_ledger"][1]
assert digest(ROOT / binding["projection_path"]) == binding["projection_sha256"]
validation = result["query_ledger"][2]
assert digest(PROJECT / "contracts/02-cost-estimate.recovery-3.json") == validation["historical_result_sha256"]
assert digest(ROOT / validation["prior_failed_result_path"]) == validation["prior_failed_result_sha256"]
assert digest(ROOT / validation["fixed_equations_path"]) == validation["fixed_equations_sha256"]
assert digest(ROOT / validation["official_semantics_path"]) == validation["official_semantics_sha256"]
for filename, expected in validation["candidate_hashes"].items():
    assert digest(PROJECT / "contracts" / filename) == expected

old = load(PROJECT / "contracts/02-cost-estimate.recovery-3.json")
archive = load(PROJECT / "_meta/02-cost-recovery-3-archive-receipt.json")
native_count = 0
for entry in old["query_ledger"]:
    if entry.get("command") == "pricing_get":
        path = ROOT / (archive["archive_path"] if entry["id"] == "q11" else entry["response_path"])
        assert digest(path) == entry["sha256"]
        response = load(path)
        assert response["status"] == 200 and len(response["results"]["prices"]) == entry["rows"]
        fresh(entry["recorded_at"])
        native_count += 1
assert native_count == 14
semantic = load(PROJECT / "contracts/02-cost-estimate.recovery-3.json.retail-evidence/recovery-validation.json")
for entry in semantic["official_semantic_archives"]:
    assert digest(ROOT / entry["path"]) == entry["sha256"]

direct_count = 0
for source in result["retail_api_evidence"]:
    path = ROOT / source["evidence_path"]
    evidence = load(path)
    assert evidence["query"]["priceType"] == "Consumption" and evidence["query"]["currencyCode"] == "USD"
    assert len(evidence["pages"]) == evidence["requests_used"] == 1
    for page in evidence["pages"]:
        assert hashlib.sha256(page["raw_response"].encode()).hexdigest() == page["response_sha256"]
        body = json.loads(page["raw_response"])
        assert body["NextPageLink"] is None and body["Count"] == len(body["Items"])
        assert all("tierMinimumUnits" in row for row in body["Items"])
        fresh(page["queried_at"])
    direct_count += 1
assert direct_count == 7
latest = result["query_ledger"][-1]
assert latest["requests_used"] == 1 and latest["pagination_requests"] == latest["retry_requests"] == 0
assert digest(ROOT / latest["evidence_path"]) == latest["sha256"]
bastion = load(ROOT / latest["evidence_path"])
assert bastion["query"] == request["exact_new_evidence"]["query"]
rows = json.loads(bastion["pages"][0]["raw_response"])["Items"]
for row in rows:
    for key in ["serviceName", "productName", "skuName", "meterName", "armRegionName", "currencyCode"]:
        assert row[key] == bastion["query"][key]
    assert row["type"] == "Consumption" and row["unitOfMeasure"] == "1 GB"
    assert row["meterId"] == request["exact_new_evidence"]["expected_meter_id"]
mgn = load(ROOT / request["evidence_checks"]["mgn_path"])
assert digest(ROOT / request["evidence_checks"]["mgn_path"]) == request["evidence_checks"]["mgn_sha256"]
mgn_rows = json.loads(mgn["pages"][0]["raw_response"])["Items"]
internet = next(x for x in result["resources"] if x["name"] == "internet-outbound-allocation-dev")
expected = 6 * max(D(str(x["retailPrice"])) for x in mgn_rows) + 5 * max(D(str(x["retailPrice"])) for x in rows)
assert expected == D(str(internet["monthly_cost"]))
fixed = load(ROOT / validation["fixed_equations_path"])
published = {x["name"]: D(str(x["monthly_cost"])) for x in result["resources"]}
for line in fixed["lines"]:
    assert published[line["name"]] == D(str(line["monthly_component_cost_usd"]))

manifest = load(PROJECT / "contracts/sku-manifest.json")
assert manifest["current_revision"] == 2
assert manifest["revisions"][0]["commit_sha"] == "16cd2c7"
for writeback in result["manifest_writeback"]:
    service = next(x for x in manifest["services"] if x["id"] == writeback["id"])
    assert service["cost_estimate_monthly_usd"] == writeback["cost_estimate_monthly_usd"]
    assert service["cost_estimated_at"] == writeback["cost_estimated_at"]
for service in manifest["services"]:
    service.pop("cost_estimate_monthly_usd", None)
    service.pop("cost_estimated_at", None)
# The worker's canonical non-price digest has no serialized payload contract.
# Do not pretend a guessed serialization independently reproduces that receipt.
# The actual worker checked the protected prepublication tree; validate current
# revision, lock and exact price/timestamp writeback explicitly here.
lock = next(x for x in manifest["services"] if x["id"] == "storage-blob-replication")
assert lock["size"] == "LRS" and lock["source"] == "user-pin" and lock["source_step"] == "1"
assert {x["id"]: x["size"] for x in manifest["services"]} == {
    "storage-blob-replication": "LRS", "app-host": "B1",
    "document-store": "Serverless", "access-compute": "Standard_D2as_v5"
}
assert digest(PROJECT / "01-requirements.md") == "180a57f22a2a676c02846a0fcdccd008cb580a9e4805b076ec31a5438e1cca99"
assert digest(ROOT / request["original_request_path"]) == request["original_request_sha256"]
print(json.dumps({
    "status": "PASS_COMPLETE_CURRENT69_SCENARIO",
    "output_path": str(result_path.relative_to(ROOT)),
    "output_sha256": digest(result_path),
    "verified_lines": 17, "verified_native_archives": native_count,
    "verified_direct_envelopes": direct_count, "material_records": 69,
    "prior_consumed": 34, "new_mcp": 0, "new_direct": 1,
    "cumulative": 35, "absolute_limit": 35, "remaining": 0,
    "monthly_total": result["monthly_total"], "yearly_total": result["yearly_total"],
    "manifest_pins_revision_and_writeback": "PASS",
    "prepublication_tree_preservation": "Actual pricing-owner receipt; not independently reproduced from an unspecified canonical serialization"
}, indent=2))
