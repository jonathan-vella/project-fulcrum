"""Owned Step 3 checks, never state-file access or upstream edits."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET

from PIL import Image, ImageChops

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
META = PROJECT / "_meta"
SNAPSHOT = META / "03-des-protected-snapshot.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def protected():
    result = {}
    for path in PROJECT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(PROJECT).as_posix()
        # Never inspect session state or its locks/backups. CLI is its sole owner.
        if "session-state" in rel or path.suffix in {".lock", ".pyc"}:
            continue
        if rel in {"README.md", "00-handoff.md"} or path.name.startswith("03-des-"):
            # Existing Architect cost/comparison/chart assets remain protected.
            if not any(path.name.startswith(p) for p in
                       ("03-des-cost-", "03-des-sku-")):
                continue
        result[rel] = sha(path)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", action="store_true")
    args = parser.parse_args()
    if args.snapshot:
        assert not SNAPSHOT.exists(), "Never replace an existing baseline"
        baseline = {"files": protected(), "git_index_sha256": sha(ROOT / ".git/index")}
        SNAPSHOT.write_text(json.dumps(baseline, indent=2) + "\n")
        print("Protected baseline captured:", len(baseline["files"]), "files")
        return
    before = json.loads(SNAPSHOT.read_text())
    for rel, digest in before["files"].items():
        assert sha(PROJECT / rel) == digest, f"Protected bytes changed: {rel}"
    assert sha(ROOT / ".git/index") == before["git_index_sha256"], "Git index changed"
    recall = json.loads(subprocess.run(
        ["apex-recall", "show", "fulcrum", "--json"], capture_output=True,
        text=True, check=True).stdout)["session"]
    projection = json.loads((META / "assessment-step-2.json").read_text())
    assert len(projection["inputs"]) == 69
    assert projection["inputs"] == recall["decisions"]["material_inputs"]
    design_projection = json.loads((META / "assessment-step-3.json").read_text())
    assert design_projection["inputs"] == projection["inputs"]
    assert design_projection["scope"]["request_id"] == "fulcrum-optional-design-selection-20261109"
    assert design_projection["scope"]["environments"] == ["dev"]
    assert recall["decisions"]["design_scope"] == "both"
    assert recall["decisions"]["diagram_tool"] == "python"
    assert recall["decisions"]["review_depth"] == "default"
    assert recall["steps"]["1"]["status"] == "complete"
    assert recall["steps"]["2"]["status"] == "complete"
    manifest = json.loads((PROJECT / "contracts/sku-manifest.json").read_text())
    sizes = {s["id"]: s["size"] for s in manifest["services"]}
    assert sizes == {"app-host": "B1", "document-store": "Serverless",
                     "access-compute": "Standard_D2as_v5",
                     "storage-blob-replication": "LRS"}
    code = PROJECT / "assets/03-des-diagram.py"
    compile(code.read_text(), str(code), "exec")
    previous_renders = {p.name: sha(p) for p in (PROJECT / "assets").glob("03-des-diagram*.png")}
    previous_renders.update({p.name: sha(p) for p in (PROJECT / "assets").glob("03-des-diagram*.svg")})
    run = subprocess.run(["python3", str(code)], capture_output=True, text=True, check=True)
    print(run.stdout.strip())
    assert "WARN overflow:" not in run.stdout + run.stderr
    assert previous_renders and all(sha(PROJECT / "assets" / name) == digest
                                    for name, digest in previous_renders.items())
    ns = {"s": "http://www.w3.org/2000/svg"}
    renders = []
    import cairosvg
    for stem in ("03-des-diagram", "03-des-diagram-network"):
        svg = PROJECT / f"assets/{stem}.svg"
        png = PROJECT / f"assets/{stem}.png"
        xml = ET.fromstring(svg.read_text())
        assert xml.attrib["viewBox"] == "0 0 1920 1080"
        ids = {e.attrib["id"] for e in xml.iter() if "id" in e.attrib}
        assert xml.findall(".//s:symbol", ns), "Icons must be embedded symbols"
        for e in xml.iter():
            for key, value in e.attrib.items():
                if key.endswith("href"):
                    assert value.startswith("#") or value.startswith("data:"), value
                    if value.startswith("#"):
                        assert value[1:] in ids, value
        with Image.open(png) as image:
            assert image.size == (3840, 2160)
            assert ImageChops.difference(image.convert("RGB"), Image.new("RGB", image.size, "white")).getbbox()
            image.resize((1920, 1080)).save(META / f"{stem}-png-preview.png")
        # Actual SVG re-render, not a header/file-size proxy; inspect these previews.
        cairosvg.svg2png(url=str(svg), write_to=str(META / f"{stem}-svg-preview.png"),
                        output_width=1920, output_height=1080)
        renders.append({"stem": stem, "png_dimensions": [3840, 2160],
                        "svg_embedded_symbols": len(xml.findall(".//s:symbol", ns)),
                        "svg_rasterized_for_visual_inspection": True,
                        "svg_sha256": sha(svg), "png_sha256": sha(png)})
    adrs = sorted(PROJECT.glob("03-des-adr-*.md"))
    assert len(adrs) == 7
    for number, adr in enumerate(adrs, 1):
        body = adr.read_text()
        assert adr.name.startswith(f"03-des-adr-{number:04d}-")
        assert "> Generated by design agent | 2026-11-09" in body
        for term in ("Context", "Decision", "Alternatives", "Consequences",
                     "WAF Pillar Analysis", "Compliance Considerations",
                     "Implementation Notes", "Security", "Reliability",
                     "Performance", "Cost", "Operations"):
            assert term in body, (adr.name, term)
        assert "02-architecture-assessment.md#" in body
        # Confirm the direct architecture quote exists verbatim in its frozen source.
        quote = body.split("## Context", 1)[1].split("> ", 1)[1].split("\n", 1)[0]
        assert quote in (PROJECT / "02-architecture-assessment.md").read_text(), (adr.name, quote)
    # Focused local link existence for owned Markdown, not artifact Markdown lint.
    owned = adrs + [PROJECT / "README.md", PROJECT / "00-handoff.md",
                    PROJECT / "03-des-design-traceability.md"]
    links = 0
    for path in owned:
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
            if target.startswith(("https://", "http://", "#")):
                continue
            target = target.split("#")[0]
            resolved = path.parent / target
            # This receipt is produced below on the first successful run.
            assert resolved == META / "03-des-validation.json" or resolved.exists(), (path.name, target)
            links += 1
    visual = json.loads((META / "03-des-visual-checks.json").read_text())
    assert visual["status"] == "PASS" and visual["independent_review"] is False
    for render in renders:
        inspected = next(v for v in visual["views"] if v["stem"] == render["stem"])
        assert inspected["svg_sha256"] == render["svg_sha256"]
        assert inspected["png_sha256"] == render["png_sha256"]
        assert (PROJECT / inspected["png_inspected"]).exists()
        assert (PROJECT / inspected["svg_render_inspected"]).exists()
    receipt = {"status": "MECHANICAL_CHECKS_PASS", "protected_files_unchanged": len(before["files"]),
               "git_index_unchanged": True, "python_compile": "PASS", "overflow_warnings": 0,
               "deterministic_rerender": "PASS", "current_material_input_equality": "69/69",
               "manifest_choices_unchanged": True, "adr_source_quotes": "7/7 verbatim",
               "step3_status": recall["steps"]["3"]["status"],
               "step3_completed": recall["steps"]["3"]["completed"],
               "step3_scope_binding": "Actual Design selection / same 69 inputs / DEV only",
               "renders": renders, "adrs": [p.name for p in adrs],
               "owned_local_links_checked": links,
               "independent_adr_review": "NOT_REQUESTED",
               "visual_inspection": "PASS: directly inspected PNG and actual rasterized SVG for both hash-bound views; not independent runtime verification"}
    (META / "03-des-validation.json").write_text(json.dumps(receipt, indent=2) + "\n")
    assert json.loads((META / "03-des-validation.json").read_text()) == receipt
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
