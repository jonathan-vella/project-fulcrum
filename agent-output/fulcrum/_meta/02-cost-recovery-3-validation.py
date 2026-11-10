"""Read-only validation of actual worker pricing, not a pricing implementation."""

import datetime as dt
import hashlib
import json
import pathlib
from decimal import Decimal as D, ROUND_HALF_UP

ROOT = pathlib.Path("/workspaces/project-fulcrum")
PROJECT = ROOT / "agent-output/fulcrum"
OUT = PROJECT / "contracts/02-cost-estimate.recovery-3.json"
EVIDENCE = pathlib.Path(str(OUT) + ".retail-evidence")
NOW = dt.datetime.now(dt.timezone.utc)


def load(path):
    return json.loads(pathlib.Path(path).read_text())


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def fresh(value):
    stamp = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    assert dt.timedelta(0) <= NOW - stamp <= dt.timedelta(days=30), value


def strip_notes(value):
    if isinstance(value, dict):
        return {k: strip_notes(v) for k, v in value.items() if k != "notes"}
    if isinstance(value, list):
        return [strip_notes(v) for v in value]
    return value


def native_rows(value):
    if isinstance(value, str):
        value = json.loads(value)
    if "results" in value:
        return value["results"]["prices"]
    return value["Items"]


request = load(PROJECT / "_meta/02-cost-recovery-3-request.json")
original = load(ROOT / request["original_request_path"])
result = load(OUT)
fixed = load(EVIDENCE / "fixed-scope-calculations.json")
quote = load(EVIDENCE / "indicative-app-transfer-unit-quote.json")
archive = load(PROJECT / "_meta/02-cost-recovery-3-archive-receipt.json")

for key in ("manifest_path", "manifest_usage", "supplemental_resources",
            "currency", "region", "compare_regions", "include_ri_savings",
            "manifest_writeback"):
    assert strip_notes(request[key]) == strip_notes(original[key]), key
for path, expected in request["protected_hashes"].items():
    assert digest(PROJECT / path) == expected, path
assert digest(ROOT / request["original_request_path"]) == request["original_request_sha256"]
assert result["status"] == "FAILED"
assert result["monthly_total"] is None and result["yearly_total"] is None
assert result["manifest_writeback"] == []
assert len(result["resources"]) == 17
assert sum(x["monthly_cost"] is None for x in result["resources"]) == 1
assert not (PROJECT / "contracts/02-cost-estimate.json").exists()
fresh(result["queried_at"])

mcp = [x for x in result["query_ledger"] if x.get("command") == "pricing_get"]
direct = [x for x in result["query_ledger"] if str(x.get("id", "")).startswith("d0")]
assert len(mcp) == result["mcp_calls_used"] == 14
assert len(direct) == result["direct_api_calls_used"] == 6
assert 14 + result["mcp_calls_used"] + result["direct_api_calls_used"] == 34
assert len({json.dumps(x["parameters"], sort_keys=True) for x in mcp}) == len(mcp)
rows_by_file = {}
for entry in mcp:
    path = ROOT / entry["response_path"]
    if entry["id"] == "q11":
        path = ROOT / archive["archive_path"]
    assert digest(path) == entry["sha256"], entry["id"]
    response = load(path)
    assert response["status"] == entry["status"] == 200
    rows_by_file[path.name] = native_rows(response)
    assert len(rows_by_file[path.name]) == entry["rows"]
    fresh(entry["recorded_at"])

assert digest(ROOT / archive["archive_path"]) == archive["sha256"]
assert (ROOT / archive["archive_path"]).stat().st_size == archive["bytes"]
assert len(rows_by_file["q11-alert-discovery.native.txt"]) == archive["expected_rows"]

direct_page_requests = 0
for entry in direct:
    path = ROOT / entry["evidence_path"]
    assert digest(path) == entry["sha256"], entry["id"]
    evidence = load(path)
    assert evidence["query"]["priceType"] == "Consumption"
    assert evidence["query"]["currencyCode"] == "USD"
    assert evidence["mcp_failure"]["kind"] == "missing_tier_metadata"
    fresh(evidence["mcp_failure"]["recorded_at"])
    rows = []
    for page in evidence["pages"]:
        raw = page["raw_response"]
        assert hashlib.sha256(raw.encode()).hexdigest() == page["response_sha256"]
        body = json.loads(raw)
        assert not body["NextPageLink"]
        assert body["Count"] == len(body["Items"])
        rows.extend(body["Items"])
        fresh(page["queried_at"])
    assert evidence["requests_used"] == entry["requests_used"] == len(evidence["pages"])
    direct_page_requests += evidence["requests_used"]
    rows_by_file[path.name] = rows
assert direct_page_requests == 6

for entry in result["query_ledger"]:
    if entry.get("issued_now") is False and entry.get("source_status") == "COMPLETE":
        assert digest(ROOT / entry["evidence_path"]) == entry["sha256"]
        fresh(entry["queried_at"])
for record in load(EVIDENCE / "recovery-validation.json")["official_semantic_archives"]:
    assert digest(ROOT / record["path"]) == record["sha256"]

bandwidth_path = ROOT / quote["source_evidence_path"]
assert digest(bandwidth_path) == quote["source_evidence_sha256"]
assert digest(ROOT / quote["prior_native_evidence_path"]) == quote["prior_native_evidence_sha256"]
fresh(quote["queried_at"])
actual = sorted(rows_by_file[bandwidth_path.name], key=lambda x: x["tierMinimumUnits"])
assert len(actual) == len(quote["bands"]) == 6
for i, (row, band) in enumerate(zip(actual, quote["bands"])):
    for key in ("tierMinimumUnits", "retailPrice", "unitOfMeasure"):
        assert row[key] == band[key], key
    for key, value in quote["selection"].items():
        assert row[key] == value, key
    expected_upper = actual[i + 1]["tierMinimumUnits"] if i + 1 < len(actual) else None
    assert band["upper_exclusive_native_gb"] == expected_upper
    if "illustrative_marginal_usd_per_TB" in band:
        assert D(str(row["retailPrice"])) * 1000 == D(str(band["illustrative_marginal_usd_per_TB"]))
assert quote["coverage"]["monthly_app_wire_volume"] == "UNKNOWN"
assert quote["coverage"]["accepted_numeric_app_volume"] is False
assert quote["coverage"]["suggested_5_gb_adopted"] is False

published = {x["name"]: D(str(x["monthly_cost"])) for x in result["resources"]
             if x["monthly_cost"] is not None}
assert len(published) == len(fixed["lines"]) == 16
for line in fixed["lines"]:
    assert published[line["name"]] == D(str(line["monthly_component_cost_usd"]))
assert sum(published.values()) == D(str(fixed["fixed_scope_only_subtotal_usd"]))

# Verify the worker's component arithmetic from its actually sourced rates.
# No values from this validator are written to pricing or approval contracts.
def price(filename, meter, tier=None):
    rows = [r for r in rows_by_file[filename] if r["meterName"] == meter]
    if tier is not None:
        rows = [r for r in rows if r.get("tierMinimumUnits") == tier]
    assert len(rows) == 1, (filename, meter, tier, len(rows))
    return D(str(rows[0]["retailPrice"]))


def rounded(value):
    return value.quantize(D("0.000001"), rounding=ROUND_HALF_UP)


def candidate_rate(filename, query_key, query_value, meter_id):
    candidate = load(PROJECT / "contracts" / filename)
    assert candidate["status"] == "COMPLETE"
    queries = [q for q in candidate["query_ledger"] if q.get(query_key) == query_value]
    assert len(queries) == 1
    records = [r for r in native_rows(queries[0]["response"]) if r["meterId"] == meter_id]
    assert len(records) == 1, (filename, meter_id)
    record = records[0]
    assert record["currencyCode"] == "USD"
    assert record["priceType"] == "Consumption"
    return D(str(record["retailPrice"]))


cosmos_file = "02-cost-candidates-document-store.json"
cosmos_ru = candidate_rate(cosmos_file, "sequence", 2, "7f356bc7-f8a6-5cb2-a7c2-4cf785e6c596")
cosmos_storage = candidate_rate(cosmos_file, "sequence", 2, "feba2784-d0c5-55e9-8543-c57af5affe64")
cosmos_backup = candidate_rate(cosmos_file, "sequence", 2, "04c6d453-bc0e-5ad3-880a-19b8bb45a275")
cosmos_restore = candidate_rate(cosmos_file, "sequence", 2, "2f880206-a729-597a-9c13-8423a683475e")
reused_equations = {
    "app-host (dev, swedencentral)":
        730 * candidate_rate("02-cost-candidates-app-host.json", "id", "q3",
                             "87a319c7-c1cc-56a0-a6c2-a043cd34225d"),
    "document-store (dev, swedencentral)":
        20 * cosmos_ru + 10 * cosmos_storage + 10 * cosmos_backup + 10 * cosmos_restore,
    "access-compute (dev, swedencentral)":
        80 * candidate_rate("02-cost-candidates-access-compute.json", "query_id", "q1",
                            "0ef9fe9f-7a45-596d-905c-dc15a89559ad"),
    "temporary-cosmos-restore-target-dev":
        cosmos_ru + 10 * cosmos_storage + 10 * cosmos_backup,
}
for name, value in reused_equations.items():
    assert rounded(value) == published[name], (name, value, published[name])


equations = {
    "storage-blob-replication (dev, swedencentral)":
        D("30.5") * price("d06-blob.json", "Hot LRS Data Stored", 0)
        + 11 * price("q12-gpv2.native.json", "Hot Read Operations")
        + 2 * price("q12-gpv2.native.json", "Hot LRS Write Operations")
        + price("q12-gpv2.native.json", "LRS List and Create Container Operations")
        + 500 * price("q14-pitr.native.json", "Point-in-time Restore LRS Data Processed"),
    "acr-premium-dev-swedencentral":
        price("q01-acr.native.json", "Premium Registry Unit") * 365 / 12,
    "steady-private-endpoints-dev-swedencentral":
        4 * 730 * price("d02-private-link.json", "Standard Private Endpoint", 0)
        + 40 * price("d02-private-link.json", "Standard Data Processed - Ingress", 0)
        + 130 * price("d02-private-link.json", "Standard Data Processed - Egress", 0),
    "central-private-dns-allocation-dev":
        4 * price("d03-dns.json", "Private Zone", 0)
        + price("d03-dns.json", "Private Queries", 0),
    "log-analytics-app-insights-combined-dev":
        price("d04-logs.json", "Analytics Logs Data Ingestion", 5),
    "operational-metric-alerts-dev":
        4 * price("d05-metric.json", "Alerts Metric Monitored", 10),
    "operational-scheduled-log-alert-dev":
        price("q13-global-alerts.native.json", "Alerts System Log Monitored at 5 Minute Frequency"),
    "ephemeral-bastion-standard-dev":
        80 * price("q06-bastion.native.json", "Standard Gateway"),
    "ephemeral-nat-standard-dev":
        80 * price("q07-nat.native.json", "Standard Gateway")
        + 25 * price("q07-nat.native.json", "Standard Data Processed"),
    "ephemeral-runner-os-disk-dev":
        price("q08-disk.native.json", "P6 LRS Disk") * 80 / 730,
    "ephemeral-service-public-ipv4-dev":
        2 * 80 * price("q09-ip.native.json", "Standard IPv4 Static Public IP"),
    "temporary-cosmos-restore-private-endpoint-dev":
        4 * price("d02-private-link.json", "Standard Private Endpoint", 0)
        + price("d02-private-link.json", "Standard Data Processed - Ingress", 0)
        + 10 * price("d02-private-link.json", "Standard Data Processed - Egress", 0),
}
for name, value in equations.items():
    assert rounded(value) == published[name], (name, value, published[name])

print(json.dumps({
    "checked_at": NOW.isoformat(),
    "status": "PASS_DIAGNOSTIC_AND_INDICATIVE_EVIDENCE",
    "output_sha256": digest(OUT),
    "request_sha256": digest(PROJECT / "_meta/02-cost-recovery-3-request.json"),
    "fixed_evidence_sha256": digest(EVIDENCE / "fixed-scope-calculations.json"),
    "unit_quote_sha256": digest(EVIDENCE / "indicative-app-transfer-unit-quote.json"),
    "resolved_lines": 16, "unresolved_lines": 1, "full_scope_status": "FAILED",
    "verified_new_native_archives": len(mcp),
    "verified_direct_envelopes": len(direct),
    "verified_direct_raw_pages": direct_page_requests,
    "verified_component_equations_from_new_raw_sources": len(equations),
    "reused_candidate_components": len(reused_equations),
    "prior_requests": 14, "new_requests": 20, "cumulative_requests": 34,
    "absolute_limit": 34, "remaining": 0,
    "archival_persistence": "RECOVERED_BY_MAIN_WITHOUT_WORKER_EDITS",
    "monthly_total": None, "yearly_total": None, "manifest_writeback": [],
    "gate2_ready": False
}, indent=2))
